<script setup>
defineProps({
  class: String,
});
</script>

<template>
  <p class="text-sm text-gray-400" :class="class">
    <slot></slot>
  </p>
</template>
