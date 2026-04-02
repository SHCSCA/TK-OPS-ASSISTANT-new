<template>
  <div class="app-shell">
    <TitleBar />
    <Sidebar />
    <PageHost />
    <DetailPanel />
    <StatusBar />
  </div>
</template>

<script setup lang="ts">
import DetailPanel from './DetailPanel.vue';
import PageHost from './PageHost.vue';
import Sidebar from './Sidebar.vue';
import StatusBar from './StatusBar.vue';
import TitleBar from './TitleBar.vue';
</script>
