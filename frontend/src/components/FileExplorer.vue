<template>
  <div
    class="file-explorer h-full bg-[#0a0a0a] text-gray-300 text-sm overflow-auto flex flex-col">
    <!-- Header with actions -->
    <div
      class="flex items-center justify-between px-3 py-2.5 border-b border-white/5">
      <span class="text-xs font-medium text-white/50 uppercase tracking-wider">
        Explorer
      </span>
      <div v-if="!readOnly" class="flex items-center gap-0.5">
        <button
          @click="showNewFileInput = true"
          class="p-1.5 hover:bg-white/5 rounded-md text-white/40 hover:text-white/70 transition-colors"
          title="New File">
          <svg
            class="w-3.5 h-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </button>
        <button
          @click="showNewFolderInput = true"
          class="p-1.5 hover:bg-white/5 rounded-md text-white/40 hover:text-white/70 transition-colors"
          title="New Folder">
          <svg
            class="w-3.5 h-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          </svg>
        </button>
        <button
          @click="fetchFileTree"
          class="p-1.5 hover:bg-white/5 rounded-md text-white/40 hover:text-white/70 transition-colors"
          title="Refresh">
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
        v-else
        @click="fetchFileTree"
        class="p-1.5 hover:bg-white/5 rounded-md text-white/40 hover:text-white/70 transition-colors"
        title="Refresh">
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

    <!-- New file/folder input at root level -->
    <div
      v-if="!readOnly && (showNewFileInput || showNewFolderInput)"
      class="px-2 py-1.5 border-b border-white/5">
      <input
        ref="newItemInput"
        v-model="newItemName"
        @keyup.enter="createNewItem"
        @keyup.escape="cancelNewItem"
        @blur="cancelNewItem"
        class="w-full bg-white/5 border border-white/10 focus:border-white/20 text-white text-xs px-2.5 py-1.5 rounded-md outline-none placeholder-white/30 transition-colors"
        :placeholder="showNewFileInput ? 'filename.js' : 'folder name'"
        autofocus />
    </div>

    <!-- Loading/Error states -->
    <div v-if="loading" class="p-3 text-white/30 text-xs">Loading...</div>
    <div v-else-if="error" class="p-3 text-red-400/80 text-xs">{{ error }}</div>

    <!-- File tree -->
    <div v-else class="py-1 flex-1 overflow-auto">
      <FileTreeNode
        v-for="node in tree"
        :key="node.id"
        :node="node"
        :depth="0"
        :selected-id="selectedId"
        :can-edit="!readOnly"
        :room-id="roomId"
        @select="handleSelect"
        @create="handleCreate"
        @rename="handleRename"
        @delete="handleDelete" />
      <div v-if="tree.length === 0" class="px-3 py-2 text-white/30 text-xs">
        No files yet.{{ readOnly ? "" : " Create one!" }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from "vue";
import FileTreeNode from "./FileTreeNode.vue";
import { apiUrl } from "@/lib/api";

const props = defineProps({
  roomId: {
    type: String,
    required: true,
  },
  readOnly: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["file-select", "file-change"]);

const tree = ref([]);
const loading = ref(true);
const error = ref(null);
const selectedId = ref(null);

// New item creation
const showNewFileInput = ref(false);
const showNewFolderInput = ref(false);
const newItemName = ref("");
const newItemInput = ref(null);

// Focus input when shown
watch([showNewFileInput, showNewFolderInput], () => {
  if (showNewFileInput.value || showNewFolderInput.value) {
    nextTick(() => newItemInput.value?.focus());
  }
});

async function fetchFileTree() {
  try {
    loading.value = true;
    error.value = null;
    const response = await fetch(
      apiUrl(`/api/files/?room_id=${props.roomId}`),
      {
        credentials: "include",
      }
    );
    if (!response.ok) throw new Error("Failed to fetch file tree");
    const data = await response.json();
    tree.value = data.tree;
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function handleSelect(node) {
  selectedId.value = node.id;

  if (node.type === "file") {
    try {
      const response = await fetch(
        apiUrl(`/api/files/content/?id=${node.id}`),
        { credentials: "include" }
      );
      if (!response.ok) throw new Error("Failed to fetch file content");
      const data = await response.json();
      emit("file-select", {
        id: node.id,
        path: data.path,
        name: data.name,
        content: data.content,
      });
    } catch (e) {
      console.error("Error loading file:", e);
    }
  }
}

async function createNewItem() {
  const name = newItemName.value.trim();
  if (!name) {
    cancelNewItem();
    return;
  }

  try {
    const response = await fetch(apiUrl("/api/files/create/"), {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        type: showNewFolderInput.value ? "folder" : "file",
        parentId: null,
        content: showNewFileInput.value ? "" : undefined,
        room_id: props.roomId,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || "Failed to create");
    }

    cancelNewItem();
    await fetchFileTree();
    emit("file-change");
  } catch (e) {
    console.error("Error creating item:", e);
    alert(e.message);
  }
}

function cancelNewItem() {
  showNewFileInput.value = false;
  showNewFolderInput.value = false;
  newItemName.value = "";
}

async function handleCreate({ parentId, name, type }) {
  try {
    const response = await fetch(apiUrl("/api/files/create/"), {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        type,
        parentId,
        content: type === "file" ? "" : undefined,
        room_id: props.roomId,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || "Failed to create");
    }

    await fetchFileTree();
    emit("file-change");
  } catch (e) {
    console.error("Error creating item:", e);
    alert(e.message);
  }
}

async function handleRename({ id, newName }) {
  try {
    const response = await fetch(apiUrl(`/api/files/${id}/rename/`), {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || "Failed to rename");
    }

    await fetchFileTree();
    emit("file-change");
  } catch (e) {
    console.error("Error renaming:", e);
    alert(e.message);
  }
}

async function handleDelete({ id }) {
  if (!confirm("Are you sure you want to delete this?")) return;

  try {
    const response = await fetch(apiUrl(`/api/files/${id}/delete/`), {
      method: "DELETE",
      credentials: "include",
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || "Failed to delete");
    }

    if (selectedId.value === id) {
      selectedId.value = null;
      emit("file-select", null);
    }

    await fetchFileTree();
    emit("file-change");
  } catch (e) {
    console.error("Error deleting:", e);
    alert(e.message);
  }
}

onMounted(() => {
  fetchFileTree();
});

// Expose refresh method for parent components
defineExpose({ refresh: fetchFileTree });
</script>

<style scoped>
.file-explorer {
  user-select: none;
}
</style>
