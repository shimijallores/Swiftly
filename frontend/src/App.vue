<script setup>
import { ref, onMounted } from "vue";
import CollabEditor from "./components/CollabEditor.vue";
import AuthPage from "./components/AuthPage.vue";
import Navbar from "./components/Navbar.vue";
import HomePage from "./components/HomePage.vue";
import RoomsPage from "./components/RoomsPage.vue";
import { apiUrl } from "@/utils/api";

const user = ref(null);
const loading = ref(true);
const currentRoom = ref(null);
const currentPage = ref("home"); // 'home' or 'rooms'
const showAuth = ref(false);

// Check if user is already logged in
async function checkAuth() {
  try {
    const response = await fetch(apiUrl("/api/auth/me/"), {
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
  showAuth.value = false;
  currentPage.value = "rooms";
}

async function handleLogout() {
  try {
    await fetch(apiUrl("/api/auth/logout/"), {
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

function goToAuth() {
  showAuth.value = true;
}

function handleGoToRooms() {
  if (user.value) {
    currentPage.value = "rooms";
  } else {
    showAuth.value = true;
  }
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

  <!-- Editor View (requires auth + room) -->
  <template v-else-if="user && currentRoom">
    <CollabEditor
      :user="user"
      :room="currentRoom"
      @logout="handleLogout"
      @exit-room="handleExitRoom" />
  </template>

  <!-- Auth Page -->
  <template v-else-if="showAuth">
    <AuthPage
      @login="handleAuth"
      @register="handleAuth"
      @home="showAuth = false" />
  </template>

  <!-- Main App (works for both logged in and logged out) -->
  <template v-else>
    <Navbar
      :current-page="currentPage"
      :user="user"
      @navigate="handleNavigate"
      @logout="handleLogout"
      @login="goToAuth" />

    <div class="h-screen w-screen overflow-auto">
      <HomePage v-if="currentPage === 'home'" @go-to-rooms="handleGoToRooms" />

      <RoomsPage
        v-else-if="currentPage === 'rooms' && user"
        @select-room="handleSelectRoom" />
    </div>
  </template>
</template>

<style>
html,
body,
#app {
  @apply h-full w-full overflow-hidden box-border;
}
</style>
