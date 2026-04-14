"""Tests for the Rent vs Buy finance module."""

import math

import pandas as pd
import pytest

from lib.rentbuy.finance import (
    calculate_sdlt,
    monthly_mortgage_payment,
    remaining_balance,
)


# ── SDLT — Standard bands (non-first-time-buyer) ────────────────────

SDLT_STANDARD = [
    (   125_000,       0),
    (   250_000,       0),
    (   400_000,    7_500),
    (   500_000,   12_500),
    (   925_000,   33_750),
    ( 1_000_000,   41_250),
    ( 1_500_000,   91_250),
    ( 2_000_000,  151_250),
]


@pytest.mark.parametrize("price,expected", SDLT_STANDARD)
def test_sdlt_standard(price, expected):
    assert calculate_sdlt(price, first_time_buyer=False) == pytest.approx(expected, abs=1)


# ── SDLT — First-time buyer relief ──────────────────────────────────

SDLT_FTB = [
    (   400_000,      0),
    (   425_000,      0),
    (   500_000,  3_750),
    (   625_000, 10_000),
]


@pytest.mark.parametrize("price,expected", SDLT_FTB)
def test_sdlt_first_time_buyer(price, expected):
    assert calculate_sdlt(price, first_time_buyer=True) == pytest.approx(expected, abs=1)


def test_sdlt_ftb_above_cap_uses_standard():
    """Above £625k, first-time buyers pay the same as non-FTB."""
    standard = calculate_sdlt(700_000, first_time_buyer=False)
    ftb = calculate_sdlt(700_000, first_time_buyer=True)
    assert standard == ftb


# ── Mortgage amortization ───────────────────────────────────────────

def test_mortgage_payment_standard_case():
    """£500k loan at 5% for 25 years → monthly payment ≈ £2,923."""
    payment = monthly_mortgage_payment(500_000, 0.05, 25)
    assert 2_920 < payment < 2_930


def test_mortgage_payment_zero_interest():
    """£240k / 240 months = £1,000/month exactly."""
    payment = monthly_mortgage_payment(240_000, 0.0, 20)
    assert abs(payment - 1_000) < 0.01


def test_mortgage_payment_scales_with_principal():
    """Doubling the principal doubles the monthly payment."""
    small = monthly_mortgage_payment(250_000, 0.05, 25)
    big = monthly_mortgage_payment(500_000, 0.05, 25)
    assert abs(big - 2 * small) < 0.01


def test_remaining_balance_at_start_equals_principal():
    assert abs(remaining_balance(500_000, 0.05, 25, 0) - 500_000) < 1


def test_remaining_balance_partial_term():
    """After 120 months on a 25y loan at 5%, ~£360k-£390k remains."""
    remaining = remaining_balance(500_000, 0.05, 25, 120)
    assert 360_000 < remaining < 390_000


def test_remaining_balance_at_end_is_zero():
    """After full term, balance should be zero (or near-zero due to rounding)."""
    assert remaining_balance(500_000, 0.05, 25, 300) < 1.0


def test_remaining_balance_zero_interest():
    """With 0% interest and linear amortization, half the term = half paid."""
    remaining = remaining_balance(240_000, 0.0, 20, 120)
    assert abs(remaining - 120_000) < 0.01
