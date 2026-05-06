#!/usr/bin/env python3
"""
RinggitSense — Golden dataset generator.

Generates synthetic Malaysian bank statements (Maybank + CIMB) and
expected classification outputs for AG-01, AG-02, and AG-03 validation.

Usage:
    python generate_golden_dataset.py

Outputs (in the same directory):
    - maybank_golden.csv       Synthetic Maybank statement (100+ transactions, 3 months)
    - cimb_golden.csv          Synthetic CIMB statement (80+ transactions, 3 months)
    - expected_categories.json  AG-01 expected categorization per transaction
    - expected_debts.json       AG-02 expected debt detection output
    - expected_patterns.json    AG-03 expected pattern analysis output
"""
import csv
import io
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Transaction definitions: (date_offset_from_start, description, debit, credit, expected_category, debt_info)
# date_offset is days from 2026-01-01
# debt_info: None or dict with {tier, debt_type, provider, person_name, indicators, group_key}
# ---------------------------------------------------------------------------

START_DATE = date(2026, 1, 1)


def d(offset: int) -> str:
    """Return date string DD/MM/YYYY from offset."""
    return (START_DATE + timedelta(days=offset)).strftime("%d/%m/%Y")


def d_iso(offset: int) -> str:
    """Return ISO date from offset."""
    return (START_DATE + timedelta(days=offset)).isoformat()


# ── Maybank Transactions ──────────────────────────────────────────────

