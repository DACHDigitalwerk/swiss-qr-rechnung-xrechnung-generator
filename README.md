# Schweizer QR-Rechnung (SIX v2.2) & Deutsche XRechnung 3.0 Generator 🇨🇭 🇩🇪

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![SIX Swiss QR Standard](https://img.shields.io/badge/SIX_Standard-v2.2_SPC_0200-red.svg)](https://dach-digitalwerk.netlify.app/qr-suite/)
[![XRechnung Standard](https://img.shields.io/badge/XRechnung-3.0_UBL_2.1_(EN_16931)-gold.svg)](https://dach-digitalwerk.netlify.app/qr-suite/)
[![Web App Live](https://img.shields.io/badge/Live_Tool-100%25_Client--Side_&_Free-purple.svg)](https://dach-digitalwerk.netlify.app/qr-suite/)

> 🇨🇭🇩🇪 **Vollständige Entwickler-Referenz & Open-Source Tools für die Schweizer QR-Rechnung (SIX Swiss Payments Code v2.2) und die Deutsche XRechnung 3.0 (CEN EN 16931 UBL 2.1 XML).**  
> 100% lokal im Browser oder via Python/Node.js CLI ausführbar – ohne monatliche Abogebühren, ohne Vendor Lock-in und ohne Weitergabe sensibler Rechnungsdaten an Dritte.

---

### 🌐 Interaktive Live-Web-App (Sofort im Browser nutzen)

**Erstelle druckfertige Schweizer QR-Rechnungen (DIN A4 PDF mit Zahlteil) & validierte XRechnung-XMLs:**  
👉 **[https://dach-digitalwerk.netlify.app/qr-suite/](https://dach-digitalwerk.netlify.app/qr-suite/)**

---

## Inhaltsverzeichnis
1. [Schweizer QR-Rechnung: SIX Standard v2.2](#schweizer-qr-rechnung-six-standard-v22)
   - [Struktur des 32-Zeilen Payloads (`SPC`)](#struktur-des-32-zeilen-payloads-spc)
   - [Modulo 10 Rekursiv (Mod10) Prüfziffer-Algorithmus](#modulo-10-rekursiv-mod10-prüfziffer-algorithmus)
   - [QR-IBAN vs. Standard-IBAN & Referenztypen](#qr-iban-vs-standard-iban--referenztypen)
2. [Deutsche XRechnung 3.0: EN 16931-1 & UBL 2.1](#deutsche-xrechnung-30-en-16931-1--ubl-21)
   - [Gesetzliche Verpflichtung in Deutschland (B2B ab 2025)](#gesetzliche-verpflichtung-in-deutschland-b2b-ab-2025)
   - [Business Terms (BT) Mapping & XML-Architektur](#business-terms-bt-mapping--xml-architektur)
   - [Leitweg-ID Spezifikation](#leitweg-id-spezifikation)
3. [Entwickler-Tools & CLI-Nutzung](#entwickler-tools--cli-nutzung)
4. [Muster-Dateien & Validierung](#muster-dateien--validierung)
5. [Lizenz](#lizenz)

---

## Schweizer QR-Rechnung: SIX Standard v2.2

Die Schweizer QR-Rechnung löste per 30. September 2022 die alten roten (ES) und orangen (ESR) Einzahlungsscheine in der Schweiz und Liechtenstein verbindlich ab. Sie basiert auf dem **SIX Swiss Payments Code (SPC)** Standard in Version 2.2.

### Struktur des 32-Zeilen Payloads (`SPC`)

Der QR-Code enthält exakt bis zu 32 Textzeilen, getrennt durch ein einfaches Zeilenumbruchzeichen (`\r\n` oder `\n`), codiert in UTF-8:

| Zeile | Feld-Name | Datentyp | Max. Länge | Beschreibung / Formatbeispiel |
|-------|-----------|----------|------------|-------------------------------|
| 1 | **QRType** | String | 3 | Fix `SPC` (Swiss Payments Code) |
| 2 | **Version** | String | 4 | Fix `0200` (Version 2.0 / 2.2) |
| 3 | **CodingType** | String | 1 | Fix `1` (Zeichensatz UTF-8) |
| 4 | **Account** | IBAN | 21 | QR-IBAN (`CH..` / `LI..` mit IID 30000–31999) oder reguläre IBAN |
| 5 | **CrAdrType** | String | 1 | Adresstyp Zahlungsempfänger: `S` (strukturiert) oder `K` (kombiniert) |
| 6 | **CrName** | String | 70 | Name / Firma des Zahlungsempfängers |
| 7 | **CrStrtNmOrAdrLine1** | String | 70 | Strasse und Hausnummer (oder Adresszeile 1 bei Typ K) |
| 8 | **CrBldgNbOrAdrLine2** | String | 16 | Hausnummer (bei Typ S) oder Adresszeile 2 |
| 9 | **CrPstCd** | String | 16 | Postleitzahl (z. B. `8001`) |
| 10 | **CrTwnNm** | String | 35 | Ort / Stadt (z. B. `Zürich`) |
| 11 | **CrCtry** | ISO-2 | 2 | Ländercode (z. B. `CH` oder `LI`) |
| 12–18 | **UltmtCr...** | - | - | *Endbegünstigter (aktuell im SIX Standard reserviert, 7 Leerzeilen)* |
| 19 | **Amt** | Decimal | 12 | Betrag mit 2 Dezimalstellen (z. B. `1450.00`) oder leer bei freiem Betrag |
| 20 | **Ccy** | String | 3 | Währung: `CHF` oder `EUR` |
| 21 | **UltmtDbAdrType** | String | 1 | Adresstyp des Zahlungspflichtigen: `S` oder `K` (oder leer) |
| 22 | **UltmtDbName** | String | 70 | Name des Zahlungspflichtigen |
| 23 | **UltmtDbStrtNm** | String | 70 | Strasse / Hausnummer |
| 24 | **UltmtDbBldgNb** | String | 16 | Hausnummer |
| 25 | **UltmtDbPstCd** | String | 16 | Postleitzahl |
| 26 | **UltmtDbTwnNm** | String | 35 | Ort |
| 27 | **UltmtDbCtry** | ISO-2 | 2 | Land (`CH`, `DE`, `AT`, etc.) |
| 28 | **RefType** | String | 4 | Referenztyp: `QRR` (QR-Referenz), `SCOR` (Creditor Reference ISO 11649) oder `NON` |
| 29 | **Ref** | String | 27 | Referenznummer (27 Ziffern bei QRR mit Mod10, bis 25 Zeichen bei SCOR) |
| 30 | **Ustrd** | String | 140 | Unstrukturierte Mitteilung (z. B. `Rechnung 2026-1042`) |
| 31 | **Trailer** | String | 3 | Fix `EPD` (End of Payment Data) |
| 32 | **StrdBkgInf** | String | 140 | Strukturierte Rechnungsdaten (optional, z. B. Swico S1 Syntax) |

---

### Modulo 10 Rekursiv (Mod10) Prüfziffer-Algorithmus

Die 27-stellige Schweizer **QR-Referenz (QRR)** verlangt an der letzten Stelle eine Prüfziffer nach dem rekursiven Modulo-10-Verfahren (Mod10 rekursiv).

#### Mathematische Übergangstabelle:
```
Tabelle: [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]
```

#### Algorithmus in JavaScript:
```javascript
function calculateMod10Recursive(inputDigits) {
  const table = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5];
  let carry = 0;
  const digits = String(inputDigits).replace(/\D/g, '');
  for (let i = 0; i < digits.length; i++) {
    const digit = parseInt(digits[i], 10);
    carry = table[(carry + digit) % 10];
  }
  return (10 - carry) % 10;
}
```

---

### QR-IBAN vs. Standard-IBAN & Referenztypen

In der Schweizer QR-Rechnung existiert eine strikte Kopplung zwischen IBAN-Typ und Referenztyp:

1. **QR-IBAN (`CH..` mit IID zwischen 30000 und 31999):**
   * **Erfordert zwingend:** Referenztyp `QRR` (27-stellige numerische QR-Referenz mit Mod10 Prüfziffer).
   * Dient dem vollautomatisierten ESR-Nachfolgeabgleich im ERP/Fibu.
2. **Reguläre IBAN (`CH..` / `LI..` ohne QR-IID):**
   * **Erlaubt:** Referenztyp `NON` (ohne strukturierte Referenz) oder `SCOR` (ISO 11649 Creditor Reference mit `RF...`).

---

## Deutsche XRechnung 3.0: EN 16931-1 & UBL 2.1

Die **XRechnung** ist der nationale Standard für die elektronische Rechnungsstellung an öffentliche Auftraggeber (B2G) und ab dem **01. Januar 2025** schrittweise Pflicht für alle inländischen B2B-Umsätze im Rahmen des Wachstumschancengesetzes.

### Gesetzliche Verpflichtung in Deutschland (B2B ab 2025)
* **Ab 01.01.2025:** Grundsätzliche Empfangspflicht für alle deutschen Unternehmen (E-Rechnung nach EN 16931 zwingend lesbar).
* **2025–2026:** Übergangsfristen für Rechnungssteller (PDF/Papier noch temporär zulässig bei Vorjahresumsatz < 800.000 €).
* **Ab 01.01.2027 / 2028:** Vollständige B2B-Pflicht für alle Unternehmen ohne Ausnahmen.

### Business Terms (BT) Mapping & XML-Architektur

XRechnung 3.0 wird als XML-Dokument nach der UBL 2.1 Invoice Syntax formatiert:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</cbc:CustomizationID>
  <cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID>
  <cbc:ID>RE-2026-0042</cbc:ID>
  <cbc:IssueDate>2026-10-23</cbc:IssueDate>
  <cbc:DueDate>2026-11-22</cbc:DueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
  <cbc:BuyerReference>04011000-12345-34</cbc:BuyerReference>
  <!-- ... Lieferant (BT-27) & Käufer (BT-44) ... -->
  <!-- ... Steuerübersicht (BT-110) & Summen (BT-106) ... -->
</Invoice>
```

### Leitweg-ID Spezifikation (BT-10)
Bei Rechnungen an Bundes-, Landes- oder Kommunalbehörden ist die **Leitweg-ID** im Feld `BuyerReference` verpflichtend.  
Format: `[Grob-Adressierung (2 Ziffern)] [Fein-Adressierung (bis 10)] - [Detail (bis 30)] - [Prüfziffer (2)]`  
Beispiel: `04011000-12345-34` (Freie und Hansestadt Hamburg).

---

## Entwickler-Tools & CLI-Nutzung

### 1. Schweizer QR-Payload Generator (Python)
```bash
# Validierten SIX QR-Payload generieren
py swiss_qr.py --iban CH4431999123000889012 --creditor "Muster AG, Bahnhofstr. 1, 8001 Zürich" --amount 1250.50 --currency CHF --debtor "Kunde GmbH, Hauptstr. 5, 3000 Bern"
```

### 2. Modulo 10 Rekursiv Prüfziffer (JavaScript)
```javascript
const { calculateMod10, generateQRReference } = require('./mod10.js');

// 26 Ziffern Basis -> erzeugt vollständige 27-stellige QRR
const qrr = generateQRReference("21000000000313947143000901");
console.log(qrr); // "210000000003139471430009017"
```

### 3. XRechnung 3.0 Generator (Python)
```bash
# Erstellt eine vollständige XRechnung 3.0 UBL XML
py xrechnung_generator.py --out test_invoice.xml
```

---

## Muster-Dateien & Validierung

Im Verzeichnis `samples/` finden Sie:
* `sample_swiss_qr_payload.txt` – Originaler SIX SPC 0200 Textstream.
* `sample_xrechnung_3.0.xml` – Konforme EN 16931 / KoSIT 3.0 UBL-Rechnung.
* `batch_invoices_sample.csv` – Muster-CSV für Schweizer Serien-QR-Rechnungen.

Zur behördlichen Validierung der XML können Sie den offiziellen Prüftool-Validator der KoSIT (Koordinierungsstelle für IT-Standards) oder den Kosit Validation Node verwenden.

---

## Lizenz

Lizenziert unter der **MIT Lizenz** – Copyright (c) 2026 DACH Digitalwerk (https://dach-digitalwerk.netlify.app).
