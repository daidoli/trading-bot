---
title: "Trading Bot 專案開發工作流程"
description: "自動化的 trading-bot 專案開發流程，包含資料抓取、回測、繪圖與 Pylance 驗證"
---

# 💹 Trading Bot 專案開發工作流程

本指令為整個 trading-bot 專案提供自動化開發與驗證流程。

## 🎯 開發流程

### 第 1 步：實作變更
- 在受影響檔案實作變更
- 策略邏輯主要在 `src/trading_bot/momentum_strategy.py`
- 價格圖工具主要在 `src/trading_bot/btc_2025_chart.py`

### 第 2 步：檢查 Pylance 錯誤（必須）
**每次實作都必須進行 Pylance 驗證：**

```bash
# 在 VS Code 中查看 Problems 面板
Ctrl+Shift+M (Mac 上按 Cmd+Shift+M)
```

**如果發現錯誤：**
1. 對第三方庫使用 `# type: ignore[error-code]`
2. 盡可能添加適當的類型提示
3. 運行 `get_errors` 驗證所有錯誤已清除

### 第 3 步：驗證執行
```bash
# 回測腳本
poetry run python src/trading_bot/momentum_strategy.py

# 價格圖腳本
poetry run python src/trading_bot/btc_2025_chart.py
```

**成功指標：**
- ✅ 無 Python 錯誤或異常
- ✅ 若改到回測，控制台有交易輸出與最終投資組合價值
- ✅ 若改到繪圖，圖表可顯示或可輸出 PNG

### 第 4 步：檢查輸出
- 檢查最終投資組合價值和總收益（回測）
- 驗證圖表已生成或可正常顯示（繪圖）
- 審查策略信號與輸出是否合理

---

## 📋 Pylance 錯誤模式及解決方案

### 模式 1：缺少庫存根
**錯誤：** `Library stubs not installed for "X"`
**解決方案：**
```python
import backtrader as bt  # type: ignore
import pandas as pd  # type: ignore
```

### 模式 2：訪問動態屬性（backtrader params）
**錯誤：** `無法存取類別 "tuple[tuple[str, int]]" 的屬性 "momentum_period"`
**解決方案：**
```python
self.momentum = self.data.close - self.data.close(-self.params.momentum_period)  # type: ignore[attr-defined]
```

### 模式 3：錯誤的導入路徑
**錯誤：** `"FuncFormatter" 未從模組 "matplotlib.pyplot" 匯出`
**解決方案：**
```python
from matplotlib.ticker import FuncFormatter  # 正確的導入方式
```

### 模式 4：第三方庫參數
**錯誤：** `沒有名為 "dataname" 的參數`
**解決方案：**
```python
data = bt.feeds.PandasData(dataname=data_df)  # type: ignore
```

---

## 🔍 代碼品質清單

實作完成前需要檢查：

- [ ] 零個 Pylance 錯誤（在 Problems 面板中驗證）
- [ ] 受影響腳本運行無異常
- [ ] 若改回測：有交易輸出與最終損益
- [ ] 若改繪圖：圖表可顯示或輸出成功
- [ ] 自定義函數添加了類型提示
- [ ] 註解解釋了複雜邏輯
- [ ] 性能指標計算正確

---

## 📂 文件結構

```
trading-bot/
├── .github/
│   └── TRADING_BOT_SKILL.md (Skill 參考)
├── .vscode/
│   └── launch.json (Poetry 執行配置)
├── src/trading_bot/
│   ├── momentum_strategy.py (策略主實作)
│   └── btc_2025_chart.py (數據視覺化)
├── pyproject.toml (依賴：backtrader、yfinance、pandas、matplotlib)
└── momentum_backtest_results.png (輸出圖表)
```

---

## 🚀 快速命令

| 任務 | 命令 |
|------|------|
| 檢查錯誤 | View → Problems (Ctrl+Shift+M) |
| 運行回測 | `poetry run python src/trading_bot/momentum_strategy.py` |
| 運行價格圖 | `poetry run python src/trading_bot/btc_2025_chart.py` |
| 儲存回測圖 | `poetry run python src/trading_bot/momentum_strategy.py --save` |
| 在 VS Code 中運行 | 按 F5（調試模式） |
| 檢查依賴 | `poetry show` |
| 添加依賴 | `poetry add package_name` |

---

## ⚠️ 重要事項

1. **始終驗證 Pylance** 再提交代碼
2. **Type ignore 註解** 應該具體：`# type: ignore[attr-defined]`
3. **測試執行** 確保運行時正確
4. **方法設計** 優先使用一般 instance method
5. **註解規則** 不保留緊跟 class 或 method 後的導言註解，方法內流程註解可保留

---

## 🔧 擴展策略

### 修改動量期間：
```python
cerebro.addstrategy(MomentumStrategy, momentum_period=30)
```

### 添加新指標：
```python
self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
```

### 改進信號邏輯：
修改 `next()` 方法添加額外條件

---

## 📊 專案目標

- **可維護性**：腳本結構清晰、型別錯誤可控
- **可執行性**：核心腳本可在 Poetry 環境下穩定執行
- **可驗證性**：回測與繪圖結果可重現

---

## ✅ Copilot 驗證命令

當您要求 Copilot 協助專案開發時：

1. **"修正動量策略 Pylance 錯誤"** → 運行 `get_errors` 並修正所有類型問題
2. **"添加 [功能] 到回測"** → 修改策略 + 驗證執行 + 檢查 Pylance
3. **"驗證回測腳本"** → 運行回測 + 檢查輸出 + 驗證錯誤
4. **"更新 2025 圖表腳本"** → 修改繪圖 + 運行驗證 + 檢查錯誤

---

## 📖 相關文檔

- Skill 參考：`.github/TRADING_BOT_SKILL.md`
- 項目設置：`README.md`

---

**最後更新**：2026-05-12
**狀態**：✅ 專案級流程（已同步 Skill）

