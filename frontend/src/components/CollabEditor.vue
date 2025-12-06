<template>
  <div class="flex flex-col h-screen w-screen">
    <div
      class="flex items-center gap-4 px-4 py-2 bg-[#1e1e1e] border-b border-gray-700 text-gray-400 text-xs font-sans">
      <!-- Back button -->
      <button
        @click="emit('exit-room')"
        class="flex items-center gap-1 px-2 py-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
        title="Back to rooms">
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
      </button>
      <!-- Room name -->
      <span class="font-medium text-white">{{ room.name }}</span>
      <span
        class="px-1.5 py-0.5 text-[10px] uppercase tracking-wider rounded"
        :class="{
          'bg-white text-black': room.userRole === 'owner',
          'bg-gray-700 text-gray-200': room.userRole === 'editor',
          'bg-gray-800 text-gray-400': room.userRole === 'viewer',
        }">
        {{ room.userRole }}
      </span>
      <span class="text-gray-600">|</span>
      <span
        class="flex items-center gap-1"
        :class="isConnected ? 'text-green-500' : 'text-gray-400'">
        {{ isConnected ? "● Connected" : "○ Disconnected" }}
      </span>
      <span
        class="px-2 py-0.5 rounded text-white text-xs"
        :style="{ backgroundColor: userColor }">
        {{ userName }}
      </span>
      <span v-if="currentFile" class="text-gray-500">
        {{ currentFile.path }}
      </span>
      <span v-if="typingCount > 0" class="text-orange-400 italic">
        {{ typingCount }} user{{ typingCount > 1 ? "s" : "" }} typing...
      </span>
      <div class="flex items-center gap-2 ml-auto">
        <span
          v-for="(cursor, id) in remoteCursors"
          :key="id"
          class="flex items-center gap-1 px-2 py-0.5 rounded text-white text-xs"
          :style="{ backgroundColor: cursor.color }"
          :title="
            cursor.filePath ? `Editing: ${cursor.filePath}` : 'No file open'
          ">
          {{ cursor.name }}
          <span v-if="cursor.fileName" class="text-[10px] opacity-75">
            ({{ cursor.fileName }})
          </span>
        </span>
        <button
          @click="emit('logout')"
          class="px-2 py-1 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
          Logout
        </button>
      </div>
    </div>
    <div class="flex flex-1 overflow-hidden">
      <!-- File Explorer Sidebar -->
      <div class="w-64 shrink-0 border-r border-gray-700">
        <FileExplorer
          :room-id="room.id"
          :read-only="isViewer"
          @file-select="handleFileSelect" />
      </div>
      <!-- Editor -->
      <div ref="editorContainer" class="flex-1 overflow-hidden relative">
        <!-- Read-only overlay for viewers -->
        <div
          v-if="isViewer"
          class="absolute top-2 right-2 z-10 px-2 py-1 bg-gray-800 text-gray-400 text-xs rounded">
          Read-only mode
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from "vue";
import * as monaco from "monaco-editor";
import * as Y from "yjs";
import { MonacoBinding } from "y-monaco";
import { emmetHTML, emmetCSS, emmetJSX } from "emmet-monaco-es";
import FileExplorer from "./FileExplorer.vue";

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
  room: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["logout", "exit-room"]);

const editorContainer = ref(null);
const isConnected = ref(false);
const typingCount = ref(0);
const currentFile = ref(null);

// Use user data from props
const userName = props.user.collab_user?.name || props.user.username;
const userColor = props.user.collab_user?.color || "#2196f3";
const clientId = props.user.collab_user?.client_id || String(props.user.id);

// Role-based permissions
const isViewer = computed(() => props.room.userRole === "viewer");
const canEdit = computed(() => props.room.userRole !== "viewer");

let editor = null;
let ydoc = null;
let ws = null;
let binding = null;
let typingTimeout = null;
let cursorUpdateTimeout = null;
let saveTimeout = null;
let currentFileId = null; // Track current file for per-file sync

// Track remote users' typing states
const remoteTypingStates = new Map();

// Track remote cursors
const remoteCursors = reactive({});
const cursorDecorations = new Map(); // Map of clientId -> decoration IDs

