<script setup>
import { ref, onMounted, computed } from "vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogContent,
  DialogFooter,
} from "@/components/ui/dialog";
import { apiUrl } from "@/lib/api";

const emit = defineEmits(["select-room", "logout"]);

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
    // Check if room already in list
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
  if (!confirm(`Are you sure you want to leave "${room.name}"?`)) return;
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
  if (
    !confirm(
      `Are you sure you want to delete "${room.name}"? This cannot be undone.`
    )
  )
    return;
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
  if (!confirm(`Remove ${member.username} from the room?`)) return;
  try {
    const res = await fetch(
      apiUrl(`/api/rooms/${selectedRoom.value.id}/members/${member.id}/kick/`),
      {
        method: "DELETE",
        credentials: "include",
      }
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
  navigator.clipboard.writeText(code);
}

const roleOptions = [
  { value: "editor", label: "Editor" },
  { value: "viewer", label: "Viewer" },
];

function getRoleBadgeVariant(role) {
  switch (role) {
    case "owner":
      return "default";
    case "editor":
      return "secondary";
    default:
      return "outline";
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#121212] text-white p-8">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight">Rooms</h1>
          <p class="text-gray-400 text-sm mt-1">
            Create or join a collaborative workspace
          </p>
        </div>
        <div class="flex gap-2">
          <Button variant="ghost" @click="emit('logout')"> Logout </Button>
          <Button variant="outline" @click="showJoinDialog = true">
            Join Room
          </Button>
          <Button @click="showCreateDialog = true"> Create Room </Button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-gray-400">
        Loading rooms...
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-12 text-red-400">
        {{ error }}
      </div>

      <!-- Empty state -->
      <div
        v-else-if="rooms.length === 0"
        class="text-center py-16 border border-dashed border-gray-700 rounded-lg">
        <div class="text-gray-500 mb-4">
          <svg
            class="w-12 h-12 mx-auto mb-4 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <p>No rooms yet</p>
        </div>
        <Button @click="showCreateDialog = true">Create your first room</Button>
      </div>

      <!-- Room grid -->
      <div v-else class="grid gap-4">
        <Card
          v-for="room in rooms"
          :key="room.id"
          class="bg-[#1e1e1e] border-gray-800 hover:border-gray-700 transition-colors">
          <CardHeader class="pb-3">
            <div class="flex items-start justify-between">
              <div>
                <CardTitle class="text-white">{{ room.name }}</CardTitle>
                <CardDescription class="mt-1">
                  <span
                    class="font-mono text-xs bg-[#2d2d2d] px-2 py-1 rounded">
                    {{ room.code }}
                  </span>
                  <button
                    class="ml-2 text-gray-500 hover:text-white transition-colors"
                    @click.stop="copyCode(room.code)"
                    title="Copy code">
                    <svg
                      class="w-4 h-4 inline"
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
                </CardDescription>
              </div>
              <Badge :variant="getRoleBadgeVariant(room.userRole)">
                {{ room.userRole }}
              </Badge>
            </div>
          </CardHeader>
          <CardContent class="pb-3">
            <div class="flex items-center gap-4 text-sm text-gray-400">
              <span class="flex items-center gap-1">
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                {{ room.memberCount }} member{{
                  room.memberCount !== 1 ? "s" : ""
                }}
              </span>
              <span>Owner: {{ room.ownerName }}</span>
            </div>
          </CardContent>
          <CardFooter class="pt-3 border-t border-gray-800 flex gap-2">
            <Button size="sm" @click="selectRoom(room)"> Enter </Button>
            <Button
              v-if="room.userRole === 'owner'"
              variant="ghost"
              size="sm"
              @click="openMembersDialog(room)">
              Members
            </Button>
            <Button
              v-if="room.userRole === 'owner'"
              variant="ghost"
              size="sm"
              class="text-red-400 hover:text-red-300 hover:bg-red-950"
              @click="deleteRoom(room)">
              Delete
            </Button>
            <Button
              v-else
              variant="ghost"
              size="sm"
              class="text-gray-400"
              @click="leaveRoom(room)">
              Leave
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>

    <!-- Create Room Dialog -->
    <Dialog v-model:open="showCreateDialog">
      <DialogHeader>
        <DialogTitle>Create Room</DialogTitle>
        <DialogDescription>
          Create a new collaborative workspace. Share the code with others to
          let them join.
        </DialogDescription>
      </DialogHeader>
      <DialogContent>
        <form @submit.prevent="createRoom" class="space-y-4">
          <div class="space-y-2">
            <Label for="create-name">Room Name</Label>
            <Input
              id="create-name"
              v-model="createForm.name"
              placeholder="My Project"
              required />
          </div>
          <div class="space-y-2">
            <Label for="create-password">Password</Label>
            <Input
              id="create-password"
              v-model="createForm.password"
              type="password"
              placeholder="••••••••"
              required />
            <p class="text-xs text-gray-500">
              Others will need this password to join
            </p>
          </div>
          <div v-if="formError" class="text-red-400 text-sm">
            {{ formError }}
          </div>
        </form>
      </DialogContent>
      <DialogFooter>
        <Button variant="ghost" @click="showCreateDialog = false">
          Cancel
        </Button>
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
          Enter the room code and password to join an existing workspace.
        </DialogDescription>
      </DialogHeader>
      <DialogContent>
        <form @submit.prevent="joinRoom" class="space-y-4">
          <div class="space-y-2">
            <Label for="join-code">Room Code</Label>
            <Input
              id="join-code"
              v-model="joinForm.code"
              placeholder="ABC12345"
              class="font-mono uppercase"
              required />
          </div>
          <div class="space-y-2">
            <Label for="join-password">Password</Label>
            <Input
              id="join-password"
              v-model="joinForm.password"
              type="password"
              placeholder="••••••••"
              required />
          </div>
          <div v-if="formError" class="text-red-400 text-sm">
            {{ formError }}
          </div>
        </form>
      </DialogContent>
      <DialogFooter>
        <Button variant="ghost" @click="showJoinDialog = false">
          Cancel
        </Button>
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
            class="flex items-center justify-between p-3 rounded-lg bg-[#2d2d2d]">
            <div class="flex items-center gap-3">
              <div
                class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-sm font-medium">
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
              <Badge
                v-if="member.role === 'owner'"
                :variant="getRoleBadgeVariant(member.role)">
                {{ member.role }}
              </Badge>
              <template v-else>
                <Select
                  :model-value="member.role"
                  :options="roleOptions"
                  class="w-24"
                  @update:model-value="changeRole(member, $event)" />
                <button
                  class="p-1 text-gray-500 hover:text-red-400 transition-colors"
                  @click="kickMember(member)"
                  title="Remove member">
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
        <Button @click="showMembersDialog = false"> Close </Button>
      </DialogFooter>
    </Dialog>
  </div>
</template>
