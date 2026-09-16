# CFA Institute Equity Valuation & Stock Analysis Framework

## 1. Fundamental Equity Valuation Methods

### A. Discounted Cash Flow (DCF) Valuation
The DCF model calculates the intrinsic value of a firm based on the present value of its future free cash flows discounted at the Weighted Average Cost of Capital (WACC).

$$\text{Enterprise Value (EV)} = \sum_{t=1}^{N} \frac{\text{FCFF}_t}{(1 + \text{WACC})^t} + \frac{\text{Terminal Value}}{(1 + \text{WACC})^N}$$

- **Free Cash Flow to Firm (FCFF):** EBIT \times (1 - t) + \text{Depreciation} - \text{CapEx} - \Delta \text{NWC}
- **Terminal Value (Gordon Growth Model):** $\text{TV} = \frac{\text{FCFF}_{N+1}}{\text{WACC} - g}$ where $g$ is the perpetual growth rate.

### B. Relative Valuation (Multiples Approach)
1. **Price-to-Earnings (P/E):**
   - **Forward P/E:** $\frac{\text{Current Price}}{\text{Estimated Next 12M EPS}}$
   - Benchmark: FPT current forward P/E is 22.0x vs 5-year historical average of 18.5x.
2. **Price-to-Book (P/B):**
   - Ideal for financial institutions (banks, insurance companies like Vietcombank VCB, MBBank MBB).
   - Relationship with ROE: $\text{Justified P/B} = \frac{\text{ROE} - g}{\text{r} - g}$
3. **EV/EBITDA:**
   - Capital structure-neutral multiple used for capital-intensive sectors (e.g., Hoa Phat Group HPG steel manufacturing).

## 2. Technical Analysis & Trading Indicators

### A. Moving Averages (MA)
- **Golden Cross:** 50-day Simple Moving Average (SMA) crosses above 200-day SMA -> Strong bullish trend confirmation.
- **Death Cross:** 50-day SMA crosses below 200-day SMA -> Bearish trend signal.

### B. Moving Average Convergence Divergence (MACD)
- **MACD Line:** 12-period EMA - 26-period EMA.
- **Signal Line:** 9-period EMA of MACD Line.
- **Bullish Crossover:** MACD line crosses above Signal line below zero.

### C. Financial Risk Metrics
- **Altman Z-Score for Bankruptcy Risk:**
  $$Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$$
  - $Z > 2.99$: Safe Zone (Low default risk).
  - $1.81 < Z < 2.99$: Grey Zone.
  - $Z < 1.81$: Distress Zone.
