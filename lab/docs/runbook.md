# Runbook — Lab Day 10 (incident tối giản)

---

## Symptom

> User / agent thấy gì?
- Agent trả lời thông tin cũ: Ví dụ, trả lời khách hàng về chính sách hoàn tiền là "14 ngày làm việc" (quy định cũ) thay vì "7 ngày làm việc" (quy định mới).
- Agent không tìm thấy tài liệu mới nhất (ví dụ: IT FAQ vừa cập nhật sáng nay nhưng agent vẫn báo không biết).
- Kết quả tìm kiếm (retrieval) chứa các ký tự lạ hoặc định dạng bị lỗi.

---

## Detection

> Metric nào báo?
- **Freshness FAIL**: Check manifest thấy `age_hours` vượt quá `SLA_HOURS` (ví dụ > 24h).
- **Expectation FAIL**: Pipeline bị dừng (HALT) ở bước `run_expectations` với lỗi `refund_no_stale_14d_window` hoặc `hr_leave_no_stale_10d_annual`.
- **Evaluation alert**: Chạy `eval_retrieval.py` thấy metric `hits_forbidden` > 0 (agent vẫn truy cập vào dữ liệu cũ/cấm).
- **Log error**: Kiểm tra `artifacts/logs/run_*.log` thấy báo lỗi `unknown_doc_id` hoặc `invalid_effective_date_format`.

---

## Diagnosis

| Bước | Việc làm | Kết quả mong đợi |
|------|----------|------------------|
| 1 | Kiểm tra `artifacts/manifests/*.json` | Xem `no_refund_fix` có đang là `true` không, hoặc `skipped_validate` có bị bật không. |
| 2 | Mở `artifacts/quarantine/*.csv` | Kiểm tra cột `reason`. Nếu thấy nhiều `stale_hr_policy_effective_date`, có nghĩa là source data đang gửi bản cũ. |
| 3 | Chạy `python etl_pipeline.py freshness --manifest artifacts/manifests/latest.json` | Xác định dữ liệu trễ bao nhiêu tiếng so với thực tế. |
| 4 | Chạy `python eval_retrieval.py` | Kiểm tra xem mô hình có đang bị "hallucinate" do context nhiễu (noise) từ các chunk quá ngắn/dài không. |

---

## Mitigation

- **Tức thời**: Rerun pipeline với flag mặc định (đảm bảo không có `--no-refund-fix`).
- **Data Cleanup**: Nếu `quarantine` quá nhiều do `unknown_doc_id`, cập nhật `ALLOWED_DOC_IDS` trong `cleaning_rules.py` nếu đó là tài liệu mới hợp lệ.
- **Rollback**: Xóa collection ChromaDB và rerun từ một bản export sạch gần nhất.
- **Manual Patch**: Nếu source data sai hàng loạt, sửa trực tiếp file CSV raw (chỉ dùng khi khẩn cấp) rồi rerun pipeline.

---

## Prevention

- **Expectations**: Luôn giữ severity `halt` cho các rules quan trọng như `refund_no_stale_14d_window`.
- **CI/CD Validation**: Tích hợp `run_expectations` vào quá trình push dữ liệu tự động.
- **Alerting**: Cài đặt cronjob chạy `freshness check` định kỳ và bắn alert qua Slack/Email nếu FAIL.
- **Guardrails**: Nối sang Day 11 để cài đặt lớp lọc Output (đảm bảo agent không bao giờ thốt ra con số "14 ngày" ngay cả khi retrieval lỗi).
