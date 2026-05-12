---
name: trading-bot-skill
description: "開發與維護整個 trading-bot 專案（資料抓取、回測、繪圖與 Pylance 驗證）"
---

# 💹 Trading Bot 專案開發 Skill

本 Skill 用於整個 trading-bot 專案的開發與維護，涵蓋：
- BTC 歷史資料抓取
- 圖表繪製
- Backtrader 回測策略
- VS Code / Pylance 型別問題處理

## 🎯 概述

目前專案主要由兩個可執行腳本構成：
- `src/trading_bot/momentum_strategy.py`：動量策略回測與績效圖
- `src/trading_bot/btc_2025_chart.py`：2025 年 BTC 價格圖

## 📦 核心組件

### 回測模組（momentum_strategy.py）
- 動量定義：`momentum = close(t) - close(t-n)`
- 預設動量期間：20 天
- 買入信號：動量 > 0
- 賣出信號：動量 < 0
- 初始資金：100,000 USD
- 交易手續費：0.1%
- 輸出圖檔：`output/momentum_backtest_results.png`

### 視覺化模組（btc_2025_chart.py）
- 抓取 2025 年 BTC-USD 日線資料
- 顯示收盤價趨勢圖
- 用於快速資料檢查與手動比對

### 共同依賴
- `yfinance`
- `matplotlib`
- `backtrader`

## 🚀 使用方法

### 快速開始
```bash
# 回測腳本
poetry run python src/trading_bot/momentum_strategy.py

# 僅查看 2025 價格圖
poetry run python src/trading_bot/btc_2025_chart.py
```

### 存檔輸出
```bash
poetry run python src/trading_bot/momentum_strategy.py --save
```

## ✅ 開發檢查清單

實現功能時：
1. ✅ 在對應模組修改代碼（策略或繪圖）
2. ✅ 檢查 Pylance 錯誤：`Ctrl+Shift+M`（或 View → Problems）
3. ✅ 使用 `# type: ignore[error-code]` 修正第三方庫錯誤
4. ✅ 驗證至少一個腳本能正常執行
5. ✅ 若改到策略邏輯，確認交易輸出與最終投組價值
6. ✅ 若改到繪圖，確認圖表可顯示或可輸出

## 🧭 代碼風格約定（本專案）

### 方法設計
- 優先使用一般 instance method
- 避免使用 `@staticmethod` / `@classmethod`，除非有明確需求

### 註解規則
- 不要保留緊跟在 class / method 後面的說明註解或 docstring
- 允許並保留方法內部的流程註解（例如資料轉換、繪圖步驟）

## 🛠️ 常見 Pylance 問題及解決方案

### 問題：backtrader、pandas、yfinance 缺少庫存根
```python
import backtrader as bt  # type: ignore
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore
```

### 問題：無法存取 params.momentum_period
```python
self.momentum = self.data.close - self.data.close(-self.params.momentum_period)  # type: ignore[attr-defined]
```

### 問題：FuncFormatter 未從 matplotlib.pyplot 匯出
```python
from matplotlib.ticker import FuncFormatter
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))
```

### 問題：cerebro 參數類型問題
```python
data = bt.feeds.PandasData(dataname=data_df)  # type: ignore
```

## 🔧 擴展策略

### 修改動量期間
```python
cerebro.addstrategy(MomentumStrategy, momentum_period=30)  # 從 20 改為 30
```

### 添加止損
修改 `next()` 方法添加尾隨止損條件

### 不同的資產
將 `yf.download()` 中的 `"BTC-USD"` 替換為其他股票代碼

### 風險管理
調整 `cerebro.broker.setcash()` 和 `cerebro.broker.setcommission()` 值

## 🧪 測試及驗證

始終驗證：
- ✅ Problems 面板中沒有 Pylance 錯誤
- ✅ 受影響腳本運行無異常
- ✅ 回測腳本可產生交易與最終資產輸出
- ✅ 圖表腳本可顯示圖或成功輸出 PNG

## 📖 相關文件
- 回測策略：`src/trading_bot/momentum_strategy.py`
- 價格圖工具：`src/trading_bot/btc_2025_chart.py`
- 套件設定：`pyproject.toml`
- 專案輸出目錄：`output/`

---

**最後更新**：2026-05-12
**狀態**：✅ 專案級 Skill（已套用）
