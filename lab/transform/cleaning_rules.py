"""
Cleaning rules — raw export → cleaned rows + quarantine.

Baseline gồm các failure mode mở rộng (allowlist doc_id, parse ngày, HR stale version).
Sinh viên thêm ≥3 rule mới: mỗi rule phải ghi `metric_impact` (xem README — chống trivial).

Sprint 2 Extensions by Member 2 (M2):
- Rule 7: BOM/Special Character Removal (metric_impact: giảm encoding errors, cải thiện embedding quality)
- Rule 8: Text Length Validation (metric_impact: tăng retrieval precision, giảm noise)
- Rule 9: Font/Character Normalization (metric_impact: cải thiện search/matching accuracy)
- Rule 10: Metadata Consistency Check (metric_impact: phát hiện data corruption sớm)
"""

from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Khớp export hợp lệ trong lab (mở rộng khi nhóm thêm doc mới — phải đồng bộ contract).
ALLOWED_DOC_IDS = frozenset(
    {
        "policy_refund_v4",
        "sla_p1_2026",
        "it_helpdesk_faq",
        "hr_leave_policy",
    }
)

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DMY_SLASH = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")

# Sprint 2 - M2: Constants for new rules
MAX_CHUNK_LENGTH = 500  # Maximum reasonable chunk length
MIN_CHUNK_LENGTH = 8    # Minimum chunk length (aligned with expectations)


def _norm_text(s: str) -> str:
    return " ".join((s or "").strip().split()).lower()


def _remove_bom_and_special_chars(text: str) -> str:
    """
    Rule 7: BOM/Special Character Removal
    
    Metric Impact: Giảm encoding errors, cải thiện embedding quality
    - Loại bỏ BOM (Byte Order Mark) \ufeff
    - Loại bỏ các ký tự control characters không nhìn thấy
    - Normalize unicode về dạng chuẩn NFC
    """
    if not text:
        return text
    
    # Remove BOM
    text = text.replace('\ufeff', '')
    
    # Remove other common invisible characters
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\u200c', '')  # Zero-width non-joiner
    text = text.replace('\u200d', '')  # Zero-width joiner
    text = text.replace('\ufeff', '')  # BOM
    
    # Normalize unicode to NFC (canonical composition)
    text = unicodedata.normalize('NFC', text)
    
    # Remove control characters except newline, tab, carriage return
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t\r')
    
    return text.strip()


def _normalize_font_and_punctuation(text: str) -> str:
    """
    Rule 9: Font/Character Normalization
    
    Metric Impact: Cải thiện search/matching accuracy
    - Convert full-width characters → half-width (ASCII)
    - Normalize Vietnamese diacritics
    - Standardize punctuation
    """
    if not text:
        return text
    
    # Normalize to NFKC (compatibility composition) - converts full-width to half-width
    text = unicodedata.normalize('NFKC', text)
    
    # Standardize common punctuation variations
    replacements = {
        '"': '"',  # Smart quotes to straight quotes
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
        '–': '-',  # En dash to hyphen
        '—': '-',  # Em dash to hyphen
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Normalize multiple spaces to single space
    text = ' '.join(text.split())
    
    return text.strip()


def _stable_chunk_id(doc_id: str, chunk_text: str, seq: int) -> str:
    h = hashlib.sha256(f"{doc_id}|{chunk_text}|{seq}".encode("utf-8")).hexdigest()[:16]
    return f"{doc_id}_{seq}_{h}"


def _normalize_effective_date(raw: str) -> Tuple[str, str]:
    """
    Trả về (iso_date, error_reason).
    iso_date rỗng nếu không parse được.
    """
    s = (raw or "").strip()
    if not s:
        return "", "empty_effective_date"
    if _ISO_DATE.match(s):
        return s, ""
    m = _DMY_SLASH.match(s)
    if m:
        dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
        return f"{yyyy}-{mm}-{dd}", ""
    return "", "invalid_effective_date_format"


def load_raw_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: (v or "").strip() for k, v in r.items()})
    return rows


