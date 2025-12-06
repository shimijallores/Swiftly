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
          @click="downloadProject"
          :disabled="isDownloading"
          class="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors disabled:opacity-50"
          title="Download project as ZIP">
          <svg v-if="!isDownloading" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <svg v-else class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isDownloading ? 'Exporting...' : 'Export ZIP' }}
        </button>
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
          ref="fileExplorerRef"
          :room-id="room.id"
          :read-only="isViewer"
          @file-select="handleFileSelect" />
      </div>
      <!-- Editor -->
      <div
        ref="editorContainer"
        class="overflow-hidden relative"
        :class="showPreview ? 'w-1/2' : 'flex-1'">
        <!-- Read-only overlay for viewers -->
        <div
          v-if="isViewer"
          class="absolute top-2 right-2 z-10 px-2 py-1 bg-gray-800 text-gray-400 text-xs rounded">
          Read-only mode
        </div>
      </div>
      <!-- Live Preview Panel -->
      <div
        v-if="showPreview"
        class="w-1/2 flex flex-col border-l border-gray-700 bg-white">
        <!-- Preview Header -->
        <div
          class="flex items-center justify-between px-3 py-2 bg-[#1e1e1e] border-b border-gray-700">
          <div class="flex items-center gap-2">
            <span class="text-gray-400 text-xs">Live Preview</span>
            <button
              @click="refreshPreview"
              class="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
              title="Refresh Preview">
              <svg
                class="w-3.5 h-3.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          <button
            @click="showPreview = false"
            class="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Close Preview">
            <svg
              class="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <!-- Preview iframe -->
        <iframe
          ref="previewFrame"
          class="flex-1 w-full bg-white"
          sandbox="allow-scripts allow-same-origin"
          title="Live Preview">
        </iframe>
      </div>
      <!-- Preview Toggle Button (shows when preview is hidden and file is previewable) -->
      <button
        v-if="!showPreview && isPreviewable"
        @click="
          showPreview = true;
          updatePreview();
        "
        class="absolute right-4 bottom-4 flex items-center gap-2 px-3 py-2 bg-[#2d2d2d] text-gray-300 hover:bg-[#3d3d3d] rounded-lg shadow-lg border border-gray-600 z-20"
        title="Open Live Preview">
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <span class="text-xs">Preview</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from "vue";
import * as monaco from "monaco-editor";
import * as Y from "yjs";
import { MonacoBinding } from "y-monaco";
import { emmetHTML, emmetCSS, emmetJSX } from "emmet-monaco-es";
import JSZip from "jszip";
import { saveAs } from "file-saver";
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
const previewFrame = ref(null);
const fileExplorerRef = ref(null);
const isConnected = ref(false);
const typingCount = ref(0);
const currentFile = ref(null);
const showPreview = ref(false);
const isDownloading = ref(false);

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
let previewUpdateTimeout = null; // Debounce preview updates

// Check if current file is previewable (HTML)
const isPreviewable = computed(() => {
  if (!currentFile.value) return false;
  const ext = currentFile.value.path?.split(".").pop()?.toLowerCase();
  return ext === "html" || ext === "htm";
});

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

// Update live preview with current HTML content
async function updatePreview() {
  if (!showPreview.value || !previewFrame.value || !editor) return;

  const currentPath = currentFile.value?.path;
  if (!currentPath) return;

  const ext = currentPath.split(".").pop()?.toLowerCase();
  if (ext !== "html" && ext !== "htm") return;

  let htmlContent = editor.getValue();

  // Try to resolve linked CSS and JS files from the same project
  htmlContent = await resolveLinkedFiles(htmlContent);

  // Write to iframe
  const iframe = previewFrame.value;
  const doc = iframe.contentDocument || iframe.contentWindow?.document;
  if (doc) {
    doc.open();
    doc.write(htmlContent);
    doc.close();
  }
}

// Resolve linked CSS and JS files by fetching their content
async function resolveLinkedFiles(htmlContent) {
  // Get all files in the project for lookup
  const allFiles = await getAllProjectFiles();

  // Process <link> tags for CSS
  htmlContent = await processLinkTags(htmlContent, allFiles);

  // Process <script src="..."> tags for JS
  htmlContent = await processScriptTags(htmlContent, allFiles);

  return htmlContent;
}

// Get all files from the file explorer
async function getAllProjectFiles() {
  try {
    const response = await fetch(
      `http://localhost:8000/api/files/?room_id=${props.room.id}`,
      { credentials: "include" }
    );
    if (!response.ok) return [];
    const data = await response.json();

    // Flatten the tree to get all files
    const files = [];
    function flattenTree(nodes, parentPath = "") {
      for (const node of nodes) {
        const nodePath = parentPath ? `${parentPath}/${node.name}` : node.name;
        if (node.type === "file") {
          files.push({ ...node, fullPath: nodePath });
        }
        if (node.children) {
          flattenTree(node.children, nodePath);
        }
      }
    }
    flattenTree(data.tree || []);
    return files;
  } catch (e) {
    console.error("Error fetching project files:", e);
    return [];
  }
}