// Get language from file extension
function getLanguageFromPath(path) {
  if (!path) return "plaintext";
  const ext = path.split(".").pop().toLowerCase();
  const langMap = {
    js: "javascript",
    ts: "typescript",
    vue: "html",
    py: "python",
    json: "json",
    md: "markdown",
    html: "html",
    css: "css",
    scss: "scss",
    xml: "xml",
    yaml: "yaml",
    yml: "yaml",
  };
  return langMap[ext] || "plaintext";
}

// Track pending file sync responses
let pendingFileSync = null;

// Handle file selection from explorer
function handleFileSelect(file) {
  if (!file) {
    currentFile.value = null;
    currentFileId = null;
    pendingFileSync = null;
    if (editor && binding) {
      binding.destroy();
      binding = null;
      editor.getModel()?.setValue("");
    }
    // Broadcast that we're not editing any file
    broadcastFileChange(null);
    return;
  }

  currentFile.value = file;
  currentFileId = file.id;

  if (editor) {
    // Destroy previous binding if exists
    if (binding) {
      binding.destroy();
      binding = null;
    }

    // Get or create a Yjs text for this specific file
    const ytext = ydoc.getText(`file-${file.id}`);

    // Set the editor language and clear content
    const model = editor.getModel();
    if (model) {
      monaco.editor.setModelLanguage(model, getLanguageFromPath(file.path));
      model.setValue(""); // Clear while loading
    }

    // If Yjs already has content for this file (from earlier in this session), use it
    if (ytext.length > 0) {
      binding = new MonacoBinding(ytext, editor.getModel(), new Set([editor]));
      pendingFileSync = null;
    } else {
      // Don't create binding yet - wait for server sync to complete
      // Mark that we're waiting for server sync
      pendingFileSync = {
        fileId: file.id,
        fileContent: file.content || "",
        ytext: ytext, // Store reference for later binding creation
      };

      // Request any stored Yjs updates for this file from the server
      // Server will respond with file-sync-complete when done
      requestFileSync(file.id);
    }
  }

  // Broadcast which file we're now editing
  broadcastFileChange(file.id);
}

// Request Yjs state for a specific file from the server
function requestFileSync(fileId) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: "file-sync-request",
        fileId: fileId,
      })
    );
  }
}

// Broadcast file change to other users
function broadcastFileChange(fileId) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: "file-change",
        clientId: clientId,
        fileId: fileId,
        fileName: currentFile.value?.name || null,
        filePath: currentFile.value?.path || null,
      })
    );
  }
}

// Save file content to server with debounce
function saveFileContent() {
  if (!currentFile.value || !editor) return;

  const content = editor.getValue();

  fetch(`http://localhost:8000/api/files/${currentFile.value.id}/`, {
    method: "PUT",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  })
    .then((res) => {
      if (res.ok) {
        console.log("File saved");
      }
    })
    .catch((err) => console.error("Save failed:", err));
}

// Debounced save (2 seconds)
function debouncedSave() {
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }
  saveTimeout = setTimeout(() => {
    saveFileContent();
  }, 2000);
}

function broadcastAwareness(isTyping) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: "awareness",
        clientId: clientId,
        state: { isTyping },
      })
    );
  }
}

function broadcastCursor() {
  if (ws && ws.readyState === WebSocket.OPEN && editor) {
    const position = editor.getPosition();
    const selection = editor.getSelection();
    ws.send(
      JSON.stringify({
        type: "cursor",
        clientId: clientId,
        name: userName,
        color: userColor,
        fileId: currentFileId,
        fileName: currentFile.value?.name || null,
        filePath: currentFile.value?.path || null,
        position: position
          ? { lineNumber: position.lineNumber, column: position.column }
          : null,
        selection: selection
          ? {
              startLineNumber: selection.startLineNumber,
              startColumn: selection.startColumn,
              endLineNumber: selection.endLineNumber,
              endColumn: selection.endColumn,
            }
          : null,
      })
    );
  }
}

