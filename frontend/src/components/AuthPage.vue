<script setup>
import { ref } from "vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiUrl } from "@/utils/api";

const emit = defineEmits(["login", "register", "home"]);

const mode = ref("login"); // 'login' or 'register'
const loading = ref(false);
const error = ref("");

// Form fields
const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");

async function handleLogin() {
  error.value = "";
  loading.value = true;

  try {
    const response = await fetch(apiUrl("/api/auth/login/"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      emit("login", data);
    } else {
      error.value = data.error || "Login failed";
    }
  } catch (e) {
    error.value = "Network error. Please try again.";
  } finally {
    loading.value = false;
  }
}

async function handleRegister() {
  error.value = "";

  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match";
    return;
  }

  if (password.value.length < 6) {
    error.value = "Password must be at least 6 characters";
    return;
  }

  loading.value = true;

  try {
    const response = await fetch(apiUrl("/api/auth/register/"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      emit("register", data);
    } else {
      error.value = data.error || "Registration failed";
    }
  } catch (e) {
    error.value = "Network error. Please try again.";
  } finally {
    loading.value = false;
  }
}

function switchMode() {
  mode.value = mode.value === "login" ? "register" : "login";
  error.value = "";
}

function handleSubmit() {
  if (mode.value === "login") {
    handleLogin();
  } else {
    handleRegister();
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#0a0a0a] flex">
    <!-- Left side - Branding -->
    <div
      class="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 border-r border-white/5">
      <button
        @click="emit('home')"
        class="flex items-center gap-3 hover:opacity-80 transition-opacity">
        <img src="/logo.svg" alt="Swiftly" class="h-8 w-8" />
        <span class="font-semibold text-white text-xl tracking-tight"
          >Swiftly</span
        >
      </button>

      <div class="max-w-md">
        <h1 class="text-4xl font-bold text-white leading-tight mb-4">
          Collaborative coding,<br />
          <span class="text-gray-500">simplified.</span>
        </h1>
        <p class="text-gray-500 leading-relaxed">
          A web-based collaborative code editor. Create rooms, invite your team,
          and build together swiftly.
        </p>
      </div>

      <p class="text-sm text-gray-600">Built by yours truly, Shimi Jallores</p>
    </div>

    <!-- Right side - Auth Form -->
    <div class="flex-1 flex items-center justify-center p-8">
      <div class="w-full max-w-sm">
        <!-- Mobile Logo + Home Link -->
        <div class="lg:hidden flex items-center justify-center gap-2 mb-10">
          <button
            @click="emit('home')"
            class="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <img src="/logo.svg" alt="Swiftly" class="h-8 w-8" />
            <span class="font-semibold text-white text-xl tracking-tight"
              >Swiftly</span
            >
          </button>
        </div>

        <!-- Header -->
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-white mb-2">
            {{ mode === "login" ? "Welcome back" : "Create account" }}
          </h2>
          <p class="text-gray-500 text-sm">
            {{
              mode === "login"
                ? "Enter your credentials to continue"
                : "Sign up to start collaborating"
            }}
          </p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="space-y-2">
            <Label for="username" class="text-gray-400">Username</Label>
            <Input
              id="username"
              v-model="username"
              type="text"
              placeholder="Enter your username"
              class="bg-white/5 border-white/10 text-white placeholder:text-gray-600 focus:border-white/20"
              required />
          </div>

          <div v-if="mode === 'register'" class="space-y-2">
            <Label for="email" class="text-gray-400"
              >Email <span class="text-gray-600">(optional)</span></Label
            >
            <Input
              id="email"
              v-model="email"
              type="email"
              placeholder="Enter your email"
              class="bg-white/5 border-white/10 text-white placeholder:text-gray-600 focus:border-white/20" />
          </div>

          <div class="space-y-2">
            <Label for="password" class="text-gray-400">Password</Label>
            <Input
              id="password"
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="bg-white/5 border-white/10 text-white placeholder:text-gray-600 focus:border-white/20"
              required />
          </div>

          <div v-if="mode === 'register'" class="space-y-2">
            <Label for="confirmPassword" class="text-gray-400"
              >Confirm Password</Label
            >
            <Input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              placeholder="••••••••"
              class="bg-white/5 border-white/10 text-white placeholder:text-gray-600 focus:border-white/20"
              required />
          </div>

          <!-- Error -->
          <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

          <!-- Submit -->
          <Button
            type="submit"
            class="w-full bg-white text-black hover:bg-gray-200 mt-2"
            :disabled="loading">
            {{
              loading
                ? mode === "login"
                  ? "Signing in..."
                  : "Creating account..."
                : mode === "login"
                ? "Sign in"
                : "Create account"
            }}
          </Button>
        </form>

        <!-- Switch mode -->
        <p class="text-center mt-6 text-sm text-gray-500">
          {{
            mode === "login"
              ? "Don't have an account?"
              : "Already have an account?"
          }}
          <button
            type="button"
            class="text-white hover:underline underline-offset-4 ml-1"
            @click="switchMode">
            {{ mode === "login" ? "Sign up" : "Sign in" }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>
