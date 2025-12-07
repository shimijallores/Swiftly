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

const emit = defineEmits(["register", "switchToLogin"]);

const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const error = ref("");
const loading = ref(false);

async function handleSubmit() {
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
</script>

<template>
  <Card class="w-full max-w-md">
    <CardHeader>
      <CardTitle class="text-2xl">Register</CardTitle>
      <CardDescription>
        Create an account to start collaborating
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
            placeholder="Choose a username"
            required />
        </div>
        <div class="space-y-2">
          <Label for="email">Email (optional)</Label>
          <Input
            id="email"
            v-model="email"
            type="email"
            placeholder="Enter your email" />
        </div>
        <div class="space-y-2">
          <Label for="password">Password</Label>
          <Input
            id="password"
            v-model="password"
            type="password"
            placeholder="Choose a password"
            required />
        </div>
        <div class="space-y-2">
          <Label for="confirmPassword">Confirm Password</Label>
          <Input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            required />
        </div>
        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      </CardContent>
      <CardFooter class="flex flex-col gap-4">
        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? "Creating account..." : "Register" }}
        </Button>
        <p class="text-sm text-muted-foreground">
          Already have an account?
          <button
            type="button"
            class="text-primary underline-offset-4 hover:underline"
            @click="emit('switchToLogin')">
            Login
          </button>
        </p>
      </CardFooter>
    </form>
  </Card>
</template>
