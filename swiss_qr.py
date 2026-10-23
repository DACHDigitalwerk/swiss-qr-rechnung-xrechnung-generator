#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swiss QR-Bill (SIX SPC Standard v2.2) Payload Generator & Validator
Copyright (c) 2026 DACH Digitalwerk (MIT License)
"""

import sys
import re
import argparse

MOD10_TABLE = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]

def calculate_mod10_recursive(digits: str) -> int:
    clean = re.sub(r'\D', '', str(digits))
    if not clean:
        raise ValueError("Keine Ziffern übergeben")
    carry = 0
    for ch in clean:
        digit = int(ch)
        carry = MOD10_TABLE[(carry + digit) % 10]
    return (10 - carry) % 10

def is_qr_iban(iban: str) -> bool:
    clean = re.sub(r'\s', '', str(iban)).upper()
    if not (clean.startswith("CH") or clean.startswith("LI")) or len(clean) != 21:
        return False
    try:
        iid = int(clean[4:9])
        return 30000 <= iid <= 31999
    except ValueError:
        return False

def build_swiss_qr_payload(
    iban: str,
    cr_name: str,
    cr_street: str,
    cr_bldg: str,
    cr_zip: str,
    cr_city: str,
    cr_country: str = "CH",
    amount: float = None,
    currency: str = "CHF",
    db_name: str = "",
    db_street: str = "",
    db_bldg: str = "",
    db_zip: str = "",
    db_city: str = "",
    db_country: str = "CH",
    reference_type: str = "NON",
    reference: str = "",
    unstructured_msg: str = "",
    trailer: str = "EPD"
) -> str:
    clean_iban = re.sub(r'\s', '', iban).upper()
    formatted_amount = f"{amount:.2f}" if amount is not None and amount > 0 else ""
    
    # Check reference consistency
    if is_qr_iban(clean_iban):
        if reference_type != "QRR":
            raise ValueError("Für eine QR-IBAN muss der Referenztyp zwingend QRR sein!")
        if len(re.sub(r'\D', '', reference)) != 27:
            raise ValueError("Die QRR muss genau 27 Ziffern lang sein!")

    lines = [
        "SPC",              # 1. Header
        "0200",             # 2. Version
        "1",                # 3. Coding Type (UTF-8)
        clean_iban,         # 4. IBAN
        "S",                # 5. Adresstyp Kreditor (S = strukturiert)
        cr_name[:70],       # 6. Kreditor Name
        cr_street[:70],     # 7. Kreditor Strasse
        cr_bldg[:16],       # 8. Kreditor Hausnummer
        cr_zip[:16],        # 9. Kreditor PLZ
        cr_city[:35],       # 10. Kreditor Ort
        cr_country[:2],     # 11. Kreditor Land
        "", "", "", "", "", "", "", # 12-18 Reserviert (Ultimate Creditor)
        formatted_amount,   # 19. Betrag
        currency,           # 20. Währung (CHF oder EUR)
        "S" if db_name else "", # 21. Adresstyp Debitor
        db_name[:70],       # 22. Debitor Name
        db_street[:70],     # 23. Debitor Strasse
        db_bldg[:16],       # 24. Debitor Hausnummer
        db_zip[:16],        # 25. Debitor PLZ
        db_city[:35],       # 26. Debitor Ort
        db_country[:2] if db_name else "", # 27. Debitor Land
        reference_type,     # 28. Referenztyp (QRR, SCOR, NON)
        reference,          # 29. Referenznummer
        unstructured_msg[:140], # 30. Unstrukturierte Mitteilung
        trailer,            # 31. Trailer EPD
        ""                  # 32. Billing Info (optional)
    ]
    return "\r\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="SIX Swiss QR Payload Generator v2.2")
    parser.add_argument("--iban", default="CH4431999123000889012", help="Kreditor IBAN oder QR-IBAN")
    parser.add_argument("--name", default="DACH Digitalwerk Solutions AG", help="Kreditor Name")
    parser.add_argument("--street", default="Bahnhofstrasse", help="Kreditor Strasse")
    parser.add_argument("--bldg", default="10", help="Kreditor Hausnummer")
    parser.add_argument("--zip", default="8001", help="Kreditor PLZ")
    parser.add_argument("--city", default="Zürich", help="Kreditor Ort")
    parser.add_argument("--amount", type=float, default=1450.00, help="Rechnungsbetrag")
    parser.add_argument("--currency", default="CHF", choices=["CHF", "EUR"], help="Währung")
    parser.add_argument("--ref", default="210000000003139471430009017", help="27-stellige QRR oder Referenz")
    parser.add_argument("--msg", default="Rechnung 2026-1042 / Cloud Consulting", help="Mitteilung")

    args = parser.parse_args()
    ref_type = "QRR" if is_qr_iban(args.iban) else "NON"
    
    payload = build_swiss_qr_payload(
        iban=args.iban,
        cr_name=args.name,
        cr_street=args.street,
        cr_bldg=args.bldg,
        cr_zip=args.zip,
        cr_city=args.city,
        amount=args.amount,
        currency=args.currency,
        db_name="Musterkunde AG",
        db_street="Hauptstrasse",
        db_bldg="5",
        db_zip="3000",
        db_city="Bern",
        reference_type=ref_type,
        reference=args.ref if ref_type == "QRR" else "",
        unstructured_msg=args.msg
    )

    print("=" * 60)
    print(" 🇨🇭 SIX SWISS QR-BILL PAYLOAD (SPC 0200)")
    print("=" * 60)
    print(payload)
    print("=" * 60)
    print(f"Zeilenanzahl: {len(payload.splitlines())} (SIX Standard: 31/32 Zeilen)")

if __name__ == "__main__":
    main()