function updateRemoteCursor(remoteClientId, cursorData) {
  if (!editor || remoteClientId === clientId) return;

  // Remove cursor if null (user disconnected)
  if (cursorData === null) {
    delete remoteCursors[remoteClientId];
    // Remove decorations
    const oldDecorations = cursorDecorations.get(remoteClientId) || [];
    editor.deltaDecorations(oldDecorations, []);
    cursorDecorations.delete(remoteClientId);
    // Remove cursor widget
    removeCursorWidget(remoteClientId);
    // Remove typing state
    remoteTypingStates.delete(remoteClientId);
    updateTypingCount();
    return;
  }

  if (!cursorData) return;

  // Update cursor state (always store for status bar display)
  remoteCursors[remoteClientId] = cursorData;

  const { position, selection, color, name, fileId } = cursorData;

  // Only show cursor decorations if user is on the same file
  const sameFile = fileId && fileId === currentFileId;

  if (!position || !sameFile) {
    // Remove decorations if not on same file
    const oldDecorations = cursorDecorations.get(remoteClientId) || [];
    editor.deltaDecorations(oldDecorations, []);
    cursorDecorations.delete(remoteClientId);
    removeCursorWidget(remoteClientId);
    return;
  }

  // Create decorations for cursor and selection
  const decorations = [];

  // Add selection decoration if there's a selection
  if (
    selection &&
    (selection.startLineNumber !== selection.endLineNumber ||
      selection.startColumn !== selection.endColumn)
  ) {
    decorations.push({
      range: new monaco.Range(
        selection.startLineNumber,
        selection.startColumn,
        selection.endLineNumber,
        selection.endColumn
      ),
      options: {
        className: `remote-selection-${remoteClientId}`,
        inlineClassName: `remote-selection-inline`,
      },
    });
  }

  // Update decorations
  const oldDecorations = cursorDecorations.get(remoteClientId) || [];
  const newDecorations = editor.deltaDecorations(oldDecorations, decorations);
  cursorDecorations.set(remoteClientId, newDecorations);

  // Update cursor widget (the line and name label)
  updateCursorWidget(remoteClientId, position, color, name);

  // Inject dynamic CSS for selection color
  injectSelectionStyle(remoteClientId, color);
}

// Map to store cursor widgets
const cursorWidgets = new Map();

function updateCursorWidget(remoteClientId, position, color, name) {
  // Remove existing widget if any
  removeCursorWidget(remoteClientId);

  // Create cursor widget
  const cursorWidget = {
    getId: () => `cursor-widget-${remoteClientId}`,
    getDomNode: () => {
      const container = document.createElement("div");
      container.className = "remote-cursor-widget";
      container.style.pointerEvents = "none";

      // Cursor line
      const cursorLine = document.createElement("div");
      cursorLine.className = "remote-cursor-line";
      cursorLine.style.backgroundColor = color;
      cursorLine.style.width = "2px";
      cursorLine.style.height = "18px";
      cursorLine.style.position = "absolute";
      cursorLine.style.top = "0";
      cursorLine.style.left = "0";

      // Name label
      const nameLabel = document.createElement("div");
      nameLabel.className = "remote-cursor-name";
      nameLabel.textContent = name;
      nameLabel.style.backgroundColor = color;
      nameLabel.style.color = "white";
      nameLabel.style.fontSize = "10px";
      nameLabel.style.padding = "1px 4px";
      nameLabel.style.borderRadius = "2px";
      nameLabel.style.position = "absolute";
      nameLabel.style.left = "8px";
      nameLabel.style.whiteSpace = "nowrap";
      nameLabel.style.zIndex = "100";

      container.appendChild(cursorLine);
      container.appendChild(nameLabel);
      return container;
    },
    getPosition: () => ({
      position: { lineNumber: position.lineNumber, column: position.column },
      preference: [monaco.editor.ContentWidgetPositionPreference.EXACT],
    }),
  };

  editor.addContentWidget(cursorWidget);
  cursorWidgets.set(remoteClientId, cursorWidget);
}

function removeCursorWidget(remoteClientId) {
  const widget = cursorWidgets.get(remoteClientId);
  if (widget) {
    editor.removeContentWidget(widget);
    cursorWidgets.delete(remoteClientId);
  }
}