def clean_rows(
    rows: List[Dict[str, str]],
    *,
    apply_refund_window_fix: bool = True,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Trả về (cleaned, quarantine).

    Baseline (mở rộng theo narrative Day 10):
    1) Quarantine: doc_id không thuộc allowlist (export lạ / catalog sai).
    2) Chuẩn hoá effective_date sang YYYY-MM-DD; quarantine nếu không parse được.
    3) Quarantine: chunk hr_leave_policy có effective_date < 2026-01-01 (bản HR cũ / conflict version).
    4) Quarantine: chunk_text rỗng hoặc effective_date rỗng sau chuẩn hoá.
    5) Loại trùng nội dung chunk_text (giữ bản đầu).
    6) Fix stale refund: policy_refund_v4 chứa '14 ngày làm việc' → 7 ngày.
    
    Sprint 2 Extensions (M2):
    7) Rule: BOM/Special Character Removal - loại bỏ BOM và ký tự đặc biệt
    8) Rule: Text Length Validation - quarantine nếu chunk quá ngắn (<8) hoặc quá dài (>500)
    9) Rule: Font/Character Normalization - chuẩn hóa full-width → half-width, punctuation
    10) Rule: Metadata Consistency Check - quarantine nếu exported_at < effective_date (data corruption)
    """
    quarantine: List[Dict[str, Any]] = []
    seen_text: set[str] = set()
    cleaned: List[Dict[str, Any]] = []
    seq = 0

    for raw in rows:
        doc_id = raw.get("doc_id", "")
        text = raw.get("chunk_text", "")
        eff_raw = raw.get("effective_date", "")
        exported_at = raw.get("exported_at", "")

        if doc_id not in ALLOWED_DOC_IDS:
            quarantine.append({**raw, "reason": "unknown_doc_id"})
            continue

        eff_norm, eff_err = _normalize_effective_date(eff_raw)
        if eff_err == "empty_effective_date":
            quarantine.append({**raw, "reason": "missing_effective_date"})
            continue
        if eff_err == "invalid_effective_date_format":
            quarantine.append({**raw, "reason": eff_err, "effective_date_raw": eff_raw})
            continue

        if doc_id == "hr_leave_policy" and eff_norm < "2026-01-01":
            quarantine.append(
                {
                    **raw,
                    "reason": "stale_hr_policy_effective_date",
                    "effective_date_normalized": eff_norm,
                }
            )
            continue

        if not text:
            quarantine.append({**raw, "reason": "missing_chunk_text"})
            continue

        # Sprint 2 - Rule 7: BOM/Special Character Removal
        text = _remove_bom_and_special_chars(text)
        
        # Sprint 2 - Rule 9: Font/Character Normalization
        text = _normalize_font_and_punctuation(text)
        
        # Re-check after cleaning
        if not text:
            quarantine.append({**raw, "reason": "empty_after_cleaning"})
            continue
        
        # Sprint 2 - Rule 8: Text Length Validation
        text_len = len(text)
        if text_len < MIN_CHUNK_LENGTH:
            quarantine.append({
                **raw,
                "reason": "chunk_too_short",
                "chunk_length": text_len,
                "min_required": MIN_CHUNK_LENGTH
            })
            continue
        
        if text_len > MAX_CHUNK_LENGTH:
            quarantine.append({
                **raw,
                "reason": "chunk_too_long",
                "chunk_length": text_len,
                "max_allowed": MAX_CHUNK_LENGTH
            })
            continue

        key = _norm_text(text)
        if key in seen_text:
            quarantine.append({**raw, "reason": "duplicate_chunk_text"})
            continue
        seen_text.add(key)

        # Sprint 2 - Rule 10: Metadata Consistency Check
        # exported_at không được trước effective_date (data corruption indicator)
        if exported_at and eff_norm:
            try:
                # Extract date part from exported_at (format: 2026-04-10T08:00:00)
                exported_date = exported_at.split('T')[0] if 'T' in exported_at else exported_at[:10]
                if exported_date < eff_norm:
                    quarantine.append({
                        **raw,
                        "reason": "metadata_inconsistency_exported_before_effective",
                        "exported_at": exported_at,
                        "effective_date": eff_norm
                    })
                    continue
            except Exception:
                # If parsing fails, log but don't quarantine (non-critical)
                pass

        fixed_text = text
        if apply_refund_window_fix and doc_id == "policy_refund_v4":
            if "14 ngày làm việc" in fixed_text:
                fixed_text = fixed_text.replace(
                    "14 ngày làm việc",
                    "7 ngày làm việc",
                )
                fixed_text += " [cleaned: stale_refund_window]"

        seq += 1
        cleaned.append(
            {
                "chunk_id": _stable_chunk_id(doc_id, fixed_text, seq),
                "doc_id": doc_id,
                "chunk_text": fixed_text,
                "effective_date": eff_norm,
                "exported_at": exported_at or "",
            }
        )

    return cleaned, quarantine


def write_cleaned_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("chunk_id,doc_id,chunk_text,effective_date,exported_at\n", encoding="utf-8")
        return
    fieldnames = ["chunk_id", "doc_id", "chunk_text", "effective_date", "exported_at"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def write_quarantine_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("chunk_id,doc_id,chunk_text,effective_date,exported_at,reason\n", encoding="utf-8")
        return
    keys: List[str] = []
    seen_k: set[str] = set()
    for r in rows:
        for k in r.keys():
            if k not in seen_k:
                seen_k.add(k)
                keys.append(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore", restval="")
        w.writeheader()
        for r in rows:
            w.writerow(r)
