# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Nguyễn Bá Hào - 2A202600133
**Vai trò:** Cleaning & Quality Owner (Data Quality Engineer)
**Ngày nộp:** 2026-04-15
**Độ dài:** 400 - 650 từ

---

## 1. Phụ trách 

Tôi phụ trách các module làm sạch dữ liệu trong file `transform/cleaning_rules.py` (triển khai 4 quy tắc mới từ Rule 7–10) và xây dựng hệ thống kiểm soát chất lượng tại `quality/expectations.py` (bao gồm các bộ lọc E7–E9). Tôi kết nối chặt chẽ với Hậu (M1) để thống nhất cấu trúc dữ liệu đầu vào và cung cấp đầu ra sạch (cleaned CSV) cho Tú (M3) thực hiện embedding thông qua manifest.

**Bằng chứng:** Tôi đã thực hiện các commit `254c374` (Sprint 1) và `8aa35eb` (Sprint 2) trên nhánh `main`. Trong mã nguồn, tôi đã đánh dấu rõ các phần mở rộng bằng comment: `# Sprint 2, member 2`.

---

## 2. Quyết định kỹ thuật 

**Lựa chọn Severity cho Expectations:**
Tôi quyết định áp dụng mức độ **HALT** (dừng pipeline) cho Expectation E7 (No Null Critical Fields) và E9 (Pydantic Schema Validation). Lý do là vì nếu các trường như `chunk_id` hoặc `chunk_text` bị null hoặc sai kiểu dữ liệu, toàn bộ quá trình tạo vector sẽ tạo ra dữ liệu rác, gây sai lệch nghiêm trọng cho hệ thống retrieval. Ngược lại, tôi chọn mức **WARN** cho E8 (Date Range Validation 2025–2027) vì dữ liệu nằm ngoài khoảng này có thể là ngoại lệ nghiệp vụ hợp lệ cần hậu kiểm, không nên làm gián đoạn luồng xử lý ngay lập tức.

**Chiến lược Idempotency (Pruning):**
Tôi đã đề xuất và phối hợp cùng Tú (M3) triển khai logic **Prune vector**. Khi pipeline chạy lại, hệ thống sẽ tự động so sánh danh sách `ids` hiện tại và `prev_ids` cũ trong manifest để xóa bỏ các bản ghi không còn tồn tại. Điều này đảm bảo tính nhất quán: các chunk lỗi "14 ngày" sẽ biến mất hoàn toàn khỏi database ngay khi chúng bị loại bỏ khỏi file đã làm sạch.

---

## 3. Sự cố / Anomaly 

Trong kịch bản thử nghiệm với **run_id:  sprint3-inject-bad**, tôi đã thực hiện "cố ý" gây lỗi bằng cách disable Rule 6 (quy tắc sửa lỗi phiên bản hoàn tiền) và bỏ qua bước validate.

**Triệu chứng:** Kết quả đánh giá retrieval trả về `hits_forbidden=yes`. Khi truy vấn về chính sách hoàn tiền, người dùng nhận được thông tin mâu thuẫn: hệ thống trả về cả nội dung "7 ngày" (đúng) và "14 ngày" (sai - dữ liệu cũ chưa được dọn dẹp).

**Phát hiện:** Log của pipeline hiển thị lỗi xác thực:
`expectation[refund_no_stale_14d_window] FAIL (halt) :: violations=1`.

**Xử lý:** Tôi đã kích hoạt lại Rule 6 trong kịch bản `run_id: sprint3-after-fix`. Quy tắc này tự động phát hiện chuỗi "14 ngày" và sửa thành "7 ngày", đồng thời gắn thẻ định danh `[cleaned: stale_refund_window]`. Sau khi chạy lại, metric `hits_forbidden` đã trở về trạng thái `no`, khôi phục độ chính xác cho hệ thống.

---

## 4. Before/After 

Tôi đã đối soát dữ liệu giữa hai lần chạy thông qua các file evaluation thật của nhóm:

* **Trước khi sửa (Inject Bad):** Trong file `artifacts/eval/eval_inject_bad.csv`, dòng `q_refund_window` có kết quả `hits_forbidden=yes`, khiến chất lượng retrieval chỉ đạt **75%**.
* **Sau khi sửa (After Fix):** Trong file `eval_after_fix.csv`, câu hỏi `q_refund_window` đã trả về `hits_forbidden=no`.
* **Log Manifest:** Hệ thống xác nhận `embed_prune_removed=1`, chứng minh vector lỗi cũ đã bị xóa bỏ hoàn toàn. Toàn bộ 9/9 expectations của tôi đều đạt trạng thái **OK**.

---

## 5. Cải tiến thêm 2 giờ 

Nếu có thêm 2 giờ, tôi sẽ nâng cấp hệ thống đo lường **Freshness đa điểm**. Thay vì chỉ đo tại lúc publish, tôi sẽ ghi nhận thêm `ingest_timestamp` để tính toán độ trễ xử lý (processing lag) tách biệt với độ trễ của nguồn dữ liệu. Đồng thời, tôi sẽ chuyển các tham số cấu hình như `effective_date` sang file `data_contract.yaml` để tăng tính linh hoạt và dễ bảo trì cho pipeline.