/**
 * Modulo 10 Recursive (Mod10) Checksum Algorithm
 * Standard for Swiss QR-Bill (SIX SPC Standard v2.2) Reference Numbers (QRR)
 * Copyright (c) 2026 DACH Digitalwerk (MIT License)
 */

const MOD10_TABLE = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5];

/**
 * Calculates the Modulo 10 recursive check digit for a string of digits.
 * @param {string|number} input 
 * @returns {number} Check digit (0-9)
 */
function calculateMod10(input) {
  const digits = String(input || '').replace(/\D/g, '');
  if (!digits) {
    throw new Error('Input must contain at least one digit');
  }

  let carry = 0;
  for (let i = 0; i < digits.length; i++) {
    const digit = parseInt(digits[i], 10);
    carry = MOD10_TABLE[(carry + digit) % 10];
  }
  return (10 - carry) % 10;
}

/**
 * Formats a raw number into a 27-digit QRR with Mod10 check digit.
 * @param {string|number} rawNumber 
 * @returns {string} 27-digit QRR
 */
function generateQRReference(rawNumber) {
  const clean = String(rawNumber || '').replace(/\D/g, '');
  if (clean.length > 26) {
    throw new Error('Input must be max 26 digits');
  }
  const padded = clean.padStart(26, '0');
  const checkDigit = calculateMod10(padded);
  return padded + checkDigit;
}

/**
 * Validates a 27-digit Swiss QR reference string.
 * @param {string} qrr 
 * @returns {boolean}
 */
function validateQRReference(qrr) {
  const clean = String(qrr || '').replace(/\D/g, '');
  if (clean.length !== 27) return false;
  const payload = clean.slice(0, 26);
  const expectedCheck = calculateMod10(payload);
  const actualCheck = parseInt(clean[26], 10);
  return expectedCheck === actualCheck;
}

/**
 * Formats a 27-digit QRR with spaces in blocks of 5 digits from right to left.
 * Example: 21 00000 00003 13947 14300 09017
 * @param {string} qrr 
 * @returns {string}
 */
function formatQRReference(qrr) {
  const clean = String(qrr || '').replace(/\D/g, '');
  if (clean.length !== 27) return clean;
  return clean.replace(/(\d{2})(\d{5})(\d{5})(\d{5})(\d{5})(\d{5})/, '$1 $2 $3 $4 $5 $6');
}

module.exports = {
  calculateMod10,
  generateQRReference,
  validateQRReference,
  formatQRReference
};

if (require.main === module) {
  const testInput = "21000000000313947143000901";
  const check = calculateMod10(testInput);
  const full = generateQRReference(testInput);
  console.log(`Input: ${testInput}`);
  console.log(`Calculated Check Digit: ${check} (Expected: 7)`);
  console.log(`Full QRR: ${full}`);
  console.log(`Formatted: ${formatQRReference(full)}`);
  console.log(`Valid: ${validateQRReference(full)}`);
}
