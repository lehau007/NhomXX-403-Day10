# Báo Cáo Nhóm — Lab Day 10: Data Pipeline & Data Observability

**Tên nhóm:** Nhóm 3 người (Sprint 4)  
**Thành viên:**
| Tên | Vai trò (Day 10) | Email |
|-----|------------------|-------|
| Hậu | Ingestion / Monitoring / Ops ||
| Hào | Cleaning & Quality Owner ||
| Tú | Embed & Idempotency Owner ||

**Ngày nộp:** 2026-04-15  
**Repo:** VinUni/lab10/
**Độ dài khuyến nghị:** 600–1000 từ

---

## 1. Pipeline tổng quan (150–200 từ)

**Tóm tắt luồng:**
Pipeline thực hiện qua 4 giai đoạn chính: 
1. **Ingest**: Đọc dữ liệu thô từ `data/raw/policy_export_dirty.csv`, khởi tạo `run_id` và manifest để theo dõi dòng dữ liệu (lineage).
2. **Transform**: Áp dụng các quy tắc làm sạch (Cleaning Rules) như chuẩn hóa ngày tháng, xử lý trùng lặp và sửa lỗi nghiệp vụ (refund window). Các bản ghi lỗi được đẩy vào thư mục `quarantine`.
3. **Quality**: Kiểm tra các kỳ vọng dữ liệu (Expectations). Nếu vi phạm mức độ `halt`, pipeline sẽ dừng lại để bảo vệ tính toàn vẹn của Vector DB.
4. **Embed**: Thực hiện embedding dữ liệu sạch vào ChromaDB một cách idempotent (upsert theo `chunk_id` và xóa các bản ghi cũ không còn tồn tại).

**Lệnh chạy một dòng (copy từ README thực tế của nhóm):**
`python etl_pipeline.py run && python etl_pipeline.py freshness --manifest artifacts/manifests/manifest_sprint3-after-fix.json`

---

## 2. Cleaning & expectation (150–200 từ)

### 2a. Bảng metric_impact (bắt buộc — chống trivial)

| Rule / Expectation mới (tên ngắn) | Trước (số liệu) | Sau / khi inject (số liệu) | Chứng cứ (log / CSV / commit) |
|-----------------------------------|------------------|-----------------------------|-------------------------------|
| `fix_refund_window` (14 to 7) | 10 raw | 6 cleaned, 4 quarantine | `manifest_sprint3-after-fix.json` |
| `stale_hr_policy_filter` | 10 raw | 4 quarantine | `quarantine_sprint3-after-fix.csv` |

---

## 3. Before / after ảnh hưởng retrieval hoặc agent (200–250 từ)

**Kịch bản inject:**
Chúng tôi đã thực hiện inject lỗi bằng cách chạy pipeline với cờ `--no-refund-fix`. Điều này khiến quy tắc sửa cửa sổ hoàn trả từ 14 ngày về 7 ngày bị bỏ qua, dẫn đến việc Agent trả về thông tin sai lệch cho khách hàng.

**Kết quả định lượng (từ CSV / bảng):**
Dựa trên file đánh giá `artifacts/eval/sprint4_m1_eval.csv`, sau khi áp dụng đầy đủ các Cleaning Rules:
- **Câu hỏi `q_refund_window`**: Trả về chính xác "7 ngày làm việc" (Top-1: `policy_refund_v4`).
- **Câu hỏi `q_leave_version`**: Trả về chính xác "12 ngày phép" theo chính sách 2026, thay vì 10 ngày như bản cũ.
- **Trạng thái**: `contains_expected: yes` và `hits_forbidden: no` cho tất cả các câu hỏi quan trọng.

---

## 4. Freshness & monitoring (100–150 từ)

**Kết quả Monitoring:**
Mặc dù chất lượng dữ liệu đạt chuẩn, hệ thống giám sát vẫn báo trạng thái **FAIL** cho `run-id: sprint4-final`.
- **Phân tích**: Độ trễ đạt ~121 giờ do giá trị `latest_exported_at` bị cố định ở ngày 2026-04-10 trong metadata của hệ thống nguồn.
- **Hành động Ops**: Đã xác nhận dữ liệu bên trong là mới nhất thông qua Retrieval Test. Khuyến nghị đội Ingestion cập nhật lại quy trình export để metadata phản ánh đúng thời gian thực tế.

---

## 5. Liên hệ Day 09 (50–100 từ)

Dữ liệu sau khi embed vào `day10_kb` đã sẵn sàng để phục vụ cho Multi-agent Day 09. Nhờ tính năng `prune_strategy: snapshot`, chúng tôi đảm bảo Agent không bao giờ đọc phải các phiên bản chính sách cũ (như bản 14 ngày refund), giúp tăng độ tin cậy của chatbot hỗ trợ khách hàng.


---

## 6. Rủi ro còn lại & việc chưa làm
- **Thiếu cơ chế Auto-rollback:** Hiện tại nếu pipeline chạy thành công nhưng dữ liệu embed có chất lượng retrieval thấp (đo qua eval), hệ
thống vẫn chưa tự động quay lại (rollback) phiên bản Vector DB trước đó mà cần sự can thiệp thủ công của Ops.
- **Xử lý Schema Evolution:** Các quy tắc làm sạch (Cleaning Rules) hiện tại đang được hard-code. Nếu cấu trúc file CSV đầu vào thay đổi
(thêm/bớt cột), pipeline có thể bị lỗi nghiêm trọng. Cần chuyển sang cơ chế cấu trúc hóa qua cấu hình (configuration-driven).
- **Giám sát Drift:** Mới chỉ đo được Freshness (độ tươi) và Schema, chưa đo được Data Drift (sự thay đổi phân phối nội dung) vốn rất quan
trọng để đảm bảo Agent không bị "hallucination" theo thời gian.
- **Tích hợp CI/CD:** Quy trình kiểm tra `instructor_quick_check.py` và `grading_run.py` hiện tại đang chạy thủ công. Cần tích hợp vào GitHub
Actions để tự động hóa việc chấm điểm và kiểm tra chất lượng mỗi khi có commit mới.