#!/usr/bin/env python3
"""Console-based MVP for TK-OPS Desktop (CLI-only).

This lightweight CLI app demonstrates the core flows of the MVP:
- Product selection (选品)
- Copy generation (文案) via AI when available, otherwise a fallback
- Simple automation workflow visualization (运营自动化)

Usage: python desktop_app/cli_mvp.py
"""
import os
import textwrap
from dataclasses import dataclass
from typing import List, Optional

try:
    import openai  # type: ignore
except Exception:
    openai = None  # fallback


@dataclass
class Product:
    id: int
    title: str
    description: str
    price: float
    category: str = "General"


def sample_products() -> List[Product]:
    return [
        Product(101, "智能手表 ProX", "高性能健康监测、24h续航", 199.0, "穿戴"),
        Product(102, "便携充电宝 20000mAh", "超轻薄、双向快充", 59.9, "配件"),
        Product(103, "蓝牙耳机 T-Pulse", "降噪、长续航", 129.0, "音频"),
    ]


def ai_complete(prompt: str, max_tokens: int = 256) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if openai is None or not key:
        return f"[AI 提示] 未配置 OpenAI API，使用回退文本。\nPrompt: {prompt}"
    try:
        openai.api_key = key
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        return f"[AI 错误] {e}"


def main():
    print("TK-OPS TikTok Shop Desktop MVP (CLI 模拟版)")
    print("适用于快速验证选品、文案生成与运营自动化的端到端数据流。")
    products = sample_products()

    while True:
        print("\n可选商品：")
        for i, p in enumerate(products, start=1):
            print(f"  {i}. {p.title} - {p.price:.2f}元 [{p.category}] {p.description}")
        choice = input("请选择商品 (1-{}), 或输入 q 退出: ".format(len(products))).strip()
        if choice.lower() == 'q':
            print("退出 MVP CLI。")
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(products)):
            print("输入无效，请重试。")
            continue
        idx = int(choice) - 1
        product = products[idx]
        print(f"选中: {product.title}\n")

        # 文案生成
        print("生成文案：")
        tone = input("选择语气（专业/亲切/幽默/正式）：").strip() or "专业"
        length = input("设定字数上限（如 200）：").strip()
        max_tokens = int(length) if length.isdigit() else 200
        prompt = f"为商品 '{product.title}' 生成吸引人的标题与描述，语气偏向 '{tone}', 控制在约 {max_tokens} 字。"
        print("正在请求 AI 文案...")
        ai_result = ai_complete(prompt, max_tokens=max_tokens)
        print("[AI 输出]\n" + ai_result)

        # 简易运营自动化演示
        print("\n运营自动化示例：将该文案作为某推广活动的草案，生成一个简单的发布计划...")
        print("阶段 1/3: 生成草案 → 阶段 2/3: 审核 → 阶段 3/3: 发布计划")
        input("按 Enter 继续到下一个商品...")

        print("已处理商品：", product.title)

if __name__ == '__main__':
    main()
