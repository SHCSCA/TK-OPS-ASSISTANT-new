# Backend Driven Analyst And Notification Surfaces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace remaining simulated notification and analyst-page prototype data with backend/database-driven records, and expand development seed data so these pages render real content in tests and in the desktop app.

**Architecture:** Keep the existing runtime shell and route system, but move more shaping logic into Python services and bridge methods so the frontend renders structured results instead of inventing example cards. Seed data remains development-only, idempotent, and rich enough to populate notification, analytics, experiment, report, and workflow surfaces.

**Tech Stack:** Python 3.11+, SQLAlchemy 2.x, Alembic-backed SQLite, PySide6 QWebChannel bridge, vanilla JavaScript, pytest.

---

## 已实施任务概览

1. 通知中心改为后端真实数据驱动
2. analyst 页面新增真实 aggregate surface
3. analytics factory 默认态去 demo 值
4. page loader 改为读取真实 aggregate
5. dev seed 扩展为页面查看级真实样本
6. README、版本号、测试与提交流程同步更新
