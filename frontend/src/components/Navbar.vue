<script setup>
import { computed } from "vue";
import { Button } from "@/components/ui/button";

const props = defineProps({
  currentPage: {
    type: String,
    default: "home",
  },
  user: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["navigate", "logout", "login"]);

const userName = computed(() => {
  if (!props.user) return null;
  return props.user.collab_user?.name || props.user.username;
});

const userColor = computed(() => {
  return props.user?.collab_user?.color || "#3b82f6";
});
</script>

<template>
  <nav
    class="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-sm border-b border-white/5">
    <div class="max-w-6xl mx-auto px-6">
      <div class="flex items-center justify-between h-14">
        <!-- Logo -->
        <div class="flex items-center gap-8">
          <button
            @click="emit('navigate', 'home')"
            class="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <img src="/logo.svg" alt="Swiftly" class="h-7 w-7" />
            <span class="font-semibold text-white text-lg tracking-tight"
              >Swiftly</span
            >
          </button>

          <!-- Nav Links (only show full nav when logged in) -->
          <div v-if="user" class="flex items-center gap-1">
            <button
              @click="emit('navigate', 'home')"
              class="px-3 py-1.5 text-sm rounded-md transition-colors"
              :class="
                currentPage === 'home'
                  ? 'text-white bg-white/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              ">
              Home
            </button>
            <button
              @click="emit('navigate', 'rooms')"
              class="px-3 py-1.5 text-sm rounded-md transition-colors"
              :class="
                currentPage === 'rooms'
                  ? 'text-white bg-white/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              ">
              Rooms
            </button>
            <button
              @click="emit('navigate', 'templates')"
              class="px-3 py-1.5 text-sm rounded-md transition-colors"
              :class="
                currentPage === 'templates'
                  ? 'text-white bg-white/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              ">
              Templates
            </button>
          </div>
        </div>

        <!-- User Actions -->
        <div class="flex items-center gap-3">
          <!-- Logged In: Show welcome message + logout -->
          <template v-if="user">
            <span class="text-sm text-gray-400">
              Welcome back, <span class="text-white">{{ userName }}</span>
            </span>
            <div class="w-px h-4 bg-white/10"></div>
            <Button
              variant="ghost"
              size="sm"
              class="text-gray-400 hover:text-white flex items-center gap-1.5"
              @click="emit('logout')">
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
              Logout
            </Button>
          </template>

          <!-- Logged Out: Show login + get started -->
          <template v-else>
            <Button
              variant="ghost"
              size="sm"
              class="text-gray-400 hover:text-white"
              @click="emit('login')">
              Log in
            </Button>
            <Button
              size="sm"
              class="bg-white text-black hover:bg-gray-200"
              @click="emit('login')">
              Get Started
            </Button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>
