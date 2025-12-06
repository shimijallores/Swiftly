<script setup>
defineProps({
  class: String,
});
</script>

<template>
  <div class="flex flex-col space-y-1.5 p-6" :class="class">
    <slot></slot>
  </div>
</template>
