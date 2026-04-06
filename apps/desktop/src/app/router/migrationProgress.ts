import { computed } from 'vue';

import type { ShellRouteManifestItem } from './routeManifest';
import { shellNavGroups, shellRouteManifest } from './routeManifest';

export interface MigrationProgressSnapshot {
  implementedCount: number;
  placeholderCount: number;
  totalCount: number;
  completionPercent: number;
  stageTitle: string;
  stageDescription: string;
  nextPendingRoute: ShellRouteManifestItem | null;
}

function resolveOrderedManifest(): ShellRouteManifestItem[] {
  const navOrderMap = new Map<string, number>();
  shellNavGroups.forEach((group) => {
    navOrderMap.set(group.key, group.order);
  });

  return shellRouteManifest
    .slice()
    .sort((left, right) => {
      const leftGroupOrder = navOrderMap.get(left.navGroup) ?? Number.MAX_SAFE_INTEGER;
      const rightGroupOrder = navOrderMap.get(right.navGroup) ?? Number.MAX_SAFE_INTEGER;
      if (leftGroupOrder !== rightGroupOrder) {
        return leftGroupOrder - rightGroupOrder;
      }
      return left.navOrder - right.navOrder;
    });
}

function resolveStageTitle(implementedCount: number, totalCount: number): string {
  if (implementedCount <= 0) {
    return '迁移准备阶段';
  }
  if (implementedCount < 8) {
    return '旧课程 1:1 迁移阶段';
  }
  if (implementedCount < totalCount) {
    return '迁移推进阶段';
  }
  return '迁移收口阶段';
}

export function getMigrationProgressSnapshot(): MigrationProgressSnapshot {
  const orderedManifest = resolveOrderedManifest();
  const totalCount = orderedManifest.length;
  const implementedCount = orderedManifest.filter((item) => item.migrationStatus === 'implemented').length;
  const placeholderCount = totalCount - implementedCount;
  const completionPercent = totalCount > 0 ? Math.round((implementedCount / totalCount) * 100) : 0;
  const nextPendingRoute = orderedManifest.find((item) => item.migrationStatus === 'placeholder') || null;
  const stageTitle = resolveStageTitle(implementedCount, totalCount);
  const nextPendingLabel = nextPendingRoute?.title || '无（全部完成）';
  const stageDescription = `已迁移 ${implementedCount}/${totalCount}（${completionPercent}%），下一优先：${nextPendingLabel}。`;

  return {
    implementedCount,
    placeholderCount,
    totalCount,
    completionPercent,
    stageTitle,
    stageDescription,
    nextPendingRoute,
  };
}

export function useMigrationProgress() {
  const snapshot = computed(() => getMigrationProgressSnapshot());
  return {
    snapshot,
  };
}
