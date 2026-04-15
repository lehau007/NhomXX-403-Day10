# Data contract — Lab Day 10

> Bắt đầu từ `contracts/data_contract.yaml` — mở rộng và đồng bộ file này.

---

## 1. Nguồn dữ liệu (source map)

| Nguồn | Phương thức ingest | Failure mode chính | Metric / alert |
|-------|-------------------|-------------------|----------------|
| Policy Export CSV (policy_export_dirty.csv) | File-based batch ingest từ hệ thống nguồn | Duplicate records, missing dates, invalid doc_id, format không chuẩn ISO | `raw_records`, `quarantine_records` trong manifest |
| HR Leave Policy | Document ingestion từ data/docs/ | Version conflict (10 vs 12 ngày phép), effective_date cũ | `hr_leave_no_stale_10d_annual` expectation |
| Policy Refund v4 | Document ingestion từ data/docs/ | Stale refund window (14 vs 7 ngày), chunk text sai | `refund_no_stale_14d_window` expectation |
| IT Helpdesk FAQ | Document ingestion từ data/docs/ | Date format không chuẩn (DD/MM/YYYY thay vì ISO) | `effective_date_iso_yyyy_mm_dd` expectation |

---

## 2. Schema cleaned

| Cột | Kiểu | Bắt buộc | Ghi chú |
|-----|------|----------|---------|
| chunk_id | string | Có | ID ổn định sau clean (hash hoặc doc_id + seq), dùng cho idempotent embedding |
| doc_id | string | Có | Khóa logic tài liệu nguồn (vd: policy_refund_v4, hr_leave_policy) - phải nằm trong allowlist |
| chunk_text | string | Có | Nội dung chunk sau clean, min_length >= 8 ký tự |
| effective_date | date | Có | Ngày hiệu lực của policy/document, format ISO YYYY-MM-DD |
| exported_at | datetime | Có | Timestamp export từ hệ nguồn, dùng để tính freshness |

---

## 3. Quy tắc quarantine vs drop

> Record bị flag đi đâu? Ai approve merge lại?

**Quarantine rules:**
- Records với `doc_id` không nằm trong allowlist → quarantine (không được phép vào cleaned)
- Records với `chunk_text` rỗng hoặc null → quarantine
- Records duplicate (cùng chunk_text) → giữ 1 bản, các bản còn lại vào quarantine
- HR leave policy với effective_date < 2026-01-01 (version cũ 10 ngày) → quarantine
- Records với date format không chuẩn ISO (vd: DD/MM/YYYY) → quarantine sau khi thử convert

**Approval process:**
- Data Quality Engineer (Member 2) review quarantine file sau mỗi run
- Records hợp lệ nhưng bị quarantine do rule quá strict → điều chỉnh rule và re-run
- Records thực sự lỗi → báo cáo cho source system owner để fix upstream

---

## 4. Phiên bản & canonical

> Source of truth cho policy refund: file nào / version nào?

**Canonical sources:**
- **Policy Refund**: `data/docs/policy_refund_v4.txt` - Version 4 (7 ngày làm việc)
  - Mọi chunk chứa "14 ngày" trong refund context được coi là stale và phải fix thành "7 ngày"
- **HR Leave Policy**: Effective từ 2026-02-01 trở đi (12 ngày phép cho nhân viên < 3 năm)
  - Version cũ (10 ngày, effective < 2026-01-01) bị quarantine
- **SLA P1**: `data/docs/sla_p1_2026.txt` - SLA 2026 (15 phút response, 4 giờ resolution)
- **IT Helpdesk FAQ**: `data/docs/it_helpdesk_faq.txt` - FAQ cập nhật liên tục

**Version control:**
- Mọi thay đổi canonical source phải update `contracts/data_contract.yaml`
- Pipeline sử dụng `allowed_doc_ids` để enforce chỉ ingest từ canonical sources
- Freshness SLA: 24 giờ từ `exported_at` đến khi publish vào vector store
