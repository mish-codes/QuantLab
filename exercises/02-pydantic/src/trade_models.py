from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field


class Trade(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    side: Literal["buy", "sell"]
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    trade_date: date

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper()

    @field_validator("trade_date")
    @classmethod
    def not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("trade_date cannot be in the future")
        return v

    @computed_field
    @property
    def notional(self) -> float:
        return self.quantity * self.price


class Position(BaseModel):
    ticker: str
    trades: list[Trade]

    @computed_field
    @property
    def net_quantity(self) -> int:
        total = 0
        for t in self.trades:
            total += t.quantity if t.side == "buy" else -t.quantity
        return total

    @computed_field
    @property
    def avg_price(self) -> float:
        buys = [t for t in self.trades if t.side == "buy"]
        if not buys:
            return 0.0
        total_cost = sum(t.quantity * t.price for t in buys)
        total_qty = sum(t.quantity for t in buys)
        return total_cost / total_qty


class PortfolioRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=10)
    weights: list[float] = Field(..., min_length=1, max_length=10)
    period: str = Field(default="1y", pattern=r"^\d+(d|mo|y)$")
    confidence: float = Field(default=0.95, ge=0.9, le=0.99)

    @model_validator(mode="after")
    def validate_portfolio(self):
        if len(self.tickers) != len(self.weights):
            raise ValueError(
                f"tickers length ({len(self.tickers)}) must match "
                f"weights length ({len(self.weights)})"
            )
        if abs(sum(self.weights) - 1.0) > 0.01:
            raise ValueError(
                f"weights must sum to 1.0, got {sum(self.weights):.4f}"
            )
        return self
