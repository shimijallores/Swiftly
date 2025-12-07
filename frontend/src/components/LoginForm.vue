<script setup>
import { ref } from "vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiUrl } from "@/lib/api";

const emit = defineEmits(["login", "switchToRegister"]);

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function handleSubmit() {
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
</script>

<template>
  <Card class="w-full max-w-md">
    <CardHeader>
      <CardTitle class="text-2xl">Login</CardTitle>
      <CardDescription>
        Enter your credentials to access the editor
      </CardDescription>
    </CardHeader>
    <form @submit.prevent="handleSubmit">
      <CardContent class="space-y-4">
        <div class="space-y-2">
          <Label for="username">Username</Label>
          <Input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter your username"
            required />
        </div>
        <div class="space-y-2">
          <Label for="password">Password</Label>
          <Input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            required />
        </div>
        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      </CardContent>
      <CardFooter class="flex flex-col gap-4">
        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? "Logging in..." : "Login" }}
        </Button>
        <p class="text-sm text-muted-foreground">
          Don't have an account?
          <button
            type="button"
            class="text-primary underline-offset-4 hover:underline"
            @click="emit('switchToRegister')">
            Register
          </button>
        </p>
      </CardFooter>
    </form>
  </Card>
</template>
