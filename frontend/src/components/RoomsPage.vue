<script setup>
import { ref, onMounted } from "vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogContent,
  DialogFooter,
} from "@/components/ui/dialog";
import { apiUrl } from "@/utils/api";

const emit = defineEmits(["select-room"]);

// State
const rooms = ref([]);
const loading = ref(true);
const error = ref(null);

// Dialog states
const showCreateDialog = ref(false);
const showJoinDialog = ref(false);
const showMembersDialog = ref(false);
const selectedRoom = ref(null);

// Form states
const createForm = ref({ name: "", password: "" });
const joinForm = ref({ code: "", password: "" });
const formError = ref(null);
const formLoading = ref(false);

// Fetch rooms on mount
onMounted(() => {
  fetchRooms();
});

async function fetchRooms() {
  loading.value = true;
  error.value = null;
  try {
    const res = await fetch(apiUrl("/api/rooms/"), {
      credentials: "include",
    });
    if (!res.ok) throw new Error("Failed to fetch rooms");
    const data = await res.json();
    rooms.value = data.rooms;
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function createRoom() {
  formLoading.value = true;
  formError.value = null;
  try {
    const res = await fetch(apiUrl("/api/rooms/"), {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(createForm.value),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to create room");
    rooms.value.unshift(data);
    showCreateDialog.value = false;
    createForm.value = { name: "", password: "" };
  } catch (e) {
    formError.value = e.message;
  } finally {
    formLoading.value = false;
  }
}

async function joinRoom() {
  formLoading.value = true;
  formError.value = null;
  try {
    const res = await fetch(apiUrl("/api/rooms/join/"), {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(joinForm.value),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to join room");
    const existing = rooms.value.findIndex((r) => r.id === data.id);
    if (existing >= 0) {
      rooms.value[existing] = data;
    } else {
      rooms.value.unshift(data);
    }
    showJoinDialog.value = false;
    joinForm.value = { code: "", password: "" };
  } catch (e) {
    formError.value = e.message;
  } finally {
    formLoading.value = false;
  }
}

async function leaveRoom(room) {
  if (!confirm(`Leave "${room.name}"?`)) return;
  try {
    const res = await fetch(apiUrl(`/api/rooms/${room.id}/leave/`), {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Failed to leave room");
    }
    rooms.value = rooms.value.filter((r) => r.id !== room.id);
  } catch (e) {
    alert(e.message);
  }
}

async function deleteRoom(room) {
  if (!confirm(`Delete "${room.name}"? This cannot be undone.`)) return;
  try {
    const res = await fetch(apiUrl(`/api/rooms/${room.id}/`), {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Failed to delete room");
    }
    rooms.value = rooms.value.filter((r) => r.id !== room.id);
  } catch (e) {
    alert(e.message);
  }
}

function openMembersDialog(room) {
  selectedRoom.value = room;
  fetchRoomDetails(room.id);
  showMembersDialog.value = true;
}

async function fetchRoomDetails(roomId) {
  try {
    const res = await fetch(apiUrl(`/api/rooms/${roomId}/`), {
      credentials: "include",
    });
    if (!res.ok) throw new Error("Failed to fetch room details");
    const data = await res.json();
    selectedRoom.value = data;
  } catch (e) {
    console.error(e);
  }
}

async function changeRole(member, newRole) {
  try {
    const res = await fetch(
      apiUrl(`/api/rooms/${selectedRoom.value.id}/members/${member.id}/role/`),
      {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: newRole }),
      }
    );
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Failed to change role");
    }
    await fetchRoomDetails(selectedRoom.value.id);
  } catch (e) {
    alert(e.message);
  }
}

async function kickMember(member) {
  if (!confirm(`Remove ${member.username}?`)) return;
  try {
    const res = await fetch(
      apiUrl(`/api/rooms/${selectedRoom.value.id}/members/${member.id}/kick/`),
      { method: "DELETE", credentials: "include" }
    );
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Failed to remove member");
    }
    await fetchRoomDetails(selectedRoom.value.id);
  } catch (e) {
    alert(e.message);
  }
}

function selectRoom(room) {
  emit("select-room", room);
}

function copyCode(code) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(code);
  } else {
    // Fallback for non-secure contexts
    const textArea = document.createElement("textarea");
    textArea.value = code;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("copy");
    document.body.removeChild(textArea);
  }
}

const roleOptions = [
  { value: "editor", label: "Editor" },
  { value: "viewer", label: "Viewer" },
];
</script>

<template>
  <div class="pt-14 min-h-screen bg-[#0a0a0a]">
    <div class="max-w-4xl mx-auto px-6 py-10">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-semibold text-white tracking-tight">
            Your Rooms
          </h1>
          <p class="text-gray-500 text-sm mt-1">
            Create or join collaborative workspaces
          </p>
        </div>
        <div class="flex gap-2">
          <Button
            variant="outline"
            class="border-white/10 text-black hover:bg-neutral-400"
            @click="showJoinDialog = true">
            Join Room
          </Button>
          <Button
            class="bg-white text-black hover:bg-gray-200"
            @click="showCreateDialog = true">
            Create Room
          </Button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16 text-gray-500">
        Loading rooms...
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-16 text-red-400">
        {{ error }}
      </div>

      <!-- Empty state -->
      <div v-else-if="rooms.length === 0" class="text-center py-20">
        <div
          class="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mx-auto mb-4">
          <svg
            class="w-6 h-6 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <p class="text-gray-500 mb-4">No rooms yet</p>
        <Button
          class="bg-white text-black hover:bg-gray-200"
          @click="showCreateDialog = true">
          Create your first room
        </Button>
      </div>

      <!-- Room list -->
      <div v-else class="space-y-2">
        <div
          v-for="room in rooms"
          :key="room.id"
          class="group flex items-center gap-4 p-4 rounded-lg bg-white/2 border border-white/5 hover:border-white/10 hover:bg-white/4 transition-all cursor-pointer"
          @click="selectRoom(room)">
          <!-- Room Icon -->
          <div
            class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
            <span class="text-lg font-medium text-gray-400">{{
              room.name.charAt(0).toUpperCase()
            }}</span>
          </div>

          <!-- Room Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h3 class="font-medium text-white truncate">{{ room.name }}</h3>
              <span
                class="text-[10px] font-medium px-1.5 py-0.5 rounded uppercase tracking-wider"
                :class="{
                  'bg-white/10 text-white': room.userRole === 'owner',
                  'bg-white/5 text-gray-400': room.userRole === 'editor',
                  'bg-white/5 text-gray-500': room.userRole === 'viewer',
                }">
                {{ room.userRole }}
              </span>
            </div>
            <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
              <span class="flex items-center gap-1">
                <svg
                  class="w-3 h-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                {{ room.memberCount }}
              </span>
              <span>{{ room.ownerName }}</span>
              <button
                @click.stop="copyCode(room.code)"
                class="font-mono text-gray-600 hover:text-gray-400 transition-colors flex items-center gap-1">
                {{ room.code }}
                <svg
                  class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Actions -->
          <div
            class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              v-if="room.userRole === 'owner'"
              @click.stop="openMembersDialog(room)"
              class="p-2 text-gray-500 hover:text-white hover:bg-white/5 rounded-md transition-colors"
              title="Members">
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </button>
            <button
              v-if="room.userRole === 'owner'"
              @click.stop="deleteRoom(room)"
              class="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-md transition-colors"
              title="Delete">
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
            <button
              v-else
              @click.stop="leaveRoom(room)"
              class="p-2 text-gray-500 hover:text-white hover:bg-white/5 rounded-md transition-colors"
              title="Leave">
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Room Dialog -->
    <Dialog v-model:open="showCreateDialog">
      <DialogHeader>
        <DialogTitle>Create Room</DialogTitle>
        <DialogDescription>
          Create a new workspace. Share the code with others to invite them.
        </DialogDescription>
      </DialogHeader>
      <DialogContent>
        <form @submit.prevent="createRoom" class="space-y-4">
          <div class="space-y-2">
            <Label for="create-name" class="text-white">Room Name</Label>
            <Input
              id="create-name"
              v-model="createForm.name"
              placeholder="My Project"
              class="text-white"
              required />
          </div>
          <div class="space-y-2">
            <Label for="create-password" class="text-white">Password</Label>
            <Input
              id="create-password"
              v-model="createForm.password"
              type="password"
              placeholder="••••••••"
              class="text-white"
              required />
            <p class="text-xs text-gray-500">Others will need this to join</p>
          </div>
          <div v-if="formError" class="text-red-400 text-sm">
            {{ formError }}
          </div>
        </form>
      </DialogContent>
      <DialogFooter>
        <Button
          variant="ghost"
          class="bg-red-500 text-white"
          @click="showCreateDialog = false"
          >Cancel</Button
        >
        <Button :disabled="formLoading" @click="createRoom">
          {{ formLoading ? "Creating..." : "Create" }}
        </Button>
      </DialogFooter>
    </Dialog>

    <!-- Join Room Dialog -->
    <Dialog v-model:open="showJoinDialog">
      <DialogHeader>
        <DialogTitle>Join Room</DialogTitle>
        <DialogDescription>
          Enter the room code and password to join.
        </DialogDescription>
      </DialogHeader>
      <DialogContent>
        <form @submit.prevent="joinRoom" class="space-y-4">
          <div class="space-y-2">
            <Label for="join-code" class="text-white">Room Code</Label>
            <Input
              id="join-code"
              v-model="joinForm.code"
              placeholder="ABC12345"
              class="font-mono uppercase text-white"
              required />
          </div>
          <div class="space-y-2">
            <Label for="join-password" class="text-white">Password</Label>
            <Input
              id="join-password"
              v-model="joinForm.password"
              type="password"
              placeholder="••••••••"
              class="text-white"
              required />
          </div>
          <div v-if="formError" class="text-red-400 text-sm">
            {{ formError }}
          </div>
        </form>
      </DialogContent>
      <DialogFooter>
        <Button
          variant="ghost"
          class="bg-red-500 text-white"
          @click="showJoinDialog = false"
          >Cancel</Button
        >
        <Button :disabled="formLoading" @click="joinRoom">
          {{ formLoading ? "Joining..." : "Join" }}
        </Button>
      </DialogFooter>
    </Dialog>

    <!-- Members Dialog -->
    <Dialog v-model:open="showMembersDialog">
      <DialogHeader>
        <DialogTitle>Room Members</DialogTitle>
        <DialogDescription v-if="selectedRoom">
          Manage members of "{{ selectedRoom.name }}"
        </DialogDescription>
      </DialogHeader>
      <DialogContent>
        <div v-if="selectedRoom?.members" class="space-y-2">
          <div
            v-for="member in selectedRoom.members"
            :key="member.id"
            class="flex items-center justify-between p-3 rounded-lg bg-white/5">
            <div class="flex items-center gap-3">
              <div
                class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-sm font-medium text-gray-300">
                {{ member.username.charAt(0).toUpperCase() }}
              </div>
              <div>
                <div class="text-sm font-medium text-white">
                  {{ member.username }}
                </div>
                <div class="text-xs text-gray-500">
                  Joined {{ new Date(member.joinedAt).toLocaleDateString() }}
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span
                v-if="member.role === 'owner'"
                class="text-xs font-medium px-2 py-1 rounded bg-white/10 text-white">
                Owner
              </span>
              <template v-else>
                <Select
                  :model-value="member.role"
                  :options="roleOptions"
                  class="w-24"
                  @update:model-value="changeRole(member, $event)" />
                <button
                  class="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                  @click="kickMember(member)"
                  title="Remove">
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
              </template>
            </div>
          </div>
        </div>
      </DialogContent>
      <DialogFooter>
        <Button @click="showMembersDialog = false">Close</Button>
      </DialogFooter>
    </Dialog>
  </div>
</template>
