<template>
  <div>
    <!-- Context Menu -->
    <ContextMenu
      :visible="contextMenuVisible"
      :position="contextMenuPosition"
      :items="contextMenuItems"
      @close="contextMenuVisible = false" />

    <!-- Rename input mode -->
    <div
      v-if="isRenaming"
      class="flex items-center gap-1 px-2 py-0.5"
      :style="{ paddingLeft: `${depth * 12 + 8}px` }">
      <span class="w-4 h-4"></span>
      <span class="w-4 h-4"></span>
      <input
        ref="renameInput"
        v-model="renameValue"
        @keyup.enter="submitRename"
        @keyup.escape="cancelRename"
        @blur="cancelRename"
        class="flex-1 bg-[#3c3c3c] border border-blue-500 text-white text-xs px-1 py-0.5 rounded outline-none" />
    </div>

    <!-- Normal display mode -->
    <div
      v-else
      class="group flex items-center gap-1 px-2 py-0.5 cursor-pointer hover:bg-[#2a2d2e] transition-colors"
      :class="{ 'bg-[#094771]': isSelected }"
      :style="{ paddingLeft: `${depth * 12 + 8}px` }"
      @click="handleClick"
      @contextmenu.prevent="showContextMenu">
      <!-- Folder/File Icon -->
      <span
        v-if="node.type === 'folder'"
        class="w-4 h-4 flex items-center justify-center">
        <svg
          v-if="isExpanded"
          class="w-3 h-3 text-gray-400"
          fill="currentColor"
          viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clip-rule="evenodd" />
        </svg>
        <svg
          v-else
          class="w-3 h-3 text-gray-400"
          fill="currentColor"
          viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
            clip-rule="evenodd" />
        </svg>
      </span>
      <span v-else class="w-4 h-4"></span>

      <!-- Icon/Label based on type -->
      <span
        v-if="node.type === 'folder'"
        class="w-4 h-4 flex items-center justify-center">
        <svg
          class="w-4 h-4"
          :class="isExpanded ? 'text-yellow-400' : 'text-yellow-500'"
          fill="currentColor"
          viewBox="0 0 20 20">
          <path
            d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
        </svg>
      </span>
      <span
        v-else
        class="text-[9px] font-bold tracking-tight w-6 text-center shrink-0"
        :class="fileTypeColor">
        {{ fileTypeLabel }}
      </span>

      <!-- Name -->
      <span class="truncate flex-1">{{ node.name }}</span>

      <!-- Action buttons (show on hover, only for editors) -->
      <div v-if="canEdit" class="hidden group-hover:flex items-center gap-0.5">
        <button
          v-if="node.type === 'folder'"
          @click.stop="startCreateFile"
          class="p-0.5 hover:bg-gray-600 rounded"
          title="New File">
          <svg
            class="w-3 h-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <button
          @click.stop="startRename"
          class="p-0.5 hover:bg-gray-600 rounded"
          title="Rename">
          <svg
            class="w-3 h-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          @click.stop="handleDelete"
          class="p-0.5 hover:bg-red-600 rounded"
          title="Delete">
          <svg
            class="w-3 h-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- New file/folder input inside folder -->
    <div
      v-if="isCreatingFile"
      class="flex items-center gap-1 px-2 py-0.5"
      :style="{ paddingLeft: `${(depth + 1) * 12 + 8}px` }">
      <span class="w-4 h-4"></span>
      <span class="w-4 h-4"></span>
      <input
        ref="createInput"
        v-model="createFileName"
        @keyup.enter="submitCreate"
        @keyup.escape="cancelCreate"
        @blur="cancelCreate"
        class="flex-1 bg-[#3c3c3c] border border-blue-500 text-white text-xs px-1 py-0.5 rounded outline-none"
        :placeholder="
          createItemType === 'folder' ? 'folder name' : 'filename.js'
        " />
    </div>

    <!-- Children (for folders) -->
    <div v-if="node.type === 'folder' && isExpanded && node.children">
      <FileTreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :depth="depth + 1"
        :selected-id="selectedId"
        :can-edit="canEdit"
        :room-id="roomId"
        @select="$emit('select', $event)"
        @create="$emit('create', $event)"
        @rename="$emit('rename', $event)"
        @delete="$emit('delete', $event)" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from "vue";
import ContextMenu from "./ContextMenu.vue";

