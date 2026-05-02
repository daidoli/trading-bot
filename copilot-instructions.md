---
title: "動量策略開發工作流程"
description: "自動化的動量交易策略開發工作流程，包含 Pylance 驗證"
---

# 💹 動量策略開發工作流程

本指令為 BTC 動量交易策略開發提供自動化驗證工作流程。

## 🎯 開發流程

### 第 1 步：實作變更
- 修改 `src/trading_bot/momentum_strategy.py` 中的代碼
- 添加策略或視覺化功能

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
poetry run python src/trading_bot/momentum_strategy.py
```

**成功指標：**
- ✅ 無 Python 錯誤或異常
- ✅ 控制台打印交易記錄（BUY/SELL EXECUTED）
- ✅ "Chart saved to momentum_backtest_results.png"
- ✅ 顯示最終投資組合價值

### 第 4 步：檢查輸出
- 檢查最終投資組合價值和總收益
- 驗證圖表已生成
- 審查交易決策的輸出

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
self.params.momentum_period  # type: ignore[attr-defined]
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
- [ ] 代碼運行無異常
- [ ] 回測生成有效交易
- [ ] 輸出顯示利潤/損失指標
- [ ] PNG 圖表文件成功創建
- [ ] 自定義函數添加了類型提示
- [ ] 註解解釋了複雜邏輯
- [ ] 性能指標計算正確

---

## 📂 文件結構

```
trading-bot/
├── .github/
│   └── MOMENTUM_STRATEGY_SKILL.md (Skill 參考)
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
| 運行策略 | `poetry run python src/trading_bot/momentum_strategy.py` |
| 在 VS Code 中運行 | 按 F5（調試模式） |
| 檢查依賴 | `poetry show` |
| 添加依賴 | `poetry add package_name` |

---

## ⚠️ 重要事項

1. **始終驗證 Pylance** 再提交代碼
2. **Type ignore 註解** 應該具體：`# type: ignore[attr-defined]`
3. **測試執行** 確保運行時正確
4. **註解代碼** 解釋動量計算
5. **保存輸出** 用於性能追蹤

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

## 📊 性能目標

- **預期收益**：2024-2025 BTC 數據上 +15-20%
- **交易勝率**：監控利潤/損失比率
- **最大回撤**：審查圖表中的投資組合下降
- **手續費影響**：每筆交易 0.1%

---

## ✅ Copilot 驗證命令

當您要求 Copilot 幫助動量策略時：

1. **"修正動量策略 Pylance 錯誤"** → 運行 `get_errors` 並修正所有類型問題
2. **"添加 [功能] 到動量策略"** → 添加功能 + 驗證 + 檢查 Pylance
3. **"驗證動量策略"** → 運行回測 + 檢查輸出 + 驗證錯誤
4. **"優化動量期間"** → 測試不同期間 + 驗證每一個

---

## 📖 相關文檔

- Skill 參考：`.github/MOMENTUM_STRATEGY_SKILL.md`
- 項目設置：`README.md`

---

**最後更新**：2026-05-02
**策略狀態**：✅ 活躍 & 已驗證

