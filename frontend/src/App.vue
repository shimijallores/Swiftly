<script setup>
import { ref, onMounted } from "vue";
import CollabEditor from "./components/CollabEditor.vue";
import AuthPage from "./components/AuthPage.vue";
import Navbar from "./components/Navbar.vue";
import HomePage from "./components/HomePage.vue";
import RoomsPage from "./components/RoomsPage.vue";

const user = ref(null);
const loading = ref(true);
const currentRoom = ref(null);
const currentPage = ref("home"); // 'home' or 'rooms'

// Check if user is already logged in
async function checkAuth() {
  try {
    const response = await fetch("http://localhost:8000/api/auth/me/", {
      credentials: "include",
    });
    if (response.ok) {
      user.value = await response.json();
    }
  } catch (e) {
    console.error("Auth check failed:", e);
  } finally {
    loading.value = false;
  }
}

function handleAuth(userData) {
  user.value = userData;
  currentPage.value = "rooms";
}

async function handleLogout() {
  try {
    await fetch("http://localhost:8000/api/auth/logout/", {
      method: "POST",
      credentials: "include",
    });
    user.value = null;
    currentRoom.value = null;
    currentPage.value = "home";
    localStorage.removeItem("swiftly_client_id");
  } catch (e) {
    console.error("Logout failed:", e);
  }
}

function handleSelectRoom(room) {
  currentRoom.value = room;
}

function handleExitRoom() {
  currentRoom.value = null;
}

function handleNavigate(page) {
  currentPage.value = page;
}

function goToRooms() {
  currentPage.value = "rooms";
}

onMounted(() => {
  checkAuth();
});
</script>

<template>
  <!-- Loading State -->
  <div
    v-if="loading"
    class="h-screen w-screen flex items-center justify-center bg-[#0a0a0a]">
    <div class="flex items-center gap-3">
      <img src="/logo.svg" alt="Swiftly" class="h-8 w-8 animate-pulse" />
      <span class="text-gray-500">Loading...</span>
    </div>
  </div>

  <!-- Authenticated -->
  <template v-else-if="user">
    <!-- Editor View -->
    <CollabEditor
      v-if="currentRoom"
      :user="user"
      :room="currentRoom"
      @logout="handleLogout"
      @exit-room="handleExitRoom" />

    <!-- Main App -->
    <template v-else>
      <Navbar
        :current-page="currentPage"
        @navigate="handleNavigate"
        @logout="handleLogout" />

      <HomePage v-if="currentPage === 'home'" @go-to-rooms="goToRooms" />

      <RoomsPage
        v-else-if="currentPage === 'rooms'"
        @select-room="handleSelectRoom" />
    </template>
  </template>

  <!-- Auth Page -->
  <AuthPage v-else @login="handleAuth" @register="handleAuth" />
</template>

<style>
html,
body,
#app {
  @apply h-full w-full overflow-hidden box-border;
}
</style>