const props = defineProps({
  node: {
    type: Object,
    required: true,
  },
  depth: {
    type: Number,
    default: 0,
  },
  selectedId: {
    type: String,
    default: null,
  },
  canEdit: {
    type: Boolean,
    default: true,
  },
  roomId: {
    type: [Number, String],
    default: null,
  },
});

const emit = defineEmits(["select", "create", "rename", "delete"]);

const isExpanded = ref(false);
const isRenaming = ref(false);
const renameValue = ref("");
const renameInput = ref(null);

const isCreatingFile = ref(false);
const createFileName = ref("");
const createInput = ref(null);

// Context menu state
const contextMenuVisible = ref(false);
const contextMenuPosition = ref({ x: 0, y: 0 });

const isSelected = computed(() => props.selectedId === props.node.id);

// File type label (uppercase extension)
const fileTypeLabel = computed(() => {
  if (props.node.type === "folder") return "";
  const ext = props.node.name.split(".").pop()?.toLowerCase() || "";
  const labels = {
    js: "JS",
    ts: "TS",
    vue: "VUE",
    jsx: "JSX",
    tsx: "TSX",
    py: "PY",
    json: "JSON",
    md: "MD",
    html: "HTML",
    htm: "HTML",
    css: "CSS",
    scss: "SCSS",
    sass: "SASS",
    less: "LESS",
    xml: "XML",
    yaml: "YML",
    yml: "YML",
    txt: "TXT",
    svg: "SVG",
    png: "IMG",
    jpg: "IMG",
    jpeg: "IMG",
    gif: "IMG",
    gitignore: "GIT",
    env: "ENV",
  };
  return labels[ext] || ext.toUpperCase().slice(0, 4) || "FILE";
});

// File type color
const fileTypeColor = computed(() => {
  if (props.node.type === "folder") return "";
  const ext = props.node.name.split(".").pop()?.toLowerCase() || "";
  const colors = {
    js: "text-yellow-400",
    ts: "text-blue-400",
    vue: "text-green-400",
    jsx: "text-cyan-400",
    tsx: "text-blue-400",
    py: "text-yellow-300",
    json: "text-yellow-300",
    md: "text-gray-400",
    html: "text-orange-400",
    htm: "text-orange-400",
    css: "text-blue-400",
    scss: "text-pink-400",
    sass: "text-pink-400",
    less: "text-blue-300",
  };
  return colors[ext] || "text-gray-500";
});

// Context menu items based on node type and permissions
const contextMenuItems = computed(() => {
  const items = [];

  // Only show edit options if user can edit
  if (props.canEdit) {
    if (props.node.type === "folder") {
      items.push({
        label: "New File",
        icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>',
        action: () => startCreateItem("file"),
      });
      items.push({
        label: "New Folder",
        icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>',
        action: () => startCreateItem("folder"),
      });
      items.push({ separator: true });
    }

    items.push({
      label: "Rename",
      icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>',
      shortcut: "F2",
      action: startRename,
    });

    items.push({ separator: true });

    items.push({
      label: "Delete",
      icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>',
      shortcut: "Del",
      action: handleDelete,
    });
  }

  return items;
});

function handleClick() {
  if (props.node.type === "folder") {
    isExpanded.value = !isExpanded.value;
  }
  emit("select", props.node);
}

function showContextMenu(e) {
  contextMenuPosition.value = { x: e.clientX, y: e.clientY };
  contextMenuVisible.value = true;
}

function startCreateItem(type) {
  isExpanded.value = true;
  isCreatingFile.value = true;
  createFileName.value = "";
  // Store the type we're creating
  createItemType.value = type;
  nextTick(() => createInput.value?.focus());
}

// Store what type of item we're creating
const createItemType = ref("file");

function startRename() {
  isRenaming.value = true;
  renameValue.value = props.node.name;
  nextTick(() => {
    renameInput.value?.focus();
    renameInput.value?.select();
  });
}

function submitRename() {
  const newName = renameValue.value.trim();
  if (newName && newName !== props.node.name) {
    emit("rename", { id: props.node.id, newName });
  }
  cancelRename();
}

function cancelRename() {
  isRenaming.value = false;
  renameValue.value = "";
}

function startCreateFile() {
  startCreateItem("file");
}

function submitCreate() {
  const name = createFileName.value.trim();
  if (name) {
    emit("create", {
      parentId: props.node.id,
      name,
      type: createItemType.value,
    });
  }
  cancelCreate();
}

function cancelCreate() {
  isCreatingFile.value = false;
  createFileName.value = "";
}

function handleDelete() {
  emit("delete", { id: props.node.id });
}
</script>
