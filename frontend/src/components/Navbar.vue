<script setup>
import { Button } from "@/components/ui/button";

const props = defineProps({
  currentPage: {
    type: String,
    default: "home",
  },
});

const emit = defineEmits(["navigate", "logout"]);
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

          <!-- Nav Links -->
          <div class="flex items-center gap-1">
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
              class="px-3 py-1.5 text-sm rounded-md text-gray-500 cursor-not-allowed">
              Templates
            </button>
          </div>
        </div>

        <!-- User Actions -->
        <Button
          variant="ghost"
          size="sm"
          class="text-gray-400 hover:text-white"
          @click="emit('logout')">
          Logout
        </Button>
      </div>
    </div>
  </nav>
</template>
