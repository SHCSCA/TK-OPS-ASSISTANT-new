<template>
  <footer class="status-bar">
    <div class="status-bar__group status-bar__left">
      <span class="status-text">{{ runtimeLabel }}</span>
      <span class="status-text">页面：{{ currentTitle }}</span>
    </div>
    <div class="status-bar__group status-bar__right">
      <span class="status-text">版本：{{ runtimeVersion }}</span>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import { createRuntimeSocket } from '../modules/runtime/runtimeSocket';

const route = useRoute();
const runtimeVersion = ref('等待握手');
const runtimeLabel = ref('桌面宿主已就绪');

const currentTitle = computed(() => String(route.meta.title || '概览看板'));

const socket = createRuntimeSocket((data) => {
  const payload = data as { type?: string; payload?: { status?: string; version?: string } };
  if (payload.type !== 'runtime.status') {
    return;
  }
  runtimeLabel.value = `Runtime：${payload.payload?.status || 'unknown'}`;
  runtimeVersion.value = payload.payload?.version || 'unknown';
});

onMounted(() => {
  socket.connect();
});

onBeforeUnmount(() => {
  socket.disconnect();
});
</script>
