#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XRechnung 3.0 (CEN EN 16931 UBL 2.1) XML Generator
Copyright (c) 2026 DACH Digitalwerk (MIT License)
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import date, timedelta
import argparse

def generate_xrechnung_xml(
    invoice_id: str = "RE-2026-0042",
    issue_date: str = None,
    due_date: str = None,
    buyer_ref: str = "04011000-12345-34",
    seller_name: str = "DACH Digitalwerk Solutions GmbH",
    seller_vat_id: str = "DE358992104",
    seller_street: str = "Friedrichstrasse 100",
    seller_zip: str = "10117",
    seller_city: str = "Berlin",
    seller_iban: str = "DE89370400440532013000",
    seller_bic: str = "DBDESMMXXX",
    buyer_name: str = "Behörde für IT-Sicherheit und Digitalisierung",
    buyer_street: str = "Willy-Brandt-Strasse 1",
    buyer_zip: str = "10557",
    buyer_city: str = "Berlin",
    lines: list = None
) -> str:
    if not issue_date:
        issue_date = date.today().isoformat()
    if not due_date:
        due_date = (date.today() + timedelta(days=30)).isoformat()
        
    if not lines:
        lines = [
            {"name": "Senior Cloud Architecture Consulting (EN 16931)", "qty": 10, "unit": "HUR", "price": 140.00, "vat": 19},
            {"name": "XRechnung 3.0 Schnittstellen-Prüfung", "qty": 1, "unit": "C62", "price": 600.00, "vat": 19}
        ]

    # Calculations
    net_total = sum(item["qty"] * item["price"] for item in lines)
    vat_total = sum((item["qty"] * item["price"]) * (item["vat"] / 100.0) for item in lines)
    gross_total = net_total + vat_total

    # XML namespaces
    ET.register_namespace('', "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2")
    ET.register_namespace('cac', "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2")
    ET.register_namespace('cbc', "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2")

    inv = ET.Element('{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice')
    
    def sub(parent, tag, text):
        elem = ET.SubElement(parent, f'{{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}}{tag}')
        elem.text = str(text)
        return elem

    def sub_cac(parent, tag):
        return ET.SubElement(parent, f'{{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}}{tag}')

    sub(inv, 'CustomizationID', 'urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0')
    sub(inv, 'ProfileID', 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0')
    sub(inv, 'ID', invoice_id)
    sub(inv, 'IssueDate', issue_date)
    sub(inv, 'DueDate', due_date)
    sub(inv, 'InvoiceTypeCode', '380')
    sub(inv, 'DocumentCurrencyCode', 'EUR')
    sub(inv, 'BuyerReference', buyer_ref)

    # AccountingSupplierParty
    asp = sub_cac(inv, 'AccountingSupplierParty')
    party = sub_cac(asp, 'Party')
    pname = sub_cac(party, 'PartyName')
    sub(pname, 'Name', seller_name)
    paddr = sub_cac(party, 'PostalAddress')
    sub(paddr, 'StreetName', seller_street)
    sub(paddr, 'PostalZone', seller_zip)
    sub(paddr, 'CityName', seller_city)
    ctry = sub_cac(paddr, 'Country')
    sub(ctry, 'IdentificationCode', 'DE')
    ptax = sub_cac(party, 'PartyTaxScheme')
    sub(ptax, 'CompanyID', seller_vat_id)
    ts = sub_cac(ptax, 'TaxScheme')
    sub(ts, 'ID', 'VAT')
    plegal = sub_cac(party, 'PartyLegalEntity')
    sub(plegal, 'RegistrationName', seller_name)

    # AccountingCustomerParty
    acp = sub_cac(inv, 'AccountingCustomerParty')
    cparty = sub_cac(acp, 'Party')
    cpname = sub_cac(cparty, 'PartyName')
    sub(cpname, 'Name', buyer_name)
    cpaddr = sub_cac(cparty, 'PostalAddress')
    sub(cpaddr, 'StreetName', buyer_street)
    sub(cpaddr, 'PostalZone', buyer_zip)
    sub(cpaddr, 'CityName', buyer_city)
    cctry = sub_cac(cpaddr, 'Country')
    sub(cctry, 'IdentificationCode', 'DE')
    clegal = sub_cac(cparty, 'PartyLegalEntity')
    sub(clegal, 'RegistrationName', buyer_name)

    # PaymentMeans
    pm = sub_cac(inv, 'PaymentMeans')
    sub(pm, 'PaymentMeansCode', '58') # SEPA Credit Transfer
    pfa = sub_cac(pm, 'PayeeFinancialAccount')
    sub(pfa, 'ID', seller_iban)
    fi = sub_cac(pfa, 'FinancialInstitutionBranch')
    sub(fi, 'ID', seller_bic)

    # TaxTotal
    tt = sub_cac(inv, 'TaxTotal')
    tamt = sub(tt, 'TaxAmount', f"{vat_total:.2f}")
    tamt.set('currencyID', 'EUR')
    
    tsub = sub_cac(tt, 'TaxSubtotal')
    ts_taxable = sub(tsub, 'TaxableAmount', f"{net_total:.2f}")
    ts_taxable.set('currencyID', 'EUR')
    ts_amt = sub(tsub, 'TaxAmount', f"{vat_total:.2f}")
    ts_amt.set('currencyID', 'EUR')
    tcat = sub_cac(tsub, 'TaxCategory')
    sub(tcat, 'ID', 'S')
    sub(tcat, 'Percent', '19.00')
    tcatscheme = sub_cac(tcat, 'TaxScheme')
    sub(tcatscheme, 'ID', 'VAT')

    # LegalMonetaryTotal
    lmt = sub_cac(inv, 'LegalMonetaryTotal')
    sub(lmt, 'LineExtensionAmount', f"{net_total:.2f}").set('currencyID', 'EUR')
    sub(lmt, 'TaxExclusiveAmount', f"{net_total:.2f}").set('currencyID', 'EUR')
    sub(lmt, 'TaxInclusiveAmount', f"{gross_total:.2f}").set('currencyID', 'EUR')
    sub(lmt, 'PayableAmount', f"{gross_total:.2f}").set('currencyID', 'EUR')

    # InvoiceLine items
    for idx, line in enumerate(lines, start=1):
        il = sub_cac(inv, 'InvoiceLine')
        sub(il, 'ID', str(idx))
        qty_elem = sub(il, 'InvoicedQuantity', f"{line['qty']:.2f}")
        qty_elem.set('unitCode', line['unit'])
        line_net = line['qty'] * line['price']
        sub(il, 'LineExtensionAmount', f"{line_net:.2f}").set('currencyID', 'EUR')

        item_elem = sub_cac(il, 'Item')
        sub(item_elem, 'Description', line['name'])
        sub(item_elem, 'Name', line['name'])
        clt = sub_cac(item_elem, 'ClassifiedTaxCategory')
        sub(clt, 'ID', 'S')
        sub(clt, 'Percent', f"{line['vat']:.2f}")
        clts = sub_cac(clt, 'TaxScheme')
        sub(clts, 'ID', 'VAT')

        price_elem = sub_cac(il, 'Price')
        sub(price_elem, 'PriceAmount', f"{line['price']:.2f}").set('currencyID', 'EUR')

    xml_raw = ET.tostring(inv, encoding='utf-8')
    dom = minidom.parseString(xml_raw)
    return dom.toprettyxml(indent="  ", encoding="utf-8").decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description="XRechnung 3.0 UBL Generator")
    parser.add_argument("--out", "-o", default="sample_xrechnung_3.0.xml", help="Ausgabedatei XML")
    args = parser.parse_args()

    xml_content = generate_xrechnung_xml()
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"✅ XRechnung 3.0 erfolgreich erzeugt: {args.out}")

if __name__ == "__main__":
    main()
