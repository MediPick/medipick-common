/**
 * MediPick Phone Validation & Normalization (+94 format)
 */

export function normalizeSriLankanPhone(phone: string): string {
  let cleaned = phone.replace(/[^0-9+]/g, '');
  if (cleaned.startsWith('0')) {
    cleaned = '+94' + cleaned.substring(1);
  } else if (!cleaned.startsWith('+') && cleaned.startsWith('94')) {
    cleaned = '+' + cleaned;
  } else if (!cleaned.startsWith('+94')) {
    cleaned = '+94' + cleaned;
  }
  return cleaned;
}

export function formatPhoneDisplay(phone: string): string {
  const norm = normalizeSriLankanPhone(phone);
  // Format: +94 77 123 4567
  if (norm.length === 12) {
    return `${norm.slice(0, 3)} ${norm.slice(3, 5)} ${norm.slice(5, 8)} ${norm.slice(8)}`;
  }
  return norm;
}
