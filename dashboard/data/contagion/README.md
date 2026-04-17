# Contagion events parquet

`events.parquet` is a committed snapshot of market data for the Global
Contagion dashboard. Regenerate with:

```bash
python scripts/fetch_contagion_data.py
```

## Schema

| column | dtype | notes |
|---|---|---|
| date | date | trading day |
| period | string | `2020_us_iran` or `2024_hormuz` |
| ticker | string | yfinance symbol or `FRED:<series_id>` |
| asset_role | string | `epicenter` / `contagion` / `safe_haven` / `energy` / `fear` |
| country | string \| null | ISO-2 for geographic tickers, null for commodities/indices |
| close | float64 | closing price or yield |

## Sources

- yfinance: ETF + futures closing prices
- FRED public CSV endpoints (no API key): long-term government bond yields

## Notes

Israel / Saudi / UAE 10Y yield series are not cleanly available via free
yfinance or FRED, so the ETL substitutes the country ETFs (`EIS`, `KSA`,
`UAE`) as a proxy for sovereign risk. The blog post should document this
substitution.

## Ticker substitutions

Two FRED series were discontinued and had to be substituted:

| Country | Original FRED series | Substitute | Type change |
|---|---|---|---|
| India | `IRLTLT01INM156N` | `INDIRLTLT01STM` | Like-for-like (same yield construct, newer series) |
| Turkey | `IRLTLT01TRM156N` | `TUR` (iShares MSCI Turkey ETF) | Yield → equity price proxy |

The Turkey substitution changes the data type from a bond yield to an equity price.
Rolling correlations against the Middle East index will behave differently for Turkey
than for the FRED yield countries. Document this caveat in the blog post.
