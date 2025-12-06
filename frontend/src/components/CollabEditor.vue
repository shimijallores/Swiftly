<template>
  <div class="flex flex-col h-screen w-screen">
    <div
      class="flex items-center gap-4 px-4 py-2 bg-[#1e1e1e] border-b border-gray-700 text-gray-400 text-xs font-sans">
      <span
        class="flex items-center gap-1"
        :class="isConnected ? 'text-green-500' : 'text-gray-400'">
        {{ isConnected ? "● Connected" : "○ Disconnected" }}
      </span>
      <span class="text-blue-400">{{ userName }}</span>
      <span v-if="typingCount > 0" class="text-orange-400 italic">
        {{ typingCount }} user{{ typingCount > 1 ? "s" : "" }} typing...
      </span>
      <div class="flex items-center gap-2 ml-auto">
        <span
          v-for="(cursor, id) in remoteCursors"
          :key="id"
          class="flex items-center gap-1 px-2 py-0.5 rounded text-white text-xs"
          :style="{ backgroundColor: cursor.color }">
          {{ cursor.name }}
        </span>
      </div>
    </div>
    <div ref="editorContainer" class="flex-1 overflow-hidden relative"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from "vue";
import * as monaco from "monaco-editor";
import * as Y from "yjs";
import { MonacoBinding } from "y-monaco";

const editorContainer = ref(null);
const isConnected = ref(false);
const typingCount = ref(0);

let editor = null;
let ydoc = null;
let ws = null;
let binding = null;
let typingTimeout = null;
let cursorUpdateTimeout = null;

// Generate a unique client ID and random user name
const clientId = Math.random().toString(36).substring(2, 15);
const userNames = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"];
const userName = userNames[Math.floor(Math.random() * userNames.length)] + Math.floor(Math.random() * 100);

// Generate a random color for this user
const userColors = ["#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3", "#00bcd4", "#009688", "#4caf50", "#ff9800", "#ff5722"];
const userColor = userColors[Math.floor(Math.random() * userColors.length)];

// Track remote users' typing states
const remoteTypingStates = new Map();

// Track remote cursors
const remoteCursors = reactive({});
const cursorDecorations = new Map(); // Map of clientId -> decoration IDs

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
        position: position ? { lineNumber: position.lineNumber, column: position.column } : null,
        selection: selection ? {
          startLineNumber: selection.startLineNumber,
          startColumn: selection.startColumn,
          endLineNumber: selection.endLineNumber,
          endColumn: selection.endColumn,
        } : null,
      })
    );
  }
}

function updateRemoteCursor(remoteClientId, cursorData) {
  if (!editor || !cursorData || remoteClientId === clientId) return;

  // Remove cursor if null (user disconnected)
  if (cursorData === null) {
    delete remoteCursors[remoteClientId];
    // Remove decorations
    const oldDecorations = cursorDecorations.get(remoteClientId) || [];
    editor.deltaDecorations(oldDecorations, []);
    cursorDecorations.delete(remoteClientId);
    // Remove cursor widget
    removeCursorWidget(remoteClientId);
    return;
  }

  // Update cursor state
  remoteCursors[remoteClientId] = cursorData;

  const { position, selection, color, name } = cursorData;
  if (!position) return;

  // Create decorations for cursor and selection
  const decorations = [];

  // Add selection decoration if there's a selection
  if (selection && (selection.startLineNumber !== selection.endLineNumber || selection.startColumn !== selection.endColumn)) {
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
      nameLabel.style.top = "-16px";
      nameLabel.style.left = "0";
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
  const ytext = ydoc.getText("monaco");

  // Connect to Django WebSocket
  connectWebSocket();

  // Initialize Monaco Editor
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
  });

  // Bind Yjs to Monaco (without awareness for now)
  binding = new MonacoBinding(ytext, editor.getModel(), new Set([editor]));

  // Listen for Yjs updates and broadcast them
  ydoc.on("update", (update, origin) => {
    if (origin !== "remote" && ws && ws.readyState === WebSocket.OPEN) {
      // Send update as base64 encoded string
      const base64 = btoa(String.fromCharCode(...update));
      ws.send(
        JSON.stringify({
          type: "yjs-update",
          data: base64,
        })
      );
    }
  });

  // Track typing activity
  editor.onDidChangeModelContent(() => {
    broadcastAwareness(true);

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
  ws = new WebSocket("ws://localhost:8000/ws/collab/");

  ws.onopen = () => {
    console.log("WebSocket connected");
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
        // Decode base64 and apply update
        const binary = atob(message.data);
        const update = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          update[i] = binary.charCodeAt(i);
        }
        Y.applyUpdate(ydoc, update, "remote");
      } else if (message.type === "yjs-state") {
        // Apply full state
        const binary = atob(message.data);
        const state = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          state[i] = binary.charCodeAt(i);
        }
        Y.applyUpdate(ydoc, state, "remote");
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
        // Update remote cursor
        const remoteClientId = message.clientId;
        if (remoteClientId && remoteClientId !== clientId) {
          updateRemoteCursor(remoteClientId, message.cursor);
        }
      } else if (message.type === "cursor-sync") {
        // Sync all cursor states
        const cursors = message.cursors || {};
        for (const [id, cursor] of Object.entries(cursors)) {
          if (id !== clientId) {
            updateRemoteCursor(id, cursor);
          }
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