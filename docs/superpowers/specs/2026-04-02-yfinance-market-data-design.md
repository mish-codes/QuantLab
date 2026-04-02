# Task 5: yfinance — Fetching & Wrangling Market Data — Design Spec

**Date:** 2026-04-02
**Exercise:** `exercises/05-yfinance/`
**Concept:** yfinance for historical prices, pandas for data wrangling, numpy for returns computation. Data quality handling (NaN, gaps, leading nulls).

---

## Functions

### fetch_closing_prices
| | |
|--|--|
| **Signature** | `def fetch_closing_prices(tickers: list[str], period: str = "1y") -> pd.DataFrame` |
| **Purpose** | Download closing prices from Yahoo Finance |
| **Returns** | DataFrame with date index, one column per ticker |
| **Errors** | Raises `ValueError` if no data returned |
| **Notes** | Handles yfinance MultiIndex columns for multiple tickers |

### validate_data
| | |
|--|--|
| **Signature** | `def validate_data(prices: pd.DataFrame) -> pd.DataFrame` |
| **Purpose** | Clean raw price data for analysis |
| **Steps** | 1. Drop all-NaN rows 2. Drop leading rows with any NaN 3. Forward-fill remaining gaps |
| **Returns** | Cleaned DataFrame with no NaN values |

### compute_returns
| | |
|--|--|
| **Signature** | `def compute_returns(prices: pd.DataFrame) -> np.ndarray` |
| **Purpose** | Convert price DataFrame to daily percentage returns |
| **Returns** | `(n_days-1, n_tickers)` numpy array of daily returns |
| **Notes** | Uses `np.diff` for computation, `nan_to_num` for safety |

## Tests (7 total)

### TestFetchClosingPrices (2 tests)
1. `test_returns_dataframe` — mock yf.download, verify returns DataFrame with correct columns
2. `test_empty_data_raises` — mock empty return, verify ValueError with "No data"

### TestValidateData (2 tests)
3. `test_fills_nan_forward` — DataFrame with NaN gap, verify no NaN after validation
4. `test_drops_leading_nans` — DataFrame with leading NaN, verify rows dropped

### TestComputeReturns (3 tests)
5. `test_shape` — 5 prices → 4 returns, 2 tickers → shape (4, 2)
6. `test_no_nans` — verify no NaN in output
7. `test_returns_are_percentages` — verify (105-100)/100 = 0.05

## Test Fixtures
- `mock_prices` — 10 business days, 2 tickers, includes NaN (realistic)
- `clean_prices` — 5 business days, 2 tickers, no NaN (for returns tests)

## File Structure

```
exercises/05-yfinance/
├── pyproject.toml              # yfinance, numpy, pandas, pytest
├── src/
│   └── market_data.py          # fetch_closing_prices, validate_data, compute_returns
└── tests/
    └── test_market_data.py     # 7 tests across 3 test classes
```

## TDD Flow

1. Create pyproject.toml
2. Write failing tests (7 tests)
3. Run tests — verify they fail (ModuleNotFoundError)
4. Implement market_data.py
5. Run tests — verify all 7 pass
6. Commit to quant_lab (working branch)
7. Teaching conversation (yfinance, data quality concepts)
8. Write blog post to finbytes_git
9. Commit blog post (working → master via merge)
