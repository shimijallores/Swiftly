<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: String,
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: "Select...",
  },
  disabled: Boolean,
});

const emit = defineEmits(["update:modelValue"]);

const isOpen = ref(false);

const selectedLabel = computed(() => {
  const option = props.options.find((o) => o.value === props.modelValue);
  return option?.label || props.placeholder;
});

function select(value) {
  emit("update:modelValue", value);
  isOpen.value = false;
}

import { computed } from "vue";
</script>

<template>
  <div class="relative">
    <button
      type="button"
      :disabled="disabled"
      class="flex h-9 w-full items-center justify-between rounded-md border border-gray-700 bg-[#2d2d2d] px-3 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 disabled:cursor-not-allowed disabled:opacity-50"
      @click="isOpen = !isOpen">
      <span>{{ selectedLabel }}</span>
      <svg
        class="h-4 w-4 opacity-50"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    <div
      v-if="isOpen"
      class="absolute z-50 mt-1 w-full rounded-md border border-gray-700 bg-[#2d2d2d] py-1 shadow-lg">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="flex w-full items-center px-3 py-2 text-sm text-white hover:bg-gray-700"
        :class="{ 'bg-gray-700': option.value === modelValue }"
        @click="select(option.value)">
        {{ option.label }}
      </button>
    </div>
    <!-- Click outside to close -->
    <div v-if="isOpen" class="fixed inset-0 z-40" @click="isOpen = false"></div>
  </div>
</template>