// Fetch file content by ID
async function fetchFileContent(fileId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/files/content/?id=${fileId}`,
      { credentials: "include" }
    );
    if (!response.ok) return null;
    const data = await response.json();
    return data.content;
  } catch (e) {
    console.error("Error fetching file content:", e);
    return null;
  }
}

// Find a file by its path/name in the project files
function findFileByPath(files, href) {
  // Remove leading ./ or /
  const cleanHref = href.replace(/^\.?\//, "");

  // Try exact match first
  let file = files.find(
    (f) => f.fullPath === cleanHref || f.name === cleanHref
  );

  // Try matching just the filename
  if (!file) {
    const fileName = cleanHref.split("/").pop();
    file = files.find((f) => f.name === fileName);
  }

  return file;
}

// Process <link> tags and inline CSS
async function processLinkTags(html, allFiles) {
  const linkRegex =
    /<link[^>]+rel=["']stylesheet["'][^>]+href=["']([^"']+)["'][^>]*>/gi;
  const linkRegex2 =
    /<link[^>]+href=["']([^"']+)["'][^>]+rel=["']stylesheet["'][^>]*>/gi;

  const matches = [...html.matchAll(linkRegex), ...html.matchAll(linkRegex2)];

  for (const match of matches) {
    const href = match[1];
    // Skip external URLs
    if (
      href.startsWith("http://") ||
      href.startsWith("https://") ||
      href.startsWith("//")
    ) {
      continue;
    }

    const file = findFileByPath(allFiles, href);
    if (file) {
      const content = await fetchFileContent(file.id);
      if (content) {
        // Replace link tag with inline style
        html = html.replace(
          match[0],
          `<style>/* ${href} */\n${content}\n</style>`
        );
      }
    }
  }

  return html;
}

// Process <script src="..."> tags and inline JS
async function processScriptTags(html, allFiles) {
  const scriptRegex = /<script[^>]+src=["']([^"']+)["'][^>]*><\/script>/gi;

  const matches = [...html.matchAll(scriptRegex)];

  for (const match of matches) {
    const src = match[1];
    // Skip external URLs
    if (
      src.startsWith("http://") ||
      src.startsWith("https://") ||
      src.startsWith("//")
    ) {
      continue;
    }

    const file = findFileByPath(allFiles, src);
    if (file) {
      const content = await fetchFileContent(file.id);
      if (content) {
        // Replace script tag with inline script
        const scriptOpen = "<scr" + "ipt>";
        const scriptClose = "</scr" + "ipt>";
        const replacement =
          scriptOpen +
          "/* " +
          src +
          " */" +
          String.fromCharCode(10) +
          content +
          String.fromCharCode(10) +
          scriptClose;
        html = html.replace(match[0], replacement);
      }
    }
  }

  return html;
}

// Debounced preview update
function debouncedPreviewUpdate() {
  if (previewUpdateTimeout) {
    clearTimeout(previewUpdateTimeout);
  }
  previewUpdateTimeout = setTimeout(() => {
    updatePreview();
  }, 500);
}

// Manual refresh preview
function refreshPreview() {
  updatePreview();
}

// Download project as ZIP file
async function downloadProject() {
  if (isDownloading.value) return;
  
  isDownloading.value = true;
  
  try {
    // Get all project files
    const allFiles = await getAllProjectFiles();
    
    if (allFiles.length === 0) {
      alert('No files to download');
      return;
    }
    
    // Create a new ZIP file
    const zip = new JSZip();
    
    // Fetch content for each file and add to ZIP
    for (const file of allFiles) {
      const content = await fetchFileContent(file.id);
      if (content !== null) {
        // Use the full path for proper folder structure
        zip.file(file.fullPath, content);
      }
    }
    
    // Generate the ZIP file
    const blob = await zip.generateAsync({ 
      type: 'blob',
      compression: 'DEFLATE',
      compressionOptions: { level: 6 }
    });
    
    // Create filename with room name and timestamp
    const timestamp = new Date().toISOString().slice(0, 10);
    const safeName = props.room.name.replace(/[^a-zA-Z0-9-_]/g, '_');
    const filename = safeName + '_' + timestamp + '.zip';
    
    // Download the file
    saveAs(blob, filename);
    
  } catch (error) {
    console.error('Error downloading project:', error);
    alert('Failed to download project: ' + error.message);
  } finally {
    isDownloading.value = false;
  }
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

    // Update live preview if showing
    if (showPreview.value && isPreviewable.value) {
      debouncedPreviewUpdate();
    }

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
  if (previewUpdateTimeout) clearTimeout(previewUpdateTimeout);
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
