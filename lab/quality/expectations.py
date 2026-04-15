"""
Expectation suite đơn giản (không bắt buộc Great Expectations).

Sinh viên có thể thay bằng GE / pydantic / custom — miễn là có halt có kiểm soát.

Sprint 2 Extensions by Member 2 (M2):
- E7: No Null in Critical Fields - đảm bảo các field bắt buộc không null/empty
- E8: Date Range Validation - effective_date phải trong khoảng hợp lý (2025-2027)
- E9 (Distinction): Pydantic Schema Validation - type-safe validation với auto error messages
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

try:
    from pydantic import BaseModel, Field, validator, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


@dataclass
class ExpectationResult:
    name: str
    passed: bool
    severity: str  # "warn" | "halt"
    detail: str


# Sprint 2 - E9: Pydantic Model for Schema Validation (Distinction level)
if PYDANTIC_AVAILABLE:
    class CleanedChunkSchema(BaseModel):
        """
        Pydantic model for cleaned chunk validation.
        Provides type-safe validation with automatic error messages.
        """
        chunk_id: str = Field(..., min_length=1, description="Unique chunk identifier")
        doc_id: str = Field(..., min_length=1, description="Document identifier")
        chunk_text: str = Field(..., min_length=8, max_length=500, description="Chunk content")
        effective_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="ISO date format")
        exported_at: str = Field(..., min_length=1, description="Export timestamp")
        
        @validator('effective_date')
        def validate_date_range(cls, v):
            """Validate effective_date is within reasonable range (2025-2027)"""
            if v < "2025-01-01" or v > "2027-12-31":
                raise ValueError(f"effective_date {v} outside valid range 2025-2027")
            return v
        
        @validator('chunk_text')
        def validate_no_bom(cls, v):
            """Ensure no BOM or invisible characters remain"""
            if '\ufeff' in v or '\u200b' in v:
                raise ValueError("chunk_text contains BOM or invisible characters")
            return v
        
        class Config:
            extra = 'allow'  # Allow extra fields like metadata


def run_expectations(cleaned_rows: List[Dict[str, Any]]) -> Tuple[List[ExpectationResult], bool]:
    """
    Trả về (results, should_halt).

    should_halt = True nếu có bất kỳ expectation severity halt nào fail.
    """
    results: List[ExpectationResult] = []

    # E1: có ít nhất 1 dòng sau clean
    ok = len(cleaned_rows) >= 1
    results.append(
        ExpectationResult(
            "min_one_row",
            ok,
            "halt",
            f"cleaned_rows={len(cleaned_rows)}",
        )
    )

    # E2: không doc_id rỗng
    bad_doc = [r for r in cleaned_rows if not (r.get("doc_id") or "").strip()]
    ok2 = len(bad_doc) == 0
    results.append(
        ExpectationResult(
            "no_empty_doc_id",
            ok2,
            "halt",
            f"empty_doc_id_count={len(bad_doc)}",
        )
    )

    # E3: policy refund không được chứa cửa sổ sai 14 ngày (sau khi đã fix)
    bad_refund = [
        r
        for r in cleaned_rows
        if r.get("doc_id") == "policy_refund_v4"
        and "14 ngày làm việc" in (r.get("chunk_text") or "")
    ]
    ok3 = len(bad_refund) == 0
    results.append(
        ExpectationResult(
            "refund_no_stale_14d_window",
            ok3,
            "halt",
            f"violations={len(bad_refund)}",
        )
    )

    # E4: chunk_text đủ dài
    short = [r for r in cleaned_rows if len((r.get("chunk_text") or "")) < 8]
    ok4 = len(short) == 0
    results.append(
        ExpectationResult(
            "chunk_min_length_8",
            ok4,
            "warn",
            f"short_chunks={len(short)}",
        )
    )

    # E5: effective_date đúng định dạng ISO sau clean (phát hiện parser lỏng)
    iso_bad = [
        r
        for r in cleaned_rows
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", (r.get("effective_date") or "").strip())
    ]
    ok5 = len(iso_bad) == 0
    results.append(
        ExpectationResult(
            "effective_date_iso_yyyy_mm_dd",
            ok5,
            "halt",
            f"non_iso_rows={len(iso_bad)}",
        )
    )

    # E6: không còn marker phép năm cũ 10 ngày trên doc HR (conflict version sau clean)
    bad_hr_annual = [
        r
        for r in cleaned_rows
        if r.get("doc_id") == "hr_leave_policy"
        and "10 ngày phép năm" in (r.get("chunk_text") or "")
    ]
    ok6 = len(bad_hr_annual) == 0
    results.append(
        ExpectationResult(
            "hr_leave_no_stale_10d_annual",
            ok6,
            "halt",
            f"violations={len(bad_hr_annual)}",
        )
    )

    # Sprint 2 - E7: No Null in Critical Fields
    critical_fields = ["chunk_id", "doc_id", "chunk_text", "effective_date"]
    null_violations = []
    for idx, r in enumerate(cleaned_rows):
        for field in critical_fields:
            if not (r.get(field) or "").strip():
                null_violations.append(f"row_{idx}_{field}")
    ok7 = len(null_violations) == 0
    results.append(
        ExpectationResult(
            "no_null_critical_fields",
            ok7,
            "halt",
            f"null_violations={len(null_violations)} fields={', '.join(null_violations[:5])}",
        )
    )

    # Sprint 2 - E8: Date Range Validation
    # effective_date phải trong khoảng hợp lý (2025-01-01 đến 2027-12-31)
    date_range_violations = [
        r
        for r in cleaned_rows
        if (r.get("effective_date") or "") < "2025-01-01"
        or (r.get("effective_date") or "") > "2027-12-31"
    ]
    ok8 = len(date_range_violations) == 0
    results.append(
        ExpectationResult(
            "effective_date_range_2025_2027",
            ok8,
            "warn",
            f"out_of_range={len(date_range_violations)}",
        )
    )

    # Sprint 2 - E9: Pydantic Schema Validation (Distinction level)
    if PYDANTIC_AVAILABLE:
        pydantic_result = _run_pydantic_validation(cleaned_rows)
        results.append(pydantic_result)

    halt = any(not r.passed and r.severity == "halt" for r in results)
    return results, halt


def _run_pydantic_validation(cleaned_rows: List[Dict[str, Any]]) -> ExpectationResult:
    """
    Sprint 2 - E9: Pydantic Schema Validation (Distinction level)
    
    Validates all cleaned rows against Pydantic schema.
    Provides detailed type-safe validation with automatic error messages.
    """
    if not PYDANTIC_AVAILABLE:
        return ExpectationResult(
            "pydantic_schema_validation",
            True,
            "warn",
            "pydantic not installed, skipping schema validation"
        )
    
    errors = []
    for idx, row in enumerate(cleaned_rows):
        try:
            CleanedChunkSchema(**row)
        except ValidationError as e:
            errors.append(f"row_{idx}: {e.errors()[0]['msg']}")
            if len(errors) >= 5:  # Limit error messages
                errors.append(f"... and {len(cleaned_rows) - idx - 1} more rows")
                break
    
    passed = len(errors) == 0
    detail = f"validated_rows={len(cleaned_rows)}, errors={len(errors)}"
    if errors:
        detail += f" | first_errors: {'; '.join(errors[:3])}"
    
    return ExpectationResult(
        "pydantic_schema_validation",
        passed,
        "halt",
        detail
    )
