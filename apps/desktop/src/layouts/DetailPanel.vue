<template>
  <aside class="detail-panel">
    <div class="detail-root">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>当前页面摘要</strong>
            <div class="subtle">用于承接页面说明、宿主状态与上下文提示。</div>
          </div>
          <span class="status-chip info">详情区</span>
        </div>
        <div class="detail-list">
          <div class="detail-item">
            <span class="subtle">页面</span>
            <strong>{{ currentTitle }}</strong>
          </div>
          <div class="detail-item detail-item--stacked">
            <span class="subtle">说明</span>
            <strong>{{ currentSummary }}</strong>
          </div>
          <div class="detail-item">
            <span class="subtle">宿主</span>
            <strong>{{ hostMode }}</strong>
          </div>
          <div class="detail-item">
            <span class="subtle">Runtime</span>
            <strong>{{ runtimeEndpoint }}</strong>
          </div>
        </div>
      </section>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { loadHostShellInfo } from '../modules/host/hostCommands';

const route = useRoute();
const hostMode = ref('正在读取...');
const runtimeEndpoint = ref('正在读取...');

const currentTitle = computed(() => String(route.meta.title || '概览看板'));
const currentSummary = computed(() => String(route.meta.summary || '当前页面暂无额外说明。'));

async function loadHostSummary(): Promise<void> {
  const info = await loadHostShellInfo();
  hostMode.value = `${info.runtimeLaunchMode} / ${info.runtimeStatus}`;
  runtimeEndpoint.value = info.runtimeEndpoint;
}

onMounted(async () => {
  await loadHostSummary();
});

watch(
  () => route.fullPath,
  async () => {
    await loadHostSummary();
  },
);
</script>