function injectSelectionStyle(remoteClientId, color) {
  const styleId = `remote-selection-style-${remoteClientId}`;
  let styleEl = document.getElementById(styleId);
  if (!styleEl) {
    styleEl = document.createElement("style");
    styleEl.id = styleId;
    document.head.appendChild(styleEl);
  }
  // Convert hex to rgba with transparency
  const r = parseInt(color.slice(1, 3), 16);
  const g = parseInt(color.slice(3, 5), 16);
  const b = parseInt(color.slice(5, 7), 16);
  styleEl.textContent = `
    .remote-selection-${remoteClientId} {
      background-color: rgba(${r}, ${g}, ${b}, 0.3) !important;
    }
  `;
}

function updateTypingCount() {
  let count = 0;
  const now = Date.now();
  // Count users who are typing (and whose state hasn't expired)
  for (const [id, state] of remoteTypingStates.entries()) {
    if (state.isTyping && now - state.timestamp < 2000) {
      count++;
    }
  }
  typingCount.value = count;
}

onMounted(() => {
  // Initialize Yjs document
  ydoc = new Y.Doc();

  // Connect to Django WebSocket
  connectWebSocket();

  // Initialize Monaco Editor with enhanced features
  editor = monaco.editor.create(editorContainer.value, {
    value: "",
    language: "javascript",
    theme: "vs-dark",
    automaticLayout: true,
    minimap: { enabled: false },
    fontSize: 14,
    lineNumbers: "on",
    wordWrap: "on",
    scrollBeyondLastLine: false,
    readOnly: isViewer.value,
    // IntelliSense settings
    quickSuggestions: {
      other: true,
      comments: true,
      strings: true,
    },
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: "on",
    tabCompletion: "on",
    wordBasedSuggestions: "currentDocument",
    parameterHints: { enabled: true },
    formatOnType: true,
    formatOnPaste: true,
    // Bracket matching
    bracketPairColorization: { enabled: true },
    autoClosingBrackets: "always",
    autoClosingQuotes: "always",
    autoSurround: "languageDefined",
    // Code folding
    folding: true,
    foldingStrategy: "indentation",
    // Other enhancements
    linkedEditing: true,
    renderWhitespace: "selection",
    smoothScrolling: true,
  });

  // Enable Emmet for HTML, CSS, and JSX
  emmetHTML(monaco);
  emmetCSS(monaco);
  emmetJSX(monaco);

  // No initial binding - will be created when file is selected

  // Listen for Yjs updates and broadcast them
  ydoc.on("update", (update, origin) => {
    // Viewers don't send updates
    if (isViewer.value) return;

    if (
      origin !== "remote" &&
      ws &&
      ws.readyState === WebSocket.OPEN &&
      currentFileId
    ) {
      // Send update as base64 encoded string with file ID
      const base64 = btoa(String.fromCharCode(...update));
      ws.send(
        JSON.stringify({
          type: "yjs-update",
          fileId: currentFileId,
          data: base64,
        })
      );
    }
  });

  // Track typing activity and auto-save
  editor.onDidChangeModelContent(() => {
    broadcastAwareness(true);

    // Trigger debounced save
    debouncedSave();

    if (typingTimeout) {
      clearTimeout(typingTimeout);
    }

    typingTimeout = setTimeout(() => {
      broadcastAwareness(false);
    }, 1000);
  });

  // Track cursor position changes
  editor.onDidChangeCursorPosition(() => {
    // Debounce cursor updates
    if (cursorUpdateTimeout) {
      clearTimeout(cursorUpdateTimeout);
    }
    cursorUpdateTimeout = setTimeout(() => {
      broadcastCursor();
    }, 50);
  });

  // Track selection changes
  editor.onDidChangeCursorSelection(() => {
    if (cursorUpdateTimeout) {
      clearTimeout(cursorUpdateTimeout);
    }
    cursorUpdateTimeout = setTimeout(() => {
      broadcastCursor();
    }, 50);
  });

  // Periodically clean up stale typing states
  setInterval(updateTypingCount, 500);
});

