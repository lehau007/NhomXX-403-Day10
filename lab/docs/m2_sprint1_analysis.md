# Phân tích Dữ liệu Raw - Member 2 (Sprint 1)

**Người thực hiện:** Member 2 (Data Quality Engineer)  
**Sprint:** 1  
**Ngày phân tích:** 2026-04-15  
**File phân tích:** `lab/data/raw/policy_export_dirty.csv`

---

## 1. Tổng quan Dữ liệu Raw

**Tổng số dòng:** 10 dòng (bao gồm header)  
**Số dòng dữ liệu:** 9 dòng  
**Cấu trúc:** CSV với 5 cột: `chunk_id`, `doc_id`, `chunk_text`, `effective_date`, `exported_at`

---

## 2. Các Loại "Rác" Đã Phát Hiện

### 2.1. **Duplicate Records (Dòng Trùng Lặp)**
- **Vị trí:** Dòng 1 và 2
- **Mô tả:** Hai dòng có nội dung `chunk_text` hoàn toàn giống nhau
- **Nội dung:** "Yêu cầu được gửi trong vòng 7 ngày làm việc kể từ thời điểm xác nhận đơn hàng."
- **Impact:** Gây duplicate trong vector database, lãng phí storage
- **Xử lý:** Giữ dòng đầu tiên, quarantine dòng thứ hai

### 2.2. **Empty/Missing Data (Dữ liệu Rỗng)**
- **Vị trí:** Dòng 5
- **Mô tả:** 
  - `chunk_text` rỗng hoàn toàn
  - `effective_date` rỗng
- **Impact:** Không thể embedding, không có giá trị nghiệp vụ
- **Xử lý:** Quarantine với reason `missing_chunk_text` hoặc `missing_effective_date`

### 2.3. **Invalid Date Format (Định dạng Ngày Sai)**
- **Vị trí:** Dòng 10
- **Mô tả:** `effective_date` = "01/02/2026" (format DD/MM/YYYY thay vì YYYY-MM-DD)
- **Impact:** Không parse được, gây lỗi khi query theo date
- **Xử lý:** Cần normalize sang ISO format (2026-02-01) hoặc quarantine nếu không parse được

### 2.4. **Stale/Outdated Version (Phiên bản Cũ)**

#### 2.4.1. HR Leave Policy (Chính sách Phép Năm Cũ)
- **Vị trí:** Dòng 7
- **Mô tả:** 
  - Nội dung: "10 ngày phép năm (bản HR 2025)"
  - `effective_date` = "2025-01-01" (< 2026-01-01)
- **Impact:** Conflict với policy mới (12 ngày), gây nhầm lẫn cho user
- **Xử lý:** Quarantine vì `effective_date < 2026-01-01` cho doc_id = `hr_leave_policy`

#### 2.4.2. Refund Policy Window (Cửa sổ Hoàn tiền Sai)
- **Vị trí:** Dòng 3
- **Mô tả:** 
  - Nội dung chứa "14 ngày làm việc" (policy v3 cũ)
  - Có ghi chú: "(ghi chú: bản sync cũ policy-v3 — lỗi migration)"
- **Impact:** Sai lệch với policy v4 hiện tại (7 ngày), vi phạm data contract
- **Xử lý:** Cần fix/replace "14 ngày" → "7 ngày" hoặc quarantine

### 2.5. **Unknown/Invalid doc_id (Catalog Không Hợp Lệ)**
- **Vị trí:** Dòng 9
- **Mô tả:** `doc_id` = "legacy_catalog_xyz_zzz" (không nằm trong allowlist)
- **Allowlist hợp lệ:** 
  - `policy_refund_v4`
  - `sla_p1_2026`
  - `it_helpdesk_faq`
  - `hr_leave_policy`
- **Impact:** Dữ liệu từ nguồn không xác định, không đáng tin cậy
- **Xử lý:** Quarantine với reason `unknown_doc_id`

---

## 3. Thống Kê Tổng Hợp

| Loại Lỗi | Số Lượng | % Tổng | Severity |
|-----------|----------|--------|----------|
| Duplicate | 1 | 11.1% | Medium |
| Empty Data | 1 | 11.1% | High |
| Invalid Date Format | 1 | 11.1% | Medium |
| Stale HR Policy | 1 | 11.1% | High |
| Stale Refund Window | 1 | 11.1% | Critical |
| Unknown doc_id | 1 | 11.1% | High |
| **Clean Records** | **3** | **33.3%** | - |
| **Total** | **9** | **100%** | - |

**Dự kiến sau cleaning:** 3-4 dòng clean (tùy thuộc vào việc fix hay quarantine stale refund)

---

## 4. Kế Hoạch Cleaning Rules Mở Rộng (Sprint 2)

