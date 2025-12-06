<script setup>
defineProps({
  class: String,
});
</script>

<template>
  <div
    class="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 p-6 pt-0"
    :class="class">
    <slot></slot>
  </div>
</template>
