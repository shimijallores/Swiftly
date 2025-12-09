<template>
  <div class="pt-14 min-h-screen bg-[#0a0a0a]">
    <div class="max-w-4xl mx-auto px-6 py-10">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-semibold text-white tracking-tight">
            Templates
          </h1>
          <p class="text-gray-500 text-sm mt-1">
            Choose a template to get started quickly
          </p>
        </div>
      </div>

      <!-- Templates Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Vue.js Template -->
        <div
          class="bg-white/5 border border-white/10 rounded-lg p-6 hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer"
          @click="selectTemplate('vue')">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center">
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/9/95/Vue.js_Logo_2.svg"
                alt="" />
            </div>
            <div>
              <h3 class="font-semibold text-lg text-white">Vue.js</h3>
              <p class="text-sm text-gray-400">Modern Vue.js app with CDN</p>
            </div>
          </div>
          <p class="text-sm text-gray-300">
            A complete Vue.js application with components, routing, and modern
            tooling setup.
          </p>
          <Button
            type="button"
            class="mt-4 bg-neutral-800 hover:bg-neutral-200">
            Use Template
          </Button>
        </div>
      </div>

      <!-- Create Room Dialog -->
      <Dialog :open="showCreateDialog" @update:open="showCreateDialog = $event">
        <DialogContent class="w-full">
          <DialogHeader class="w-full">
            <DialogTitle
              >Create Room from using the
              {{ selectedTemplateName }} Template</DialogTitle
            >
            <DialogDescription>
              Set up your new {{ selectedTemplateName }} room
            </DialogDescription>
          </DialogHeader>

          <form @submit.prevent="createRoom" class="space-y-4 text-white">
            <div class="space-y-2">
              <Label for="room-name">Room Name</Label>
              <Input
                id="room-name"
                v-model="createForm.name"
                placeholder="Enter room name"
                required />
            </div>

            <div class="space-y-2">
              <Label for="room-password">Password</Label>
              <Input
                id="room-password"
                type="password"
                v-model="createForm.password"
                placeholder="Enter password (min 4 chars)"
                required />
            </div>

            <DialogFooter>
              <Button
                type="button"
                class="bg-red-500"
                @click="showCreateDialog = false">
                Cancel
              </Button>
              <Button :disabled="formLoading" type="submit">
                {{ formLoading ? "Creating..." : "Create Room" }}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { apiUrl } from "@/utils/api";

const emit = defineEmits(["select-room"]);

// State
const selectedTemplate = ref(null);
const selectedTemplateName = ref("");
const showCreateDialog = ref(false);
const createForm = ref({ name: "", password: "" });
const formLoading = ref(false);

function selectTemplate(template) {
  selectedTemplate.value = template;
  selectedTemplateName.value = template === "vue" ? "Vue.js" : template;
  showCreateDialog.value = true;
}

async function createRoom() {
  formLoading.value = true;
  try {
    const res = await fetch(apiUrl("/api/rooms/"), {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...createForm.value,
        template: selectedTemplate.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to create room");

    showCreateDialog.value = false;
    createForm.value = { name: "", password: "" };
    selectedTemplate.value = null;

    // Emit to select the newly created room
    emit("select-room", data);
  } catch (e) {
    console.error("Failed to create room:", e);
    // You could add error handling here
  } finally {
    formLoading.value = false;
  }
}
</script>
