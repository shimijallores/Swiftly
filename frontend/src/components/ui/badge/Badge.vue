<script setup>
defineProps({
  variant: {
    type: String,
    default: "default",
    validator: (v) => ["default", "secondary", "outline"].includes(v),
  },
});

const variantClasses = {
  default: "bg-white text-black",
  secondary: "bg-gray-700 text-gray-200",
  outline: "border border-gray-600 text-gray-300",
};
</script>

<template>
  <span
    class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium"
    :class="variantClasses[variant]">
    <slot></slot>
  </span>
</template>
