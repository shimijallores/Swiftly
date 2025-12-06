<script setup>
defineProps({
  class: String,
});
</script>

<template>
  <h2 class="text-lg font-semibold text-white" :class="class">
    <slot></slot>
  </h2>
</template>
