/**
 * 素材中心 API 客户端
 * @description 素材管理相关的 HTTP API 调用
 */

import { runtimeApi } from '../runtime/runtimeApi';
import type {
  AssetItem,
  AssetStats,
  AssetListQuery,
  AssetCreatePayload,
  AssetUpdatePayload,
} from './assetCenter.types';

/**
 * 素材 API 客户端
 */
export const assetClient = {
  /**
   * 获取素材列表
   * @param query - 查询参数
   */
  async list(query: AssetListQuery = {}): Promise<AssetItem[]> {
    const params: Record<string, string> = {};
    if (query.assetType) {
      params.asset_type = query.assetType;
    }
    if (query.query) {
      params.query = query.query;
    }

    const response = await runtimeApi.listAssets(params);
    return response.items || [];
  },

  /**
   * 获取素材统计
   */
  async getStats(): Promise<AssetStats> {
    return await runtimeApi.getAssetStats();
  },

  /**
   * 获取单个素材
   */
  async get(id: number): Promise<AssetItem | null> {
    return await runtimeApi.getAsset(id);
  },

  /**
   * 创建素材
   */
  async create(payload: AssetCreatePayload): Promise<AssetItem> {
    return await runtimeApi.createAsset({
      filename: payload.filename,
      asset_type: payload.assetType,
      file_path: payload.filePath,
      tags: payload.tags,
      account_id: payload.accountId,
    });
  },

  /**
   * 更新素材
   */
  async update(id: number, payload: AssetUpdatePayload): Promise<AssetItem> {
    return await runtimeApi.updateAsset(id, {
      filename: payload.filename,
      asset_type: payload.assetType,
      file_path: payload.filePath,
      tags: payload.tags,
      account_id: payload.accountId,
    });
  },

  /**
   * 删除素材
   */
  async delete(id: number): Promise<{ deleted: boolean }> {
    return await runtimeApi.deleteAsset(id);
  },
};
