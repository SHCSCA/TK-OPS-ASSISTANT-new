<template>
  <footer class="status-bar" :class="{ 'status-bar--minimum': shell.isMinimumMode }">
    <div class="status-bar__group status-bar__left">
      <span v-for="chip in shell.statusLeftChips" :key="chip" class="status-text">{{ chip }}</span>
    </div>
    <div class="status-bar__group status-bar__right">
      <span
        v-for="chip in shell.statusRightChips"
        :key="`${chip.text}:${chip.tone}`"
        class="status-chip"
        :class="chip.tone"
      >
        {{ chip.text }}
      </span>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useShellStore } from '../modules/shell/useShellStore';

const shell = useShellStore();
</script>
