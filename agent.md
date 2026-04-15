# Project Architecture: Lab 10 - Data Pipeline & Data Observability

## 1. Overview
Dự án tập trung vào việc xây dựng một Data Pipeline tin cậy cho hệ thống RAG (Retrieval-Augmented Generation), nhấn mạnh vào tính quan sát được (Data Observability), chất lượng dữ liệu (Data Quality) và tính bất biến (Idempotency).

## 2. Directory Structure

### 📂 Root Directory
- `agent.md`: Tài liệu kiến trúc và hướng dẫn cho Agent (file này).
- `task.md`: Danh sách các đầu việc cụ thể chia theo Sprint (0-5).
- `team_plan.md`: Kế hoạch chi tiết của nhóm 3 người, phân công vai trò và DoD (Definition of Done).
- `readme.txt.txt`: Ghi chú bổ sung (nếu có).

### 📂 `day10-references/`
Chứa các tài liệu hướng dẫn, slide bài giảng và bản mẫu của Lab 10 để tham khảo.

### 📂 `lab/` (Khu vực thực thi chính)
Đây là nơi chứa toàn bộ mã nguồn và dữ liệu thực tế của dự án.

#### Core Scripts:
- `etl_pipeline.py`: Script điều phối chính (Ingest -> Transform -> Quality -> Embed).
- `eval_retrieval.py`: Đánh giá hiệu quả tìm kiếm (Retrieval Evaluation).
- `grading_run.py`: Script tạo file kết quả cuối cùng để chấm điểm.
- `instructor_quick_check.py`: Công cụ kiểm tra nhanh tính hợp lệ của output trước khi nộp.

#### Sub-packages:
- `transform/`: Chứa `cleaning_rules.py` (logic làm sạch dữ liệu).
- `quality/`: Chứa `expectations.py` (định nghĩa các ràng buộc chất lượng dữ liệu - GE style).
- `monitoring/`: Chứa `freshness_check.py` (kiểm tra tính cập nhật của dữ liệu).

#### Config & Data:
- `contracts/`: Định nghĩa `data_contract.yaml` (Schema, Owner, SLA).
- `data/`: 
    - `raw/`: Dữ liệu thô đầu vào (`.csv`).
    - `docs/`: Các tài liệu văn bản để index vào RAG.
- `artifacts/`: Lưu trữ đầu ra của pipeline (Cleaned data, Quarantine, Manifests, Logs).

#### Documentation:
- `docs/`: Tài liệu chi tiết về Architecture, Runbook, Data Contract, Quality Report.
- `reports/`: Báo cáo nhóm (`group_report.md`) và báo cáo cá nhân (`individual/`).

---

## 3. Tech Stack
- **Language:** Python 3.9+
- **Vector DB:** ChromaDB (Local)
- **Embedding:** Google Gemini Embedding API (`gemini-embedding-2`)
- **Validation:** Pydantic (cho mục tiêu Distinction) hoặc logic Python cơ bản.
- **Environment:** Quản lý qua `.venv` và `requirements.txt`.

---

## 4. Team Roles & Responsibilities
| Vai trò | Thành viên | Nhiệm vụ chính |
|---|---|---|
| **Data Engineer (Ingestion & Ops)** | Member 1 | Pipeline orchestration, Source management, Monitoring, Integration. |
| **Data Quality Engineer** | Member 2 | Cleaning rules, Data expectations, Quarantine logic, Quality reporting. |
| **AI/Embed Engineer** | Member 3 | Idempotent embedding, Retrieval evaluation, Architecture docs, Runbook. |

---

## 5. Key Workflows
1. **Research & Strategy:** Phân tích dữ liệu thô và định nghĩa Data Contract.
2. **Implementation:** Phát triển các Rule làm sạch và Expectation về chất lượng.
3. **Execution:** Chạy pipeline để tạo Artifacts (Manifest, Cleaned CSV, Vector DB).
4. **Validation:** Đánh giá Retrieval (Before vs After fix) và chạy script chấm điểm.
5. **Reporting:** Hoàn thiện hồ sơ tài liệu và báo cáo cá nhân.
