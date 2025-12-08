<template>
  <div class="flex flex-col h-full bg-[#0a0a0a] text-gray-300">
    <!-- Header -->
    <div
      class="flex items-center justify-between px-4 py-3 border-b border-white/5">
      <div class="flex items-center gap-2">
        <svg
          class="w-4 h-4 text-white/40"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 class="text-sm font-medium text-white/90">Version history</h2>
      </div>
      <button
        @click="emit('close')"
        class="p-1.5 text-white/40 hover:text-white/70 hover:bg-white/5 rounded-md transition-colors"
        title="Close">
        <svg
          class="w-4 h-4"
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

    <!-- Current file info -->
    <div
      v-if="currentFile"
      class="px-4 py-2 border-b border-white/5 bg-white/2">
      <p class="text-xs text-white/40">{{ currentFile.path }}</p>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <svg
        class="w-5 h-5 animate-spin text-white/30"
        fill="none"
        viewBox="0 0 24 24">
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- No file selected -->
    <div
      v-else-if="!currentFile"
      class="flex flex-col items-center justify-center py-12 px-4 text-center">
      <svg
        class="w-10 h-10 text-white/10 mb-3"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-sm text-white/40">
        Select a file to view its version history
      </p>
    </div>

    <!-- No snapshots -->
    <div
      v-else-if="snapshots.length === 0"
      class="flex flex-col items-center justify-center py-12 px-4 text-center">
      <svg
        class="w-10 h-10 text-white/10 mb-3"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-white/40">No version history yet</p>
      <p class="text-xs text-white/20 mt-1">
        Versions are saved automatically as you edit
      </p>
    </div>

    <!-- Snapshots list -->
    <div v-else class="flex-1 overflow-y-auto">
      <!-- Group by date -->
      <div
        v-for="(group, date) in groupedSnapshots"
        :key="date"
        class="border-b border-white/5">
        <!-- Date header -->
        <div
          class="sticky top-0 px-4 py-2 bg-white/2 text-xs font-medium text-white/40 uppercase tracking-wider">
          {{ formatDateHeader(date) }}
        </div>

        <!-- Snapshots in this date group -->
        <div class="py-1">
          <button
            v-for="snapshot in group"
            :key="snapshot.id"
            @click="selectSnapshot(snapshot)"
            class="w-full px-4 py-3 text-left hover:bg-white/5 transition-colors"
            :class="{ 'bg-white/10': selectedSnapshot?.id === snapshot.id }">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <!-- Time -->
                <p class="text-sm text-white/90 font-medium">
                  {{ formatTime(snapshot.createdAt) }}
                </p>
                <!-- Author -->
                <p class="text-xs text-white/40 mt-0.5 flex items-center gap-1">
                  <svg
                    class="w-3 h-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {{ snapshot.authorName }}
                </p>
              </div>
              <!-- Size badge -->
              <span
                class="text-[10px] text-white/30 bg-white/5 px-1.5 py-0.5 rounded">
                {{ formatSize(snapshot.size) }}
              </span>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Preview panel (when snapshot selected) -->
    <div
      v-if="selectedSnapshot && previewContent !== null"
      class="border-t border-white/5">
      <div class="flex items-center justify-between px-4 py-2 bg-white/2">
        <span class="text-xs text-white/40">Preview</span>
        <div class="flex items-center gap-2">
          <button
            v-if="!isViewer"
            @click="restoreSnapshot"
            :disabled="isRestoring"
            class="flex items-center gap-1 px-2.5 py-1 text-xs bg-white/10 hover:bg-white/15 text-white/90 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            <svg
              v-if="!isRestoring"
              class="w-3 h-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg
              v-else
              class="w-3 h-3 animate-spin"
              fill="none"
              viewBox="0 0 24 24">
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            {{ isRestoring ? "Restoring..." : "Restore this version" }}
          </button>
          <button
            @click="
              selectedSnapshot = null;
              previewContent = null;
            "
            class="p-1 text-white/40 hover:text-white/70 hover:bg-white/5 rounded-md transition-colors"
            title="Close preview">
            <svg
              class="w-3 h-3"
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
      </div>
      <div class="max-h-48 overflow-auto bg-[#0a0a0a] border-t border-white/5">
        <pre
          class="p-3 text-xs text-white/60 font-mono whitespace-pre-wrap break-all"
          >{{ previewContent }}</pre
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { apiUrl } from "@/utils/api";

const props = defineProps({
  currentFile: {
    type: Object,
    default: null,
  },
  isViewer: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "restore"]);

const snapshots = ref([]);
const isLoading = ref(false);
const selectedSnapshot = ref(null);
const previewContent = ref(null);
const isRestoring = ref(false);

// Group snapshots by date
const groupedSnapshots = computed(() => {
  const groups = {};
  for (const snapshot of snapshots.value) {
    const date = new Date(snapshot.createdAt).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(snapshot);
  }
  return groups;
});

// Watch for file changes
watch(
  () => props.currentFile,
  (newFile) => {
    if (newFile) {
      loadSnapshots();
    } else {
      snapshots.value = [];
      selectedSnapshot.value = null;
      previewContent.value = null;
    }
  },
  { immediate: true }
);

async function loadSnapshots() {
  if (!props.currentFile) return;

  isLoading.value = true;
  try {
    const response = await fetch(
      apiUrl(`/api/files/${props.currentFile.id}/snapshots/`),
      { credentials: "include" }
    );
    if (response.ok) {
      const data = await response.json();
      snapshots.value = data.snapshots || [];
    }
  } catch (error) {
    console.error("Failed to load snapshots:", error);
  } finally {
    isLoading.value = false;
  }
}

async function selectSnapshot(snapshot) {
  selectedSnapshot.value = snapshot;
  previewContent.value = null;

  try {
    const response = await fetch(apiUrl(`/api/snapshots/${snapshot.id}/`), {
      credentials: "include",
    });
    if (response.ok) {
      const data = await response.json();
      previewContent.value = data.content;
    }
  } catch (error) {
    console.error("Failed to load snapshot content:", error);
  }
}

async function restoreSnapshot() {
  if (!selectedSnapshot.value || isRestoring.value) return;

  isRestoring.value = true;
  try {
    const response = await fetch(
      apiUrl(`/api/snapshots/${selectedSnapshot.value.id}/restore/`),
      {
        method: "POST",
        credentials: "include",
      }
    );

    if (response.ok) {
      const data = await response.json();
      emit("restore", {
        fileId: props.currentFile.id,
        content: previewContent.value,
      });
      // Reload snapshots to show the new restore snapshot
      await loadSnapshots();
      selectedSnapshot.value = null;
      previewContent.value = null;
    }
  } catch (error) {
    console.error("Failed to restore snapshot:", error);
  } finally {
    isRestoring.value = false;
  }
}

function formatDateHeader(dateStr) {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return "Today";
  } else if (date.toDateString() === yesterday.toDateString()) {
    return "Yesterday";
  } else {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: date.getFullYear() !== today.getFullYear() ? "numeric" : undefined,
    });
  }
}

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Expose refresh method for parent
defineExpose({
  refresh: loadSnapshots,
});
</script>
