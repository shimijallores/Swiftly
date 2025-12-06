<script setup>
import { Button } from "@/components/ui/button";

const emit = defineEmits(["navigate", "go-to-rooms"]);
</script>

<template>
  <div class="min-h-screen bg-[#0a0a0a] text-white">
    <!-- Hero Section -->
    <div class="pt-32 pb-20 px-6">
      <div class="max-w-4xl mx-auto text-center">
        <!-- Logo -->
        <div class="flex justify-center mb-8">
          <img src="/logo.svg" alt="Swiftly" class="h-16 w-16" />
        </div>

        <!-- Headline -->
        <h1 class="text-5xl font-bold tracking-tight mb-4">
          Code together,
          <span class="text-gray-500">in real-time</span>
        </h1>

        <p class="text-lg text-gray-400 max-w-xl mx-auto mb-10">
          A minimalist collaborative code editor. Create rooms, invite your
          team, and build together with live sync, version history, and instant
          preview.
        </p>

        <!-- CTA -->
        <div class="flex items-center justify-center gap-3">
          <Button
            size="lg"
            class="px-8 bg-white text-black hover:bg-gray-200"
            @click="emit('go-to-rooms')">
            Get Started
          </Button>
          <Button
            variant="outline"
            size="lg"
            class="px-8 border-white/20 text-white hover:bg-white/5">
            Learn More
          </Button>
        </div>
      </div>
    </div>

    <!-- Features Grid -->
    <div class="py-20 px-6 border-t border-white/5">
      <div class="max-w-5xl mx-auto">
        <h2
          class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-8 text-center">
          Features
        </h2>

        <div class="grid md:grid-cols-3 gap-6">
          <!-- Feature 1 -->
          <div
            class="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
            <div
              class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 class="font-medium text-white mb-2">Team Rooms</h3>
            <p class="text-sm text-gray-500 leading-relaxed">
              Create private rooms with role-based access. Owners, editors, and
              viewers with granular permissions.
            </p>
          </div>

          <!-- Feature 2 -->
          <div
            class="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
            <div
              class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 class="font-medium text-white mb-2">Real-time Sync</h3>
            <p class="text-sm text-gray-500 leading-relaxed">
              See changes instantly with CRDT-powered sync. Cursors, selections,
              and typing indicators included.
            </p>
          </div>

          <!-- Feature 3 -->
          <div
            class="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
            <div
              class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="font-medium text-white mb-2">Version History</h3>
            <p class="text-sm text-gray-500 leading-relaxed">
              Automatic snapshots with restore capability. Never lose your work,
              travel back in time.
            </p>
          </div>

          <!-- Feature 4 -->
          <div
            class="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
            <div
              class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
            <h3 class="font-medium text-white mb-2">Virtual File System</h3>
            <p class="text-sm text-gray-500 leading-relaxed">
              Organize your code with folders and files. Full project structure
              in your browser.
            </p>
          </div>

          <!-- Feature 5 -->
          <div
            class="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
            <div
              class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h3 class="font-medium text-white mb-2">Live Preview</h3>
            <p class="text-sm text-gray-500 leading-relaxed">
              Instant HTML preview with CSS and JS support. See your changes as
              you type.
            </p>
          </div>

          <!-- Feature 6 -->
          <div
            class="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors">
            <div
              class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <h3 class="font-medium text-white mb-2">Export Project</h3>
            <p class="text-sm text-gray-500 leading-relaxed">
              Download your entire project as a ZIP file. Take your work
              anywhere.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="py-8 px-6 border-t border-white/5">
      <div class="max-w-5xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2 text-sm text-gray-500">
          <img src="/logo.svg" alt="Swiftly" class="h-5 w-5 opacity-50" />
          <span>Swiftly</span>
        </div>
        <p class="text-sm text-gray-600">
          Built for developers who collaborate
        </p>
      </div>
    </div>
  </div>
</template>