function connectWebSocket() {
  // Connect to room-specific WebSocket
  const roomId = props.room.id;
  ws = new WebSocket(`ws://localhost:8000/ws/collab/${roomId}/`);

  ws.onopen = () => {
    console.log(`WebSocket connected to room ${roomId}`);
    isConnected.value = true;

    // Request sync from server
    ws.send(JSON.stringify({ type: "sync-request" }));
    // Request cursor states from server
    ws.send(JSON.stringify({ type: "cursor-sync-request" }));
    // Broadcast our cursor position
    setTimeout(broadcastCursor, 100);
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected");
    isConnected.value = false;

    // Attempt to reconnect after 2 seconds
    setTimeout(connectWebSocket, 2000);
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);

      if (message.type === "yjs-update") {
        // Only apply updates for the same file we're editing
        if (message.fileId && message.fileId === currentFileId) {
          // Decode base64 and apply update
          const binary = atob(message.data);
          const update = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) {
            update[i] = binary.charCodeAt(i);
          }
          Y.applyUpdate(ydoc, update, "remote");
        }
      } else if (message.type === "yjs-state") {
        // Apply stored state from server (only if for the same file)
        if (message.fileId && message.fileId === currentFileId) {
          const binary = atob(message.data);
          const state = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) {
            state[i] = binary.charCodeAt(i);
          }
          Y.applyUpdate(ydoc, state, "remote");
        }
      } else if (message.type === "awareness") {
        // Update typing indicator from remote user
        const remoteClientId = message.clientId;
        if (remoteClientId && remoteClientId !== clientId) {
          remoteTypingStates.set(remoteClientId, {
            isTyping: message.state?.isTyping || false,
            timestamp: Date.now(),
          });
          updateTypingCount();
        }
      } else if (message.type === "cursor") {
        // Update remote cursor with file info
        const remoteClientId = message.clientId;
        if (remoteClientId && remoteClientId !== clientId) {
          updateRemoteCursor(remoteClientId, {
            ...message.cursor,
            fileId: message.fileId,
            fileName: message.fileName,
            filePath: message.filePath,
          });
        }
      } else if (message.type === "cursor-sync") {
        // Sync all cursor states
        const cursors = message.cursors || {};
        for (const [id, cursor] of Object.entries(cursors)) {
          if (id !== clientId) {
            updateRemoteCursor(id, cursor);
          }
        }
      } else if (message.type === "file-change") {
        // Update remote user's file info
        const remoteClientId = message.clientId;
        if (remoteClientId && remoteClientId !== clientId) {
          // Update cursor info with new file
          if (remoteCursors[remoteClientId]) {
            remoteCursors[remoteClientId].fileId = message.fileId;
            remoteCursors[remoteClientId].fileName = message.fileName;
            remoteCursors[remoteClientId].filePath = message.filePath;
          }
        }
      } else if (message.type === "file-sync-complete") {
        // Server finished sending stored updates for the file
        const fileId = message.fileId;
        if (pendingFileSync && pendingFileSync.fileId === fileId) {
          const ytext = pendingFileSync.ytext || ydoc.getText(`file-${fileId}`);

          if (!message.hasUpdates) {
            // No updates on server - initialize with DB content
            if (ytext.length === 0 && pendingFileSync.fileContent) {
              ytext.insert(0, pendingFileSync.fileContent);
            }
          }

          // Now create the binding after sync is complete
          if (!binding && editor) {
            binding = new MonacoBinding(
              ytext,
              editor.getModel(),
              new Set([editor])
            );
          }

          pendingFileSync = null;
        }
      }
    } catch (e) {
      console.error("Error processing message:", e);
    }
  };
}

onUnmounted(() => {
  if (binding) binding.destroy();
  if (ws) ws.close();
  if (ydoc) ydoc.destroy();
  if (editor) editor.dispose();
  if (typingTimeout) clearTimeout(typingTimeout);
  if (cursorUpdateTimeout) clearTimeout(cursorUpdateTimeout);
  if (saveTimeout) clearTimeout(saveTimeout);
  // Clean up cursor widgets and styles
  for (const id of cursorWidgets.keys()) {
    removeCursorWidget(id);
    const styleEl = document.getElementById(`remote-selection-style-${id}`);
    if (styleEl) styleEl.remove();
  }
});
</script>

<style>
.remote-cursor-widget {
  position: relative;
  z-index: 100;
}
</style>
