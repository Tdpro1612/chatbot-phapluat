# KẾ HOẠCH TỔNG THỂ XÂY DỰNG HỆ THỐNG ETL VÀ DATABASE PHÁP LUẬT CHUYÊN SÂU

## 1. Tổng quan dự án
Dự án nhằm xây dựng một cơ sở dữ liệu pháp lý thông minh từ 4 bộ luật dạng `.docx` (đã phân chia heading). Hệ thống sử dụng kiến trúc Multi-Agent kết hợp **GraphRAG (LlamaIndex + Neo4j + Vector DB)** và hệ thống **Rich Metadata** đa chiều nhằm loại bỏ tình trạng RAG "mù", đảm bảo khả năng tra cứu chính xác hành vi, phân định trách nhiệm dân sự/hình sự, tình tiết tăng nặng/giảm nhẹ và quy tắc tổng hợp hình phạt.

---

## 2. Các bước triển khai chi tiết (Roadmap)

### Bước 1: Trích xuất và làm giàu dữ liệu bằng Multi-Agent ETL
*   **Mục tiêu:** Biến các file `.docx` thô thành dữ liệu cấu trúc sạch.
*   **Thực hiện:** Sử dụng hệ thống Agent tự động quét Heading (Chương, Điều, Khoản), bóc tách nội dung, phân loại nhóm hành vi (Taxonomy), gán nhãn trách nhiệm (Dân sự/Hình sự), xác định khung hình phạt, hậu quả (Hình sự + Dân sự + Khắc phục) và các tình tiết tăng nặng/giảm nhẹ (nếu có).
*   **Đầu ra:** Các file `.json` chuẩn hóa với bộ Metadata siêu chi tiết theo đúng thiết kế pháp lý.

### Bước 2: Xây dựng cơ sở dữ liệu nâng cao (LlamaIndex + Neo4j + Vector DB)
*   **Mục tiêu:** Thiết lập tầng lưu trữ tri thức có cấu trúc và mối quan hệ chéo.
*   **Thực hiện:** Sử dụng **LlamaIndex** làm framework điều phối trung tâm để:
    *   Đẩy nội dung văn bản và Vector Embedding xuống **Vector Database (ví dụ: Qdrant)** để phục vụ tìm kiếm ngữ nghĩa (Semantic Search) kết hợp Metadata Pre-filtering.
    *   Đẩy các mối quan hệ pháp lý (dẫn chiếu giữa các điều luật, quy định chung vs tội danh cụ thể) vào **Graph Database (Neo4j)** để xây dựng Đồ thị tri thức (Knowledge Graph), giải quyết bài toán móc nối điều luật phức tạp.
*   **Đầu ra:** Cơ sở dữ liệu hợp nhất sẵn sàng phục vụ truy vấn thời gian thực (`data_law.db` / cụm cluster lưu trữ).

### Bước 3: Đóng gói API/Endpoint phục vụ hệ thống Runtime Agent
*   **Mục tiêu:** Cung cấp giao diện giao tiếp chuẩn hóa để các ứng dụng Chatbot hoặc Agent tầng Runtime bên ngoài gọi vào khai thác.
*   **Thực hiện:** Xây dựng tầng API Gateway (Sử dụng FastAPI) bao bọc quanh hệ thống LlamaIndex Query Engine. Cung cấp các endpoint chuyên biệt cho việc:
    *   Tra cứu theo Metadata Filter (Lọc theo loại luật, nhóm hành vi, mức hình phạt).
    *   Truy vấn kết hợp GraphRAG (Lấy điều luật kèm theo các điều dẫn chiếu liên quan).
    *   Truy vấn phân tầng theo Khoản (Multi-tier chunking).

---

## 3. Kiến trúc công nghệ cốt lõi
*   **Data Processing:** Python (`python-docx`, Pydantic).
*   **Orchestration Framework:** LlamaIndex.
*   **Storage Layer:** Qdrant (Vector & Metadata Filter) + Neo4j (Graph Relations).
*   **Serving Layer:** FastAPI (RESTful API endpoints).