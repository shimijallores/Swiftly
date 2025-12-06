<script setup>
import { ref, onMounted } from "vue";
import CollabEditor from "./components/CollabEditor.vue";
import LoginForm from "./components/LoginForm.vue";
import RegisterForm from "./components/RegisterForm.vue";
import { Button } from "@/components/ui/button";

const user = ref(null);
const authView = ref("login"); // 'login' or 'register'
const loading = ref(true);

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

function handleLogin(userData) {
  user.value = userData;
}

function handleRegister(userData) {
  user.value = userData;
}

async function handleLogout() {
  try {
    await fetch("http://localhost:8000/api/auth/logout/", {
      method: "POST",
      credentials: "include",
    });
    user.value = null;
    // Clear localStorage client_id on logout
    localStorage.removeItem("swiftly_client_id");
  } catch (e) {
    console.error("Logout failed:", e);
  }
}

onMounted(() => {
  checkAuth();
});
</script>

<template>
  <div
    v-if="loading"
    class="h-screen w-screen flex items-center justify-center bg-[#1e1e1e]">
    <p class="text-gray-400">Loading...</p>
  </div>

  <template v-else-if="user">
    <CollabEditor :user="user" @logout="handleLogout" />
  </template>

  <div
    v-else
    class="h-screen w-screen flex items-center justify-center bg-[#1e1e1e]">
    <LoginForm
      v-if="authView === 'login'"
      @login="handleLogin"
      @switch-to-register="authView = 'register'" />
    <RegisterForm
      v-else
      @register="handleRegister"
      @switch-to-login="authView = 'login'" />
  </div>
</template>

<style>
html,
body,
#app {
  @apply h-full w-full overflow-hidden box-border;
}
</style>
