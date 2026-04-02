<template>
  <header class="title-bar">
    <div class="title-bar__cluster">
      <div class="logo-mark">
        <span class="shell-icon shell-icon--strong">TK</span>
      </div>
      <div class="brand-stack">
        <strong>TK-OPS</strong>
        <p class="eyebrow">{{ currentEyebrow }}</p>
      </div>
      <div class="search-bar shell-search-bar">
        <span class="shell-icon">搜</span>
        <input :value="searchPlaceholder" readonly />
      </div>
    </div>
    <div class="title-bar__actions">
      <span class="status-chip" :class="runtimeChipClass">{{ runtimeLabel }}</span>
      <span class="subtle title-bar__meta">{{ hostMeta }}</span>
      <button type="button" class="secondary-button" @click="handleRestartRuntime">
        重启 Runtime
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { loadHostShellInfo, restartRuntimeFromHost } from '../modules/host/hostCommands';

type RuntimeChipState = 'success' | 'warning' | 'info';

const route = useRoute();
const runtimeLabel = ref('桌面宿主');
const runtimeChipClass = ref<RuntimeChipState>('info');
const hostMeta = ref('正在读取宿主状态...');

const currentEyebrow = computed(() => String(route.meta.eyebrow || '桌面工作台'));
const searchPlaceholder = computed(() => `当前页面：${String(route.meta.title || '概览看板')}`);

function normalizeRuntimeStatus(status: string): { label: string; tone: RuntimeChipState } {
  if (status.includes('running') || status === 'ready' || status === 'reachable') {
    return { label: 'Runtime 正常', tone: 'success' };
  }
  if (status.includes('waiting') || status.includes('starting') || status.includes('browser')) {
    return { label: 'Runtime 连接中', tone: 'warning' };
  }
  return { label: 'Runtime 状态异常', tone: 'info' };
}

async function refreshHostMeta(): Promise<void> {
  const info = await loadHostShellInfo();
  const runtime = normalizeRuntimeStatus(info.runtimeStatus);
  runtimeLabel.value = runtime.label;
  runtimeChipClass.value = runtime.tone;
  hostMeta.value = `宿主 ${info.appVersion} / ${info.runtimeLaunchMode} / ${info.runtimeEndpoint}`;
}

async function handleRestartRuntime(): Promise<void> {
  hostMeta.value = '正在请求宿主重启 runtime...';
  await restartRuntimeFromHost();
  await refreshHostMeta();
}

onMounted(async () => {
  await refreshHostMeta();
});

watch(
  () => route.fullPath,
  async () => {
    await refreshHostMeta();
  },
);
</script>
