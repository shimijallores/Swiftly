<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50"
      @click="close"
      @contextmenu.prevent="close">
      <div
        ref="menuRef"
        class="absolute bg-[#0f0f0f] border border-white/10 rounded-lg shadow-xl py-1 min-w-40 z-50"
        :style="{ top: `${position.y}px`, left: `${position.x}px` }"
        @click.stop>
        <div v-for="(item, index) in items" :key="index">
          <div v-if="item.separator" class="border-t border-white/5 my-1"></div>
          <button
            v-else
            @click="handleClick(item)"
            :disabled="item.disabled"
            class="w-full px-3 py-1.5 text-left text-sm text-white/70 hover:bg-white/10 hover:text-white flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <span
              v-if="item.icon"
              class="w-4 h-4 flex items-center justify-center text-white/50"
              v-html="item.icon"></span>
            <span v-else class="w-4"></span>
            <span>{{ item.label }}</span>
            <span v-if="item.shortcut" class="ml-auto text-xs text-white/30">{{
              item.shortcut
            }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from "vue";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 }),
  },
  items: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["close", "select"]);

const menuRef = ref(null);

// Adjust position if menu goes off screen
watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      await nextTick();
      if (menuRef.value) {
        const rect = menuRef.value.getBoundingClientRect();
        const newPos = { ...props.position };

        if (rect.right > window.innerWidth) {
          newPos.x = window.innerWidth - rect.width - 10;
        }
        if (rect.bottom > window.innerHeight) {
          newPos.y = window.innerHeight - rect.height - 10;
        }

        if (newPos.x !== props.position.x || newPos.y !== props.position.y) {
          menuRef.value.style.left = `${newPos.x}px`;
          menuRef.value.style.top = `${newPos.y}px`;
        }
      }
    }
  }
);

function close() {
  emit("close");
}

function handleClick(item) {
  if (!item.disabled && item.action) {
    item.action();
  }
  close();
}
</script>