Dựa trên phân tích trên, M2 sẽ thêm **≥3 rules mới** vào `transform/cleaning_rules.py`:

### Rule 1: **BOM/Special Character Removal**
- **Mục đích:** Loại bỏ BOM (Byte Order Mark) và ký tự đặc biệt không nhìn thấy
- **Metric Impact:** Giảm encoding errors, cải thiện embedding quality
- **Implementation:** Strip BOM (\ufeff), normalize unicode

### Rule 2: **Text Length Validation**
- **Mục đích:** Đảm bảo chunk_text có độ dài hợp lý (không quá ngắn/dài)
- **Metric Impact:** Tăng retrieval precision, giảm noise
- **Implementation:** 
  - Min length: 8 characters (đã có trong expectations)
  - Max length: 500 characters (tránh chunk quá dài)
  - Quarantine nếu vi phạm

### Rule 3: **Font/Character Normalization**
- **Mục đích:** Chuẩn hóa font chữ (full-width → half-width), dấu câu
- **Metric Impact:** Cải thiện search/matching accuracy
- **Implementation:** 
  - Normalize Vietnamese diacritics
  - Convert full-width numbers/letters → ASCII
  - Standardize punctuation

### Rule 4 (Bonus): **Metadata Consistency Check**
- **Mục đích:** Đảm bảo `exported_at` không trước `effective_date`
- **Metric Impact:** Phát hiện data corruption sớm
- **Implementation:** Parse cả 2 dates, compare logic

---

## 5. Kế Hoạch Expectations Mở Rộng (Sprint 2)

Thêm **≥2 expectations mới** vào `quality/expectations.py`:

### Expectation 1: **No Null in Critical Fields**
- **Check:** `chunk_id`, `doc_id`, `chunk_text`, `effective_date` không được null/empty sau clean
- **Severity:** HALT
- **Reason:** Các field này bắt buộc theo data contract

### Expectation 2: **Date Range Validation**
- **Check:** `effective_date` phải nằm trong khoảng hợp lý (2025-01-01 đến 2027-12-31)
- **Severity:** WARN
- **Reason:** Phát hiện date parsing errors hoặc data từ tương lai/quá khứ xa

### Expectation 3 (Bonus - Distinction): **Pydantic Schema Validation**
- **Check:** Validate toàn bộ schema bằng Pydantic Model
- **Severity:** HALT
- **Reason:** Type-safe validation, tự động generate error messages

---

## 6. Evidence & Screenshots (Chuẩn bị cho Report)

### 6.1. Raw Data Sample
```csv
chunk_id,doc_id,chunk_text,effective_date,exported_at
1,policy_refund_v4,"Yêu cầu được gửi trong vòng 7 ngày...",2026-02-01,2026-04-10T08:00:00
2,policy_refund_v4,"Yêu cầu được gửi trong vòng 7 ngày...",2026-02-01,2026-04-10T08:00:00  ← DUPLICATE
5,policy_refund_v4,"",,2026-04-10T08:00:00  ← EMPTY
```

### 6.2. Quarantine Reasons Mapping
| Reason Code | Description | Count |
|-------------|-------------|-------|
| `duplicate_chunk_text` | Trùng nội dung | 1 |
| `missing_chunk_text` | Text rỗng | 1 |
| `missing_effective_date` | Date rỗng | 0 |
| `invalid_effective_date_format` | Date format sai | 1 |
| `stale_hr_policy_effective_date` | HR policy cũ | 1 |
| `unknown_doc_id` | doc_id không hợp lệ | 1 |

---

## 7. Action Items cho Sprint 2

- [ ] Implement 3 cleaning rules mới trong `cleaning_rules.py`
- [ ] Thêm docstring chi tiết cho mỗi rule (giải thích metric_impact)
- [ ] Implement 2 expectations mới trong `expectations.py`
- [ ] Test với file raw, verify quarantine file có đúng 5-6 dòng
- [ ] Chụp screenshot log output để đưa vào report
- [ ] (Distinction) Cài đặt Pydantic validation model

---

## 8. Coordination với Team

### Cần từ M1 (Ingestion):
- Confirm file raw path và encoding (UTF-8)
- Log format để M2 có thể trace quarantine reasons

### Cần từ M3 (Embed):
- Confirm chunk_id format để đảm bảo idempotency
- Feedback về chunk length optimal cho embedding

### Gửi cho M1 & M3:
- Document này để sync về data quality issues
- List các quarantine reasons để họ hiểu pipeline behavior

---

**Kết luận Sprint 1 (M2):**  
Đã phân tích xong 6 loại lỗi chính trong raw data. Sẵn sàng implement cleaning rules và expectations trong Sprint 2. Dự kiến quality rate sau clean: ~33-44% (3-4/9 dòng pass).
