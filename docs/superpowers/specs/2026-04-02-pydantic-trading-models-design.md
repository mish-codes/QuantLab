# Task 2: Pydantic Models for Trading Data — Design Spec

**Date:** 2026-04-02
**Exercise:** `exercises/02-pydantic/`
**Concept:** Data validation and serialization with Pydantic v2, applied to financial entities.

---

## Models

### Trade
A single trade event.

| Field | Type | Constraints |
|-------|------|-------------|
| ticker | str | min_length=1, max_length=10, auto-uppercased via field_validator |
| side | Literal["buy", "sell"] | only buy or sell accepted |
| quantity | int | gt=0 |
| price | float | gt=0 |
| trade_date | date | cannot be in the future (field_validator) |
| notional | float | computed_field: quantity * price |

### Position
Aggregates trades for a single ticker.

| Field | Type | Notes |
|-------|------|-------|
| ticker | str | the ticker symbol |
| trades | list[Trade] | nested model list |
| net_quantity | int | computed_field: sum of buys minus sells |
| avg_price | float | computed_field: weighted avg of buy prices |

### PortfolioRequest
API request for portfolio analysis (used in Task 3: FastAPI).

| Field | Type | Constraints |
|-------|------|-------------|
| tickers | list[str] | min_length=1, max_length=10 |
| weights | list[float] | min_length=1, max_length=10 |
| period | str | default="1y", regex pattern `^\d+(d|mo|y)$` |
| confidence | float | default=0.95, ge=0.9, le=0.99 |

**Model validator:** tickers and weights must have same length; weights must sum to 1.0 (within 0.01 tolerance).

## Pydantic Features Covered

- `field_validator` — per-field transformation/validation (uppercase ticker, reject future dates)
- `model_validator` — cross-field validation (weights sum, length matching)
- `computed_field` — derived values (notional, net_quantity, avg_price)
- `Literal` — constrained string values (buy/sell)
- `Field()` — gt, ge, le, min_length, max_length, default, pattern
- `model_dump()` / `model_validate_json()` — serialization and deserialization

## Tests (12 total)

### TestTrade (7 tests)
1. `test_valid_trade` — creates Trade, checks ticker and computed notional
2. `test_ticker_uppercased` — lowercase input auto-uppercased
3. `test_invalid_side_rejected` — "hold" raises ValidationError
4. `test_negative_quantity_rejected` — negative quantity raises ValidationError
5. `test_future_date_rejected` — future date raises ValidationError
6. `test_serialization_roundtrip` — model_dump then reconstruct, assert equal
7. `test_from_json` — model_validate_json from JSON string

### TestPosition (2 tests)
8. `test_position_from_trades` — two buys, check net_quantity and avg_price
9. `test_mixed_buy_sell` — buy + sell, check net_quantity

### TestPortfolioRequest (2 tests)
10. `test_valid_request` — valid tickers/weights
11. `test_weights_must_sum_to_one` — bad weights raise ValidationError with "sum to 1"
12. `test_lengths_must_match` — mismatched lengths raise ValidationError with "length"

## File Structure

```
exercises/02-pydantic/
├── pyproject.toml          # pydantic>=2.7.0, pytest>=8.0.0
├── src/
│   └── trade_models.py     # Trade, Position, PortfolioRequest
└── tests/
    └── test_trade_models.py # 11 tests
```

## TDD Flow

1. Create pyproject.toml
2. Write failing tests
3. Run tests — verify ModuleNotFoundError
4. Implement trade_models.py
5. Run tests — verify all 12 pass
6. Commit to quant_lab (working branch)
7. Teaching conversation (Pydantic v2 concepts)
8. Write blog post to finbytes_git
9. Commit blog post (working → master via PR)