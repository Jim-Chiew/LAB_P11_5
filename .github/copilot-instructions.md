# Copilot Instructions for LAB_P11_5

## Project Overview
This is an INF1002 Python project for stock trend analysis and visualization. The main application is a Dash web app that lets users view stock data, trends, and indicators for a selected ticker and date range.

## Architecture & Key Files
- `main.py`: Entry point. Dash app UI, callbacks, and data flow. Integrates all modules.
- `yfinance_interface.py`: Fetches stock data using `yfinance.download`. Returns a pandas DataFrame with columns like Date, Open, High, Low, Close, ticker.
- `calculations.py`: Core analytics. Implements SMA calculation, daily returns, and multiple profit calculation algorithms (`max_profit`, `max_profitv2`, `max_profitv3`). Also includes price run counting.
- `plots_interface.py`: Visualization logic using Plotly. Generates multi-panel figures for price, SMA, daily returns, candlestick, and indicator panels. Relies on calculation functions for data preparation.

## Data Flow
- User input (ticker, date range, SMA window) → Dash callback in `main.py`
- Data fetched via `get_stock_data` (from `yfinance_interface.py`)
- Calculations performed (SMA, returns, profit, price runs)
- Visualizations generated (line plot, indicators)
- Results displayed in Dash app

## Patterns & Conventions
- All data manipulations use pandas DataFrames.
- Visualization uses Plotly's `make_subplots`, `Scatter`, `Bar`, `Candlestick`, and `Indicator`.
- SMA window is user-configurable via UI slider.
- Profit calculation returns buy/sell dates for annotation in plots.
- Price run statistics (upward/downward streaks) are shown as indicators.
- All modules are imported directly; no package structure.
- No explicit test or build scripts; run the app via `python main.py`.

## External Dependencies
- `dash` (for web UI)
- `plotly` (for plotting)
- `yfinance` (for stock data)
- `pandas` (for data manipulation)

## Example Workflow
1. Run `python main.py` to start the Dash app.
2. Enter ticker, date range, and SMA window in the UI.
3. App fetches data, computes analytics, and displays interactive plots.

## Integration Points
- All cross-module calls are function-based (no classes).
- Data is passed as DataFrames between modules.
- UI events trigger data fetch and plot updates via Dash callbacks.

## Tips for AI Agents
- Use the existing function signatures for analytics and plotting.
- When adding new analytics, follow the DataFrame input/output pattern.
- For new visualizations, use Plotly and add to `plots_interface.py`.
- For new data sources, extend `yfinance_interface.py`.
- Keep UI logic in `main.py`.

## References
- See `main.py` for app structure and callback logic.
- See `calculations.py` for analytics algorithms.
- See `plots_interface.py` for visualization patterns.
- See `yfinance_interface.py` for data fetching.

---

If any section is unclear or missing, please provide feedback for further refinement.
