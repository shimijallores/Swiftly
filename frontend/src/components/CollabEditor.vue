<template>
  <div class="flex flex-col h-screen w-screen">
    <div
      class="flex items-center gap-4 px-4 py-2 bg-[#1e1e1e] border-b border-gray-700 text-gray-400 text-xs font-sans">
      <span
        class="flex items-center gap-1"
        :class="isConnected ? 'text-green-500' : 'text-gray-400'">
        {{ isConnected ? "● Connected" : "○ Disconnected" }}
      </span>
      <span v-if="typingCount > 0" class="text-orange-400 italic">
        {{ typingCount }} user{{ typingCount > 1 ? "s" : "" }} typing...
      </span>
    </div>
    <div ref="editorContainer" class="flex-1 overflow-hidden"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
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

// Generate a unique client ID
const clientId = Math.random().toString(36).substring(2, 15);

// Track remote users' typing states
const remoteTypingStates = new Map();

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
});
</script>