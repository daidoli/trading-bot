---
name: momentum-strategy-dev
description: "開發和維護動量交易策略，具有自動 Pylance 錯誤檢查功能"
---

# 動量策略開發 Skill

本 Skill 提供了開發和維護動量交易策略的工作流程，包括自動 Pylance 驗證。

## 概述

動量策略實現工作流程：
- 實現基於動量的交易策略：`momentum = price(t) - price(t-n)`
- 使用 backtrader 進行 BTC-USD 數據的回測
- 生成視覺化性能報告

## 核心組件

### 策略實現
- **文件**：`src/trading_bot/momentum_strategy.py`
- **動量期間**：20 天（可配置）
- **買入信號**：正動量 → 買進
- **賣出信號**：負動量 → 賣出
- **資金**：$100,000
- **手續費**：0.1%

### 性能指標
- 追蹤買/賣執行價格
- 計算每筆交易的利潤/損失
- 生成投資組合性能圖表
- 結果保存到 `momentum_backtest_results.png`

## 使用方法

### 快速開始
```bash
# 運行回測
poetry run python src/trading_bot/momentum_strategy.py
```

### 在 VS Code 中
1. 按 **F5** 執行（需要 launch.json 配置 Poetry）
2. 圖表和交易將打印到控制台
3. 性能圖表保存為 PNG

## 開發檢查清單

實現功能時：
1. ✅ 在 `momentum_strategy.py` 中編寫/修改代碼
2. ✅ 檢查 Pylance 錯誤：`Ctrl+Shift+M`（或 View → Problems）
3. ✅ 使用 `# type: ignore[error-code]` 修正第三方庫錯誤
4. ✅ 驗證回測運行：`poetry run python src/trading_bot/momentum_strategy.py`
5. ✅ 檢查交易和投資組合價值輸出
6. ✅ 驗證生成新的性能圖表

## 常見 Pylance 問題及解決方案

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

## 文件及導入

### 核心導入（帶 type: ignore）
- `backtrader` - 回測框架
- `pandas` - 數據操作（展平 yfinance 的多級列）
- `yfinance` - BTC-USD 價格數據獲取
- `matplotlib` - 圖表生成，使用 FuncFormatter 進行貨幣格式化

### 數據流程
1. 獲取 BTC-USD OHLCV 數據（2024-2025）
2. 展平 yfinance 的多級列
3. 創建帶策略的 cerebro 引擎
4. 運行包含手續費的回測
5. 使用 matplotlib 繪製結果

## 擴展策略

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

## 測試及驗證

始終驗證：
- ✅ Problems 面板中沒有 Pylance 錯誤
- ✅ 腳本運行無異常
- ✅ 交易已執行（買/賣控制台輸出）
- ✅ 最終投資組合價值顯示利潤/損失
- ✅ PNG 圖表成功生成

## 相關文件
- 入口腳本：`src/trading_bot/momentum_strategy.py`
- BTC 圖表查看器：`src/trading_bot/btc_2025_chart.py`
- 項目配置：`pyproject.toml`
- VS Code 配置：`.vscode/launch.json`
