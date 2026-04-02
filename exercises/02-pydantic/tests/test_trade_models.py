import pytest
from datetime import date
from pydantic import ValidationError
from trade_models import Trade, Position, PortfolioRequest


class TestTrade:
    def test_valid_trade(self):
        t = Trade(
            ticker="AAPL",
            side="buy",
            quantity=100,
            price=150.25,
            trade_date=date(2026, 4, 1),
        )
        assert t.ticker == "AAPL"
        assert t.notional == 15025.0  # computed field

    def test_ticker_uppercased(self):
        t = Trade(
            ticker="aapl",
            side="buy",
            quantity=100,
            price=150.0,
            trade_date=date(2026, 4, 1),
        )
        assert t.ticker == "AAPL"

    def test_invalid_side_rejected(self):
        with pytest.raises(ValidationError):
            Trade(
                ticker="AAPL",
                side="hold",
                quantity=100,
                price=150.0,
                trade_date=date(2026, 4, 1),
            )

    def test_negative_quantity_rejected(self):
        with pytest.raises(ValidationError):
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=-10,
                price=150.0,
                trade_date=date(2026, 4, 1),
            )

    def test_future_date_rejected(self):
        with pytest.raises(ValidationError):
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=100,
                price=150.0,
                trade_date=date(2030, 1, 1),
            )

    def test_serialization_roundtrip(self):
        t = Trade(
            ticker="AAPL",
            side="buy",
            quantity=100,
            price=150.25,
            trade_date=date(2026, 4, 1),
        )
        data = t.model_dump()
        t2 = Trade(**data)
        assert t == t2

    def test_from_json(self):
        json_str = '{"ticker":"AAPL","side":"buy","quantity":100,"price":150.25,"trade_date":"2026-04-01"}'
        t = Trade.model_validate_json(json_str)
        assert t.ticker == "AAPL"
        assert t.notional == 15025.0


class TestPosition:
    def test_position_from_trades(self):
        trades = [
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=100,
                price=150.0,
                trade_date=date(2026, 3, 1),
            ),
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=50,
                price=155.0,
                trade_date=date(2026, 3, 15),
            ),
        ]
        pos = Position(ticker="AAPL", trades=trades)
        assert pos.net_quantity == 150
        assert pos.avg_price == pytest.approx(151.6667, rel=1e-3)

    def test_mixed_buy_sell(self):
        trades = [
            Trade(
                ticker="MSFT",
                side="buy",
                quantity=200,
                price=300.0,
                trade_date=date(2026, 3, 1),
            ),
            Trade(
                ticker="MSFT",
                side="sell",
                quantity=50,
                price=310.0,
                trade_date=date(2026, 3, 10),
            ),
        ]
        pos = Position(ticker="MSFT", trades=trades)
        assert pos.net_quantity == 150


class TestPortfolioRequest:
    def test_valid_request(self):
        req = PortfolioRequest(
            tickers=["AAPL", "MSFT", "GOOG"],
            weights=[0.4, 0.35, 0.25],
        )
        assert len(req.tickers) == 3

    def test_weights_must_sum_to_one(self):
        with pytest.raises(ValidationError, match="sum to 1"):
            PortfolioRequest(tickers=["AAPL", "MSFT"], weights=[0.5, 0.3])

    def test_lengths_must_match(self):
        with pytest.raises(ValidationError, match="length"):
            PortfolioRequest(tickers=["AAPL", "MSFT"], weights=[1.0])