MAYBANK_TRANSACTIONS: list[dict[str, Any]] = [
    # === Month 1: January 2026 ===
    # INCOME
    {"date": d(0), "desc": "SALARY JAN 2026", "debit": "", "credit": "5500.00",
     "cat": "INCOME", "conf": 0.98, "sub": "salary", "merchant": None},
    # FOOD
    {"date": d(1), "desc": "MCDONALD'S SUNWAY PYRAMID", "debit": "25.90", "credit": "",
     "cat": "FOOD", "conf": 0.97, "sub": "fast_food", "merchant": "McDonald's"},
    {"date": d(1), "desc": "NASI KANDAR PELITA BANGSAR", "debit": "12.50", "credit": "",
     "cat": "FOOD", "conf": 0.95, "sub": "restaurant", "merchant": "Nasi Kandar Pelita"},
    {"date": d(2), "desc": "JAYA GROCER MID VALLEY", "debit": "156.80", "credit": "",
     "cat": "FOOD", "conf": 0.93, "sub": "groceries", "merchant": "Jaya Grocer"},
    {"date": d(2), "desc": "GRAB FOOD DELIVERY", "debit": "35.00", "credit": "",
     "cat": "FOOD", "conf": 0.92, "sub": "delivery", "merchant": "GrabFood"},
    # TRANSPORT
    {"date": d(3), "desc": "PLUS TOLL PLZ SUBANG", "debit": "3.20", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "PLUS"},
    {"date": d(3), "desc": "DUKE TOLL DUTA ULU KLANG", "debit": "1.60", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "DUKE"},
    {"date": d(3), "desc": "PETRONAS BANGSAR SOUTH", "debit": "85.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.95, "sub": "petrol", "merchant": "Petronas"},
    {"date": d(4), "desc": "GRAB CAR KUALA LUMPUR", "debit": "18.50", "credit": "",
     "cat": "TRANSPORT", "conf": 0.94, "sub": "ride_hailing", "merchant": "Grab"},
    {"date": d(4), "desc": "RAPIDKL MRT TOPUP", "debit": "50.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.92, "sub": "public_transport", "merchant": "RapidKL"},
    # BILLS
    {"date": d(5), "desc": "TNB BILL PAYMENT", "debit": "125.50", "credit": "",
     "cat": "BILLS", "conf": 0.97, "sub": "electricity", "merchant": "TNB"},
    {"date": d(5), "desc": "UNIFI TM BROADBAND", "debit": "149.00", "credit": "",
     "cat": "BILLS", "conf": 0.96, "sub": "internet", "merchant": "Unifi"},
    {"date": d(5), "desc": "CELCOM POSTPAID", "debit": "79.00", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "mobile", "merchant": "Celcom"},
    {"date": d(5), "desc": "NETFLIX MALAYSIA", "debit": "54.90", "credit": "",
     "cat": "BILLS", "conf": 0.93, "sub": "subscription", "merchant": "Netflix"},
    # ENTERTAINMENT
    {"date": d(6), "desc": "GSC CINEMA MID VALLEY", "debit": "36.00", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.96, "sub": "movies", "merchant": "GSC"},
    {"date": d(6), "desc": "SPOTIFY PREMIUM", "debit": "15.90", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.94, "sub": "music", "merchant": "Spotify"},
    # SHOPPING
    {"date": d(7), "desc": "SHOPEE MALAYSIA", "debit": "89.90", "credit": "",
     "cat": "SHOPPING", "conf": 0.94, "sub": "online", "merchant": "Shopee"},
    {"date": d(7), "desc": "LAZADA MALAYSIA", "debit": "245.00", "credit": "",
     "cat": "SHOPPING", "conf": 0.94, "sub": "online", "merchant": "Lazada"},
    {"date": d(8), "desc": "ZARA MID VALLEY MEGAMALL", "debit": "199.00", "credit": "",
     "cat": "SHOPPING", "conf": 0.93, "sub": "clothing", "merchant": "Zara"},
    # TRANSFER
    {"date": d(9), "desc": "TRANSFER TO ALI BIN ABU", "debit": "200.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.90, "sub": "person", "merchant": None},
    {"date": d(9), "desc": "TNG EWALLET TOPUP", "debit": "100.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.88, "sub": "ewallet", "merchant": "TnG eWallet"},
    # DEBT_PAYMENT — FORMAL tier
    {"date": d(10), "desc": "PTPTN REPAYMENT", "debit": "250.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "education_loan", "merchant": "PTPTN",
     "debt": {"tier": "FORMAL", "type": "education_loan", "provider": "PTPTN",
              "indicators": ["PTPTN", "REPAYMENT"], "group": "ptptn_loan", "monthly": 250.00}},
    {"date": d(10), "desc": "MAYBANK PERSONAL LOAN", "debit": "450.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "personal_loan", "merchant": "Maybank",
     "debt": {"tier": "FORMAL", "type": "personal_loan", "provider": "Maybank",
              "indicators": ["PERSONAL LOAN"], "group": "maybank_personal", "monthly": 450.00}},
    {"date": d(10), "desc": "MAYBANK HIRE PURCHASE", "debit": "850.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "car_loan", "merchant": "Maybank",
     "debt": {"tier": "FORMAL", "type": "hire_purchase", "provider": "Maybank",
              "indicators": ["HIRE PURCHASE"], "group": "maybank_car", "monthly": 850.00}},
    # DEBT_PAYMENT — BNPL tier
    {"date": d(11), "desc": "SPAYLATER INSTALLMENT", "debit": "89.90", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "SPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "SPayLater",
              "indicators": ["SPAYLATER", "INSTALLMENT"], "group": "spaylater", "monthly": 89.90}},
    {"date": d(11), "desc": "GRABPAYLATER REPAYMENT", "debit": "45.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "GrabPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "GrabPayLater",
              "indicators": ["GRABPAYLATER", "REPAYMENT"], "group": "grabpaylater", "monthly": 45.00}},
    {"date": d(11), "desc": "ATOME PAYMENT 2/3", "debit": "66.33", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.94, "sub": "bnpl", "merchant": "Atome",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "Atome",
              "indicators": ["ATOME", "PAYMENT", "2/3"], "group": "atome_1", "monthly": 66.33}},
    # HEALTHCARE
    {"date": d(12), "desc": "GUARDIAN PHARMACY", "debit": "42.50", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.92, "sub": "pharmacy", "merchant": "Guardian"},
    {"date": d(12), "desc": "KLINIK KESIHATAN BANGSAR", "debit": "35.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.93, "sub": "clinic", "merchant": "Klinik Kesihatan"},
    {"date": d(13), "desc": "GREAT EASTERN INSURANCE", "debit": "180.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.85, "sub": "insurance", "merchant": "Great Eastern"},
    # TRANSPORT (more)
    {"date": d(14), "desc": "PARKING KLCC", "debit": "8.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.90, "sub": "parking", "merchant": None},
    # OTHER
    {"date": d(14), "desc": "KEDAI RUNCIT PAK ALI", "debit": "5.60", "credit": "",
     "cat": "OTHER", "conf": 0.60, "sub": "convenience_store", "merchant": "Kedai Runcit Pak Ali"},
    # TRANSFER (Tabung Haji — could be OTHER or TRANSFER)
    {"date": d(15), "desc": "TABUNG HAJI DEPOSIT", "debit": "500.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.80, "sub": "savings", "merchant": "Tabung Haji"},
    # INCOME (refund, cashback)
    {"date": d(16), "desc": "REFUND SHOPEE", "debit": "", "credit": "89.90",
     "cat": "INCOME", "conf": 0.90, "sub": "refund", "merchant": "Shopee"},
    {"date": d(17), "desc": "CASHBACK MAYBANK", "debit": "", "credit": "12.50",
     "cat": "INCOME", "conf": 0.88, "sub": "cashback", "merchant": "Maybank"},
    # TRANSPORT
    {"date": d(18), "desc": "SMART TOLL KL", "debit": "2.50", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "SMART"},
    # SHOPPING
    {"date": d(19), "desc": "WATSON'S SUNWAY", "debit": "28.90", "credit": "",
     "cat": "SHOPPING", "conf": 0.88, "sub": "personal_care", "merchant": "Watson's"},
    # FOOD
    {"date": d(20), "desc": "DOMINO'S PIZZA DELIVERY", "debit": "42.90", "credit": "",
     "cat": "FOOD", "conf": 0.95, "sub": "delivery", "merchant": "Domino's"},
    # TRANSFER
    {"date": d(21), "desc": "BOOST TOPUP", "debit": "30.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.85, "sub": "ewallet", "merchant": "Boost"},
    # INCOME (transfer from friend)
    {"date": d(22), "desc": "TRANSFER FROM SARAH", "debit": "", "credit": "150.00",
     "cat": "INCOME", "conf": 0.82, "sub": "transfer_in", "merchant": None},
    # DEBT_PAYMENT — FORMAL (credit card)
    {"date": d(23), "desc": "AEON BANK CREDIT CARD", "debit": "350.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "credit_card", "merchant": "Aeon Bank",
     "debt": {"tier": "FORMAL", "type": "credit_card", "provider": "Aeon Bank",
              "indicators": ["CREDIT CARD"], "group": "aeon_cc", "monthly": 350.00}},
    # TRANSPORT
    {"date": d(24), "desc": "KESAS TOLL SHAH ALAM", "debit": "1.50", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "KESAS"},
    {"date": d(25), "desc": "SHELL PETROL DAMANSARA", "debit": "92.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.95, "sub": "petrol", "merchant": "Shell"},
    # FOOD
    {"date": d(26), "desc": "MAMAK RESTORAN PELITA", "debit": "8.50", "credit": "",
     "cat": "FOOD", "conf": 0.93, "sub": "restaurant", "merchant": "Restoran Pelita"},
    # SHOPPING
    {"date": d(27), "desc": "UNIQLO PAVILION KL", "debit": "159.00", "credit": "",
     "cat": "SHOPPING", "conf": 0.94, "sub": "clothing", "merchant": "Uniqlo"},
    # ENTERTAINMENT
    {"date": d(28), "desc": "STEAM STORE PURCHASE", "debit": "125.00", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.93, "sub": "gaming", "merchant": "Steam"},
    # HEALTHCARE
    {"date": d(29), "desc": "KPJ SPECIALIST HOSPITAL", "debit": "280.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.96, "sub": "hospital", "merchant": "KPJ"},
    # INCOME (salary advance)
    {"date": d(30), "desc": "SALARY ADVANCE", "debit": "", "credit": "500.00",
     "cat": "INCOME", "conf": 0.85, "sub": "salary_advance", "merchant": None},

    # === Month 2: February 2026 ===
    {"date": d(31), "desc": "SALARY FEB 2026", "debit": "", "credit": "5500.00",
     "cat": "INCOME", "conf": 0.98, "sub": "salary", "merchant": None},
    {"date": d(32), "desc": "MCDONALD'S BANGSAR SOUTH", "debit": "22.90", "credit": "",
     "cat": "FOOD", "conf": 0.97, "sub": "fast_food", "merchant": "McDonald's"},
    {"date": d(33), "desc": "PLUS TOLL PLZ DAMANSARA", "debit": "4.10", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "PLUS"},
    {"date": d(34), "desc": "TNB BILL PAYMENT", "debit": "132.00", "credit": "",
     "cat": "BILLS", "conf": 0.97, "sub": "electricity", "merchant": "TNB"},
    {"date": d(34), "desc": "UNIFI TM BROADBAND", "debit": "149.00", "credit": "",
     "cat": "BILLS", "conf": 0.96, "sub": "internet", "merchant": "Unifi"},
    {"date": d(35), "desc": "CELCOM POSTPAID", "debit": "79.00", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "mobile", "merchant": "Celcom"},
    {"date": d(36), "desc": "SHOPEE MALAYSIA", "debit": "134.50", "credit": "",
     "cat": "SHOPPING", "conf": 0.94, "sub": "online", "merchant": "Shopee"},
    {"date": d(37), "desc": "PETRONAS MONT KIARA", "debit": "90.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.95, "sub": "petrol", "merchant": "Petronas"},
    # Recurring debts — Month 2
    {"date": d(40), "desc": "PTPTN REPAYMENT", "debit": "250.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "education_loan", "merchant": "PTPTN",
     "debt": {"tier": "FORMAL", "type": "education_loan", "provider": "PTPTN",
              "indicators": ["PTPTN", "REPAYMENT"], "group": "ptptn_loan", "monthly": 250.00}},
    {"date": d(40), "desc": "MAYBANK PERSONAL LOAN", "debit": "450.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "personal_loan", "merchant": "Maybank",
     "debt": {"tier": "FORMAL", "type": "personal_loan", "provider": "Maybank",
              "indicators": ["PERSONAL LOAN"], "group": "maybank_personal", "monthly": 450.00}},
    {"date": d(40), "desc": "MAYBANK HIRE PURCHASE", "debit": "850.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "car_loan", "merchant": "Maybank",
     "debt": {"tier": "FORMAL", "type": "hire_purchase", "provider": "Maybank",
              "indicators": ["HIRE PURCHASE"], "group": "maybank_car", "monthly": 850.00}},
    {"date": d(41), "desc": "SPAYLATER INSTALLMENT", "debit": "89.90", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "SPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "SPayLater",
              "indicators": ["SPAYLATER", "INSTALLMENT"], "group": "spaylater", "monthly": 89.90}},
    {"date": d(41), "desc": "ATOME PAYMENT 3/3", "debit": "66.33", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.94, "sub": "bnpl", "merchant": "Atome",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "Atome",
              "indicators": ["ATOME", "PAYMENT", "3/3"], "group": "atome_1", "monthly": 66.33}},
    # HUTANG — informal debt
    {"date": d(42), "desc": "PINJAM DUIT AHMAD", "debit": "300.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.75, "sub": "person", "merchant": None,
     "debt": {"tier": "HUTANG", "type": "informal_loan", "provider": None,
              "person": "Ahmad", "indicators": ["PINJAM", "DUIT"], "group": "hutang_ahmad", "monthly": None}},
    {"date": d(45), "desc": "BAYAR BALIK DARI AHMAD", "debit": "", "credit": "300.00",
     "cat": "INCOME", "conf": 0.70, "sub": "transfer_in", "merchant": None,
     "debt": {"tier": "HUTANG", "type": "informal_repayment", "provider": None,
              "person": "Ahmad", "indicators": ["BAYAR BALIK"], "group": "hutang_ahmad", "monthly": None}},
    # More regular spending
    {"date": d(43), "desc": "NASI LEMAK ANTARABANGSA", "debit": "9.50", "credit": "",
     "cat": "FOOD", "conf": 0.92, "sub": "restaurant", "merchant": "Nasi Lemak Antarabangsa"},
    {"date": d(44), "desc": "NETFLIX MALAYSIA", "debit": "54.90", "credit": "",
     "cat": "BILLS", "conf": 0.93, "sub": "subscription", "merchant": "Netflix"},
    {"date": d(46), "desc": "GSC CINEMA PAVILION", "debit": "38.00", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.96, "sub": "movies", "merchant": "GSC"},
    {"date": d(47), "desc": "KLINIK DR SITI BANGSAR", "debit": "55.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.92, "sub": "clinic", "merchant": "Klinik Dr Siti"},
    {"date": d(48), "desc": "GREAT EASTERN INSURANCE", "debit": "180.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.85, "sub": "insurance", "merchant": "Great Eastern"},
    {"date": d(49), "desc": "AEON BANK CREDIT CARD", "debit": "350.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "credit_card", "merchant": "Aeon Bank",
     "debt": {"tier": "FORMAL", "type": "credit_card", "provider": "Aeon Bank",
              "indicators": ["CREDIT CARD"], "group": "aeon_cc", "monthly": 350.00}},

    # === Month 3: March 2026 ===
    {"date": d(59), "desc": "SALARY MAR 2026", "debit": "", "credit": "5500.00",
     "cat": "INCOME", "conf": 0.98, "sub": "salary", "merchant": None},
    {"date": d(60), "desc": "NASI KANDAR PELITA KL", "debit": "14.00", "credit": "",
     "cat": "FOOD", "conf": 0.95, "sub": "restaurant", "merchant": "Nasi Kandar Pelita"},
    {"date": d(61), "desc": "PLUS TOLL PLZ SUBANG", "debit": "3.20", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "PLUS"},
    {"date": d(62), "desc": "TNB BILL PAYMENT", "debit": "140.00", "credit": "",
     "cat": "BILLS", "conf": 0.97, "sub": "electricity", "merchant": "TNB"},
    {"date": d(62), "desc": "UNIFI TM BROADBAND", "debit": "149.00", "credit": "",
     "cat": "BILLS", "conf": 0.96, "sub": "internet", "merchant": "Unifi"},
    {"date": d(63), "desc": "CELCOM POSTPAID", "debit": "79.00", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "mobile", "merchant": "Celcom"},
    # Recurring debts — Month 3
    {"date": d(69), "desc": "PTPTN REPAYMENT", "debit": "250.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "education_loan", "merchant": "PTPTN",
     "debt": {"tier": "FORMAL", "type": "education_loan", "provider": "PTPTN",
              "indicators": ["PTPTN", "REPAYMENT"], "group": "ptptn_loan", "monthly": 250.00}},
    {"date": d(69), "desc": "MAYBANK PERSONAL LOAN", "debit": "450.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "personal_loan", "merchant": "Maybank",
     "debt": {"tier": "FORMAL", "type": "personal_loan", "provider": "Maybank",
              "indicators": ["PERSONAL LOAN"], "group": "maybank_personal", "monthly": 450.00}},
    {"date": d(69), "desc": "MAYBANK HIRE PURCHASE", "debit": "850.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "car_loan", "merchant": "Maybank",
     "debt": {"tier": "FORMAL", "type": "hire_purchase", "provider": "Maybank",
              "indicators": ["HIRE PURCHASE"], "group": "maybank_car", "monthly": 850.00}},
    {"date": d(70), "desc": "SPAYLATER INSTALLMENT", "debit": "89.90", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "SPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "SPayLater",
              "indicators": ["SPAYLATER", "INSTALLMENT"], "group": "spaylater", "monthly": 89.90}},
    {"date": d(70), "desc": "GRABPAYLATER REPAYMENT", "debit": "45.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "GrabPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "GrabPayLater",
              "indicators": ["GRABPAYLATER", "REPAYMENT"], "group": "grabpaylater", "monthly": 45.00}},
    # Another HUTANG
    {"date": d(71), "desc": "HUTANG SITI - DUIT MAKAN", "debit": "50.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.70, "sub": "person", "merchant": None,
     "debt": {"tier": "HUTANG", "type": "informal_loan", "provider": None,
              "person": "Siti", "indicators": ["HUTANG", "DUIT"], "group": "hutang_siti", "monthly": None}},
    {"date": d(72), "desc": "AEON BANK CREDIT CARD", "debit": "350.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "credit_card", "merchant": "Aeon Bank",
     "debt": {"tier": "FORMAL", "type": "credit_card", "provider": "Aeon Bank",
              "indicators": ["CREDIT CARD"], "group": "aeon_cc", "monthly": 350.00}},
    {"date": d(73), "desc": "NETFLIX MALAYSIA", "debit": "54.90", "credit": "",
     "cat": "BILLS", "conf": 0.93, "sub": "subscription", "merchant": "Netflix"},
    {"date": d(74), "desc": "SHOPEE MALAYSIA", "debit": "210.00", "credit": "",
     "cat": "SHOPPING", "conf": 0.94, "sub": "online", "merchant": "Shopee"},
    {"date": d(75), "desc": "PETRONAS CYBERJAYA", "debit": "88.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.95, "sub": "petrol", "merchant": "Petronas"},
    {"date": d(76), "desc": "GREAT EASTERN INSURANCE", "debit": "180.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.85, "sub": "insurance", "merchant": "Great Eastern"},
    {"date": d(77), "desc": "KEDAI MAMAK CORNER", "debit": "7.00", "credit": "",
     "cat": "FOOD", "conf": 0.90, "sub": "restaurant", "merchant": None},
    {"date": d(78), "desc": "PARKING MID VALLEY", "debit": "6.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.90, "sub": "parking", "merchant": None},
    # Edge cases
    {"date": d(79), "desc": "TXN WITH SPECIAL CHAR'S & SYMBOLS (TEST)", "debit": "15.00", "credit": "",
     "cat": "OTHER", "conf": 0.50, "sub": None, "merchant": None},
    {"date": d(80), "desc": "TRANSFER TO SITI BINTI MOHD", "debit": "100.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.90, "sub": "person", "merchant": None},
    {"date": d(81), "desc": "ASB FINANCING PAYMENT", "debit": "200.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "investment_loan", "merchant": "ASB",
     "debt": {"tier": "FORMAL", "type": "investment_loan", "provider": "ASB",
              "indicators": ["ASB FINANCING", "PAYMENT"], "group": "asb_financing", "monthly": 200.00}},
    {"date": d(82), "desc": "HOOLAH INSTALLMENT 1/4", "debit": "75.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.93, "sub": "bnpl", "merchant": "Hoolah",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "Hoolah",
              "indicators": ["HOOLAH", "INSTALLMENT", "1/4"], "group": "hoolah_1", "monthly": 75.00}},
    {"date": d(83), "desc": "SPLIT PAYMENT KAMAL 2/2", "debit": "55.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.90, "sub": "bnpl", "merchant": "Split",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "Split",
              "indicators": ["SPLIT", "PAYMENT", "2/2"], "group": "split_1", "monthly": 55.00}},
    {"date": d(84), "desc": "REFUND LAZADA", "debit": "", "credit": "67.00",
     "cat": "INCOME", "conf": 0.90, "sub": "refund", "merchant": "Lazada"},
    {"date": d(85), "desc": "TEALIVE MID VALLEY", "debit": "8.90", "credit": "",
     "cat": "FOOD", "conf": 0.92, "sub": "beverage", "merchant": "Tealive"},
    {"date": d(86), "desc": "MR DIY HARDWARE SUBANG", "debit": "25.00", "credit": "",
     "cat": "SHOPPING", "conf": 0.88, "sub": "hardware", "merchant": "MR DIY"},
    {"date": d(87), "desc": "STARBUCKS KLCC", "debit": "19.50", "credit": "",
     "cat": "FOOD", "conf": 0.95, "sub": "beverage", "merchant": "Starbucks"},
    {"date": d(88), "desc": "PLAYSTATION STORE PURCHASE", "debit": "185.00", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.93, "sub": "gaming", "merchant": "PlayStation"},
    {"date": d(89), "desc": "BOOST CASHBACK", "debit": "", "credit": "8.00",
     "cat": "INCOME", "conf": 0.87, "sub": "cashback", "merchant": "Boost"},
]


# ── CIMB Transactions ────────────────────────────────────────────────

CIMB_HEADER_LINES = [
    "CIMB Bank Berhad",
    "Statement Period: 01/01/2026 - 31/03/2026",
    "Account Number: 9876543210",
    "",
]

CIMB_TRANSACTIONS: list[dict[str, Any]] = [
    # === Month 1 ===
    {"date": d(0), "desc": "GAJI BULANAN", "debit": "", "credit": "4800.00",
     "cat": "INCOME", "conf": 0.96, "sub": "salary", "merchant": None},
    {"date": d(1), "desc": "KFC BUKIT BINTANG", "debit": "15.90", "credit": "",
     "cat": "FOOD", "conf": 0.96, "sub": "fast_food", "merchant": "KFC"},
    {"date": d(1), "desc": "WARUNG KOPI AHMAD", "debit": "6.50", "credit": "",
     "cat": "FOOD", "conf": 0.90, "sub": "restaurant", "merchant": "Warung Kopi Ahmad"},
    {"date": d(2), "desc": "COLD STORAGE BANGSAR VILLAGE", "debit": "210.40", "credit": "",
     "cat": "FOOD", "conf": 0.92, "sub": "groceries", "merchant": "Cold Storage"},
    {"date": d(3), "desc": "LDP TOLL PUCHONG", "debit": "2.10", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "LDP"},
    {"date": d(3), "desc": "MEX TOLL CYBERJAYA", "debit": "1.80", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "MEX"},
    {"date": d(3), "desc": "PETRONAS CYBERJAYA", "debit": "78.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.95, "sub": "petrol", "merchant": "Petronas"},
    {"date": d(4), "desc": "MOOVIT TAXI KL", "debit": "22.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.92, "sub": "ride_hailing", "merchant": "Moovit"},
    {"date": d(5), "desc": "SYABAS WATER BILL", "debit": "35.50", "credit": "",
     "cat": "BILLS", "conf": 0.96, "sub": "water", "merchant": "Syabas"},
    {"date": d(5), "desc": "MAXIS POSTPAID", "debit": "89.00", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "mobile", "merchant": "Maxis"},
    {"date": d(5), "desc": "ASTRO BILL PAYMENT", "debit": "99.90", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "subscription", "merchant": "Astro"},
    {"date": d(6), "desc": "TGV CINEMA IOI CITY", "debit": "42.00", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.96, "sub": "movies", "merchant": "TGV"},
    {"date": d(6), "desc": "APPLE MUSIC", "debit": "14.90", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.93, "sub": "music", "merchant": "Apple Music"},
    {"date": d(7), "desc": "SHOPEE PURCHASES", "debit": "67.80", "credit": "",
     "cat": "SHOPPING", "conf": 0.94, "sub": "online", "merchant": "Shopee"},
    {"date": d(7), "desc": "MR DIY HARDWARE", "debit": "35.50", "credit": "",
     "cat": "SHOPPING", "conf": 0.88, "sub": "hardware", "merchant": "MR DIY"},
    {"date": d(8), "desc": "TRANSFER TO AHMAD", "debit": "200.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.90, "sub": "person", "merchant": None},
    {"date": d(8), "desc": "BIGPAY TOPUP", "debit": "50.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.85, "sub": "ewallet", "merchant": "BigPay"},
    # DEBT — FORMAL
    {"date": d(9), "desc": "CIMB HOUSING LOAN", "debit": "1200.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "housing_loan", "merchant": "CIMB",
     "debt": {"tier": "FORMAL", "type": "housing_loan", "provider": "CIMB",
              "indicators": ["HOUSING LOAN"], "group": "cimb_housing", "monthly": 1200.00}},
    {"date": d(9), "desc": "PTPTN AUTO DEBIT", "debit": "300.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "education_loan", "merchant": "PTPTN",
     "debt": {"tier": "FORMAL", "type": "education_loan", "provider": "PTPTN",
              "indicators": ["PTPTN", "AUTO DEBIT"], "group": "ptptn_loan_cimb", "monthly": 300.00}},
    # DEBT — BNPL
    {"date": d(10), "desc": "SPAYLATER SHOPEE", "debit": "55.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "SPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "SPayLater",
              "indicators": ["SPAYLATER"], "group": "spaylater_cimb", "monthly": 55.00}},
    {"date": d(10), "desc": "ATOME INSTALLMENT 3/6", "debit": "42.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.94, "sub": "bnpl", "merchant": "Atome",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "Atome",
              "indicators": ["ATOME", "INSTALLMENT", "3/6"], "group": "atome_cimb", "monthly": 42.00}},
    # HEALTHCARE
    {"date": d(11), "desc": "WATSONS PHARMACY", "debit": "18.90", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.88, "sub": "pharmacy", "merchant": "Watson's"},
    {"date": d(11), "desc": "COLUMBIA ASIA CLINIC", "debit": "65.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.94, "sub": "clinic", "merchant": "Columbia Asia"},
    {"date": d(12), "desc": "PRUDENTIAL INSURANCE", "debit": "220.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.85, "sub": "insurance", "merchant": "Prudential"},
    # TRANSPORT
    {"date": d(13), "desc": "NPE TOLL PUCHONG", "debit": "1.20", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "NPE"},
    {"date": d(13), "desc": "PARKING IOI CITY MALL", "debit": "6.00", "credit": "",
     "cat": "TRANSPORT", "conf": 0.90, "sub": "parking", "merchant": None},
    # FOOD
    {"date": d(14), "desc": "STARBUCKS MID VALLEY", "debit": "18.50", "credit": "",
     "cat": "FOOD", "conf": 0.95, "sub": "beverage", "merchant": "Starbucks"},
    # INCOME
    {"date": d(15), "desc": "BONUS TAHUNAN", "debit": "", "credit": "2000.00",
     "cat": "INCOME", "conf": 0.95, "sub": "bonus", "merchant": None},
    {"date": d(16), "desc": "REFUND LAZADA", "debit": "", "credit": "45.00",
     "cat": "INCOME", "conf": 0.90, "sub": "refund", "merchant": "Lazada"},
    # TRANSPORT
    {"date": d(17), "desc": "AKLEH TOLL AMPANG", "debit": "2.50", "credit": "",
     "cat": "TRANSPORT", "conf": 0.96, "sub": "toll", "merchant": "AKLEH"},
    # FOOD
    {"date": d(18), "desc": "SUSHI KING PAVILION", "debit": "32.50", "credit": "",
     "cat": "FOOD", "conf": 0.95, "sub": "restaurant", "merchant": "Sushi King"},
    # SHOPPING
    {"date": d(19), "desc": "H&M PAVILION KL", "debit": "129.00", "credit": "",
     "cat": "SHOPPING", "conf": 0.93, "sub": "clothing", "merchant": "H&M"},
    # ENTERTAINMENT
    {"date": d(20), "desc": "PLAYSTATION STORE", "debit": "199.00", "credit": "",
     "cat": "ENTERTAINMENT", "conf": 0.93, "sub": "gaming", "merchant": "PlayStation"},
    # HEALTHCARE
    {"date": d(21), "desc": "GLENEAGLES HOSPITAL", "debit": "450.00", "credit": "",
     "cat": "HEALTHCARE", "conf": 0.96, "sub": "hospital", "merchant": "Gleneagles"},
    # INCOME (transfer from wife)
    {"date": d(22), "desc": "TRANSFER FROM WIFE", "debit": "", "credit": "500.00",
     "cat": "INCOME", "conf": 0.82, "sub": "transfer_in", "merchant": None},
    # DEBT — FORMAL (personal loan)
    {"date": d(23), "desc": "CIMB PERSONAL LOAN", "debit": "380.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "personal_loan", "merchant": "CIMB",
     "debt": {"tier": "FORMAL", "type": "personal_loan", "provider": "CIMB",
              "indicators": ["PERSONAL LOAN"], "group": "cimb_personal", "monthly": 380.00}},
    # DEBT — BNPL
    {"date": d(24), "desc": "GRABPAYLATER 1/3", "debit": "33.33", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.94, "sub": "bnpl", "merchant": "GrabPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "GrabPayLater",
              "indicators": ["GRABPAYLATER", "1/3"], "group": "grabpaylater_cimb", "monthly": 33.33}},
    # FOOD
    {"date": d(25), "desc": "MYDIN HYPERMARKET", "debit": "145.00", "credit": "",
     "cat": "FOOD", "conf": 0.91, "sub": "groceries", "merchant": "Mydin"},
    {"date": d(26), "desc": "MAMAK RESTORAN MURNI", "debit": "9.00", "credit": "",
     "cat": "FOOD", "conf": 0.93, "sub": "restaurant", "merchant": "Restoran Murni"},
    # INCOME
    {"date": d(27), "desc": "BOOST CASHBACK", "debit": "", "credit": "5.00",
     "cat": "INCOME", "conf": 0.87, "sub": "cashback", "merchant": "Boost"},
    # OTHER
    {"date": d(28), "desc": "KEDAI GUNTING RAMBUT", "debit": "15.00", "credit": "",
     "cat": "OTHER", "conf": 0.65, "sub": "personal_care", "merchant": None},
    # FOOD
    {"date": d(29), "desc": "TEALIVE IOI CITY", "debit": "8.90", "credit": "",
     "cat": "FOOD", "conf": 0.92, "sub": "beverage", "merchant": "Tealive"},

    # === Month 2 (CIMB) ===
    {"date": d(31), "desc": "GAJI BULANAN", "debit": "", "credit": "4800.00",
     "cat": "INCOME", "conf": 0.96, "sub": "salary", "merchant": None},
    {"date": d(35), "desc": "SYABAS WATER BILL", "debit": "38.00", "credit": "",
     "cat": "BILLS", "conf": 0.96, "sub": "water", "merchant": "Syabas"},
    {"date": d(35), "desc": "MAXIS POSTPAID", "debit": "89.00", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "mobile", "merchant": "Maxis"},
    {"date": d(36), "desc": "ASTRO BILL PAYMENT", "debit": "99.90", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "subscription", "merchant": "Astro"},
    # Recurring debts — CIMB Month 2
    {"date": d(39), "desc": "CIMB HOUSING LOAN", "debit": "1200.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "housing_loan", "merchant": "CIMB",
     "debt": {"tier": "FORMAL", "type": "housing_loan", "provider": "CIMB",
              "indicators": ["HOUSING LOAN"], "group": "cimb_housing", "monthly": 1200.00}},
    {"date": d(39), "desc": "PTPTN AUTO DEBIT", "debit": "300.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "education_loan", "merchant": "PTPTN",
     "debt": {"tier": "FORMAL", "type": "education_loan", "provider": "PTPTN",
              "indicators": ["PTPTN", "AUTO DEBIT"], "group": "ptptn_loan_cimb", "monthly": 300.00}},
    {"date": d(39), "desc": "CIMB PERSONAL LOAN", "debit": "380.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "personal_loan", "merchant": "CIMB",
     "debt": {"tier": "FORMAL", "type": "personal_loan", "provider": "CIMB",
              "indicators": ["PERSONAL LOAN"], "group": "cimb_personal", "monthly": 380.00}},
    {"date": d(40), "desc": "SPAYLATER SHOPEE", "debit": "55.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "SPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "SPayLater",
              "indicators": ["SPAYLATER"], "group": "spaylater_cimb", "monthly": 55.00}},
    # HUTANG — CIMB side
    {"date": d(42), "desc": "BAYAR HUTANG KAMAL", "debit": "80.00", "credit": "",
     "cat": "TRANSFER", "conf": 0.72, "sub": "person", "merchant": None,
     "debt": {"tier": "HUTANG", "type": "informal_repayment", "provider": None,
              "person": "Kamal", "indicators": ["BAYAR", "HUTANG"], "group": "hutang_kamal", "monthly": None}},

    # === Month 3 (CIMB) ===
    {"date": d(59), "desc": "GAJI BULANAN", "debit": "", "credit": "4800.00",
     "cat": "INCOME", "conf": 0.96, "sub": "salary", "merchant": None},
    {"date": d(65), "desc": "SYABAS WATER BILL", "debit": "36.00", "credit": "",
     "cat": "BILLS", "conf": 0.96, "sub": "water", "merchant": "Syabas"},
    {"date": d(65), "desc": "MAXIS POSTPAID", "debit": "89.00", "credit": "",
     "cat": "BILLS", "conf": 0.95, "sub": "mobile", "merchant": "Maxis"},
    {"date": d(69), "desc": "CIMB HOUSING LOAN", "debit": "1200.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "housing_loan", "merchant": "CIMB",
     "debt": {"tier": "FORMAL", "type": "housing_loan", "provider": "CIMB",
              "indicators": ["HOUSING LOAN"], "group": "cimb_housing", "monthly": 1200.00}},
    {"date": d(69), "desc": "PTPTN AUTO DEBIT", "debit": "300.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.98, "sub": "education_loan", "merchant": "PTPTN",
     "debt": {"tier": "FORMAL", "type": "education_loan", "provider": "PTPTN",
              "indicators": ["PTPTN", "AUTO DEBIT"], "group": "ptptn_loan_cimb", "monthly": 300.00}},
    {"date": d(69), "desc": "CIMB PERSONAL LOAN", "debit": "380.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.97, "sub": "personal_loan", "merchant": "CIMB",
     "debt": {"tier": "FORMAL", "type": "personal_loan", "provider": "CIMB",
              "indicators": ["PERSONAL LOAN"], "group": "cimb_personal", "monthly": 380.00}},
    {"date": d(70), "desc": "SPAYLATER SHOPEE", "debit": "55.00", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.95, "sub": "bnpl", "merchant": "SPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "SPayLater",
              "indicators": ["SPAYLATER"], "group": "spaylater_cimb", "monthly": 55.00}},
    {"date": d(70), "desc": "GRABPAYLATER 2/3", "debit": "33.33", "credit": "",
     "cat": "DEBT_PAYMENT", "conf": 0.94, "sub": "bnpl", "merchant": "GrabPayLater",
     "debt": {"tier": "BNPL", "type": "installment", "provider": "GrabPayLater",
              "indicators": ["GRABPAYLATER", "2/3"], "group": "grabpaylater_cimb", "monthly": 33.33}},
]


def _compute_balance(txns: list[dict], starting: float) -> list[tuple[dict, str]]:
    """Add running balance to transactions."""
    balance = starting
    result = []
    for t in txns:
        if t["credit"]:
            balance += float(t["credit"])
        if t["debit"]:
            balance -= float(t["debit"])
        result.append((t, f"{balance:.2f}"))
    return result


def generate_maybank_csv() -> str:
    """Generate Maybank CSV statement."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Transaction Date", "Description", "Debit", "Credit", "Balance"])

    rows = _compute_balance(MAYBANK_TRANSACTIONS, 0.0)
    for txn, balance in rows:
        writer.writerow([txn["date"], txn["desc"], txn["debit"], txn["credit"], balance])

    return output.getvalue()


def generate_cimb_csv() -> str:
    """Generate CIMB CSV statement with header rows."""
    lines = list(CIMB_HEADER_LINES)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Transaction Date", "Description", "Debit", "Credit", "Balance"])

    rows = _compute_balance(CIMB_TRANSACTIONS, 0.0)
    for txn, balance in rows:
        writer.writerow([txn["date"], txn["desc"], txn["debit"], txn["credit"], balance])

    csv_part = output.getvalue()
    return "\n".join(lines) + csv_part


def generate_expected_categories() -> dict:
    """Generate expected AG-01 categorization output."""
    all_txns = []
    for source, txns in [("maybank", MAYBANK_TRANSACTIONS), ("cimb", CIMB_TRANSACTIONS)]:
        for i, t in enumerate(txns):
            all_txns.append({
                "source": source,
                "index": i,
                "description": t["desc"],
                "amount": float(t["debit"] or t["credit"]),
                "type": "debit" if t["debit"] else "credit",
                "expected_category": t["cat"],
                "min_confidence": t["conf"] - 0.15,  # Allow some tolerance
                "expected_subcategory": t.get("sub"),
                "expected_merchant": t.get("merchant"),
            })
    return {
        "version": "1.0",
        "description": "Expected AG-01 categorization for golden dataset",
        "total_transactions": len(all_txns),
        "categories_covered": sorted(set(t["expected_category"] for t in all_txns)),
        "transactions": all_txns,
    }


def generate_expected_debts() -> dict:
    """Generate expected AG-02 debt detection output."""
    debt_txns = []
    non_debt_txns = []
    debt_groups: dict[str, dict] = {}

    for source, txns in [("maybank", MAYBANK_TRANSACTIONS), ("cimb", CIMB_TRANSACTIONS)]:
        for i, t in enumerate(txns):
            debt_info = t.get("debt")
            entry = {
                "source": source,
                "index": i,
                "description": t["desc"],
                "amount": float(t["debit"] or t["credit"]),
                "type": "debit" if t["debit"] else "credit",
            }
            if debt_info:
                entry.update({
                    "is_debt_related": True,
                    "expected_tier": debt_info["tier"],
                    "expected_debt_type": debt_info["type"],
                    "expected_provider": debt_info.get("provider"),
                    "expected_person": debt_info.get("person"),
                    "expected_indicators": debt_info["indicators"],
                    "debt_group": debt_info["group"],
                    "min_confidence": 0.70,
                })
                debt_txns.append(entry)

                # Aggregate into groups
                gk = f"{source}_{debt_info['group']}"
                if gk not in debt_groups:
                    debt_groups[gk] = {
                        "group_key": debt_info["group"],
                        "source": source,
                        "tier": debt_info["tier"],
                        "provider": debt_info.get("provider"),
                        "person": debt_info.get("person"),
                        "debt_type": debt_info["type"],
                        "transaction_count": 0,
                        "total_amount": 0.0,
                        "estimated_monthly": debt_info.get("monthly"),
                    }
                debt_groups[gk]["transaction_count"] += 1
                debt_groups[gk]["total_amount"] += float(t["debit"] or t["credit"])
            else:
                entry["is_debt_related"] = False
                non_debt_txns.append(entry)

    # Build tier summaries
    tier_summary = {"FORMAL": [], "BNPL": [], "HUTANG": []}
    for g in debt_groups.values():
        tier_summary[g["tier"]].append(g)

    return {
        "version": "1.0",
        "description": "Expected AG-02 debt detection for golden dataset",
        "total_debt_transactions": len(debt_txns),
        "total_non_debt_transactions": len(non_debt_txns),
        "tiers_covered": ["FORMAL", "BNPL", "HUTANG"],
        "debt_transactions": debt_txns,
        "non_debt_sample": non_debt_txns[:10],  # First 10 non-debt for negative testing
        "debt_groups": list(debt_groups.values()),
        "tier_summary": {
            tier: {
                "count": len(groups),
                "providers": list(set(g["provider"] for g in groups if g["provider"])),
                "people": list(set(g["person"] for g in groups if g["person"])),
                "total_monthly": sum(g["estimated_monthly"] or 0 for g in groups),
            }
            for tier, groups in tier_summary.items()
        },
    }


def generate_expected_patterns() -> dict:
    """Generate expected AG-03 pattern analysis output."""
    return {
        "version": "1.0",
        "description": "Expected AG-03 pattern analysis for golden dataset",
        "recurring_expenses": [
            {"description": "TNB BILL PAYMENT", "frequency": "monthly", "amounts": [125.50, 132.00, 140.00],
             "trend": "RISING", "source": "maybank"},
            {"description": "UNIFI TM BROADBAND", "frequency": "monthly", "amount": 149.00,
             "trend": "STABLE", "source": "maybank"},
            {"description": "CELCOM POSTPAID", "frequency": "monthly", "amount": 79.00,
             "trend": "STABLE", "source": "maybank"},
            {"description": "NETFLIX MALAYSIA", "frequency": "monthly", "amount": 54.90,
             "trend": "STABLE", "source": "maybank"},
            {"description": "GREAT EASTERN INSURANCE", "frequency": "monthly", "amount": 180.00,
             "trend": "STABLE", "source": "maybank"},
            {"description": "SYABAS WATER BILL", "frequency": "monthly", "amounts": [35.50, 38.00, 36.00],
             "trend": "STABLE", "source": "cimb"},
            {"description": "MAXIS POSTPAID", "frequency": "monthly", "amount": 89.00,
             "trend": "STABLE", "source": "cimb"},
            {"description": "ASTRO BILL PAYMENT", "frequency": "monthly", "amount": 99.90,
             "trend": "STABLE", "source": "cimb"},
        ],
        "debt_recurring": [
            {"group": "ptptn_loan", "frequency": "monthly", "amount": 250.00, "source": "maybank"},
            {"group": "maybank_personal", "frequency": "monthly", "amount": 450.00, "source": "maybank"},
            {"group": "maybank_car", "frequency": "monthly", "amount": 850.00, "source": "maybank"},
            {"group": "aeon_cc", "frequency": "monthly", "amount": 350.00, "source": "maybank"},
            {"group": "cimb_housing", "frequency": "monthly", "amount": 1200.00, "source": "cimb"},
            {"group": "ptptn_loan_cimb", "frequency": "monthly", "amount": 300.00, "source": "cimb"},
            {"group": "cimb_personal", "frequency": "monthly", "amount": 380.00, "source": "cimb"},
        ],
        "spending_trends": [
            {"category": "FOOD", "trend": "STABLE", "monthly_avg_range": [150, 350]},
            {"category": "SHOPPING", "trend": "RISING", "note": "Increasing Shopee spend across months"},
            {"category": "BILLS", "trend": "RISING", "note": "TNB electricity bill increasing"},
        ],
        "anomalies": [
            {"description": "KPJ SPECIALIST HOSPITAL", "amount": 280.00, "reason": "Unusual large healthcare expense", "source": "maybank"},
            {"description": "GLENEAGLES HOSPITAL", "amount": 450.00, "reason": "Unusual large healthcare expense", "source": "cimb"},
            {"description": "LAZADA MALAYSIA", "amount": 245.00, "reason": "Large single online purchase", "source": "maybank"},
        ],
    }


def main():
    print("Generating golden dataset...")

    # Generate CSVs
    maybank_csv = generate_maybank_csv()
    cimb_csv = generate_cimb_csv()

    (OUTPUT_DIR / "maybank_golden.csv").write_text(maybank_csv, encoding="utf-8")
    print(f"  [OK] maybank_golden.csv ({len(MAYBANK_TRANSACTIONS)} transactions)")

    (OUTPUT_DIR / "cimb_golden.csv").write_text(cimb_csv, encoding="utf-8")
    print(f"  [OK] cimb_golden.csv ({len(CIMB_TRANSACTIONS)} transactions)")

    # Generate expected JSONs
    categories = generate_expected_categories()
    (OUTPUT_DIR / "expected_categories.json").write_text(
        json.dumps(categories, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  [OK] expected_categories.json ({categories['total_transactions']} entries, "
          f"{len(categories['categories_covered'])} categories)")

    debts = generate_expected_debts()
    (OUTPUT_DIR / "expected_debts.json").write_text(
        json.dumps(debts, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  [OK] expected_debts.json ({debts['total_debt_transactions']} debt txns, "
          f"{len(debts['debt_groups'])} groups)")

    patterns = generate_expected_patterns()
    (OUTPUT_DIR / "expected_patterns.json").write_text(
        json.dumps(patterns, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  [OK] expected_patterns.json ({len(patterns['recurring_expenses'])} recurring, "
          f"{len(patterns['anomalies'])} anomalies)")

    print(f"\nAll files written to: {OUTPUT_DIR}")
    print("Done!")


if __name__ == "__main__":
    main()
