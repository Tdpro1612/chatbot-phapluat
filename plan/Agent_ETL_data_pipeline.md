# ĐẶC TẢ HỆ THỐNG MULTI-AGENT DATA PIPELINE (ETL & INGESTION)

Hệ thống ETL ngoại tuyến (Offline Pipeline) được vận hành bởi **3 Agent chuyên trách**, hoạt động tuần tự để chuyển hóa tài liệu thô thành cơ sở dữ liệu tri thức pháp lý sẵn sàng phục vụ API.

---

## AGENT 1: LEGAL PARSER & ENRICHMENT AGENT (Agent Trích xuất & Làm giàu Metadata)

*   **Chức năng chính:** 
    *   Đọc file `.docx`, bóc tách cấu trúc phân cấp (Chương, Điều, Khoản) dựa trên Heading.
    *   Duyệt qua từng khối điều luật, sử dụng LLM kết hợp Pydantic Schema để trích xuất bộ **Rich Metadata** chuẩn hóa (bao gồm: phân loại loại trách nhiệm dân sự/hình sự, phân nhóm hành vi đa cấp, định lượng hình phạt, hậu quả pháp lý gồm ngồi tù/bồi thường/xin lỗi, và cờ nhận diện tình tiết tăng nặng/giảm nhẹ hoặc quy định chung).
*   **Input:** 
    *   4 file tài liệu luật gốc dạng `.docx`.
    *   Quy chuẩn JSON Schema định nghĩa cấu trúc metadata tiếng Việt không dấu (`nguon_luat`, `phan_tich_hanh_vi`, `hau_qua_va_che_tai`, `cap_do_ap_dung`...).
*   **Output:** 
    *   Danh sách các tệp dữ liệu trung gian dạng `.json` sạch, đã được cấu trúc phân tầng (Hỗ trợ cả Parent Chunk cấp Điều và Child Chunks cấp Khoản đối với các điều có khung hình phạt phân tầng như tội trộm cắp).Dưới đây là json mẫu
    ```json
        {
    // Phân loại cấp độ áp dụng để phân biệt các parent hay child : có thể có chương, điều, tiểu mục,khoản ....
    "chunk_id": "blhs_2015_chuong_xiv_dieu_173",
    "nguon_luat": "Bộ luật Hình sự 2015",
    "pham_vi_chuong": "Chương XIV: Các tội xâm phạm sở hữu",
    "so_hieu_dieu": "Điều 173",
    "tieu_de_dieu": "Điều 173. Tội trộm cắp tài sản",
    "loai_trach_nhiem": "Hình sự", // Phân định rõ: Hình sự hoặc Dân sự

    // Phân loại cấp độ áp dụng để phân biệt điều luật chung hay tội danh cụ thể
    "cap_do_ap_dung": {
        "pham_vi": "Tội danh cụ thể", // Hoặc "Quy định chung" (như Điều 51, 52...)
        "nhom_toi": "Các tội phạm xâm phạm sở hữu"
    },

    // Hệ thống phân loại nhóm hành vi đa cấp (Taxonomy) để tránh đứt gãy từ vựng
    "nhom_hanh_vi": {
        "loai_loi": "Cố ý", // "Cố ý" hoặc "Vô ý"
        "doi_tuong_tac_dong": "Tài sản / Tổ chức hoặc cá nhân",
        "hanh_vi_loi_chuan_hoa": "TROM_CAP_LEN_LUT"
    },

    "phan_tich_hanh_vi_chi_tiet": {
        "ten_hanh_vi": "Lén lút chiếm đoạt tài sản của người khác",
        "dac_diem_nhan_dang": [
        "Tính chất lén lút (chủ sở hữu không biết tại thời điểm chiếm đoạt)",
        "Không sử dụng vũ lực ngay lập tức"
        ],
        "phan_biet_voi_toi_khac": "Khác với cướp tài sản (có vũ lực/công khai)"
    },

    // Phân tầng hậu quả và chế tài (Bao gồm Hình sự, Dân sự và Phục hồi danh dự/nhân phẩm)
    "hau_qua_va_che_tai": {
        "hinh_su": {
        "hinh_phat_chinh": ["Phạt tiền", "Cải tạo không giam giữ", "Phạt tù có thời hạn"],
        "hinh_phat_bo_sung": ["Phạt tiền bổ sung", "Cấm đảm nhiệm chức vụ"],
        "muc_phat_thap_nhat": "Phạt cải tạo không giam giữ đến 03 năm hoặc phạt tù từ 06 tháng",
        "muc_phat_cao_nhat": "Phạt tù đến 20 năm"
        },
        "dan_su_va_khac": {
        "buoc_boi_thuong_thiet_hai": true,
        "buoc_kho_phuc_tinh_trang_ban_dau": true,
        "buoc_cong_khai_xin_loi": false,
        "che_tai_khac": "Buộc hoàn trả tài sản chiếm đoạt"
        }
    },

    // Phân tầng chi tiết theo Khoản (Giải quyết bài toán khung hình phạt khác nhau theo định lượng tài sản)
    "chi_tiet_cac_khoan": [
        {
        "khoan": "Khoản 1",
        "dieu_kien_dinh_luong": "Tài sản trị giá từ 2.000.000 đồng đến dưới 50.000.000 đồng",
        "che_tai_rieng": "Phạt cải tạo không giam giữ đến 03 năm hoặc phạt tù từ 06 tháng đến 03 năm"
        },
        {
        "khoan": "Khoản 2",
        "dieu_kien_dinh_luong": "Tài sản trị giá từ 50.000.000 đồng đến dưới 200.000.000 đồng",
        "che_tai_rieng": "Phạt tù từ 02 năm đến 07 năm"
        }
        // ... các khoản tiếp theo
    ],

    // Cờ đánh dấu tình tiết tăng nặng / giảm nhẹ riêng của điều luật này (nếu có)
    "co_tinh_tiet_tang_nang_giam_nhe": true,
    "tinh_tiet_tang_nang_giam_nhe": {
        "tang_nang_rieng_cua_dieu": ["Có tổ chức", "Chuyên nghiệp", "Dùng thủ đoạn xảo quyệt"],
        "giam_nhe_nhan_than_chung_lien_quan": ["Điều 51 (Tình tiết giảm nhẹ chung)", "Điều 54 (Quyết định hình phạt dưới khung)"]
    },

    "noi_dung_goc": "1. Người nào trộm cắp tài sản trị giá từ 2.000.000 đồng đến dưới 50.000.000 đồng..."
    }
    ```

---

## AGENT 2: GRAPH & VECTOR INDEXING AGENT (Agent Xây dựng Cơ sở dữ liệu Tri thức)

*   **Chức năng chính:** 
    *   Nhận dữ liệu JSON đã có metadata từ Agent 1.
    *   Sử dụng **LlamaIndex** để thiết lập các mô hình Indexing nâng cao:
        *   Tạo Vector Embedding cho nội dung văn bản kèm theo payload metadata đầy đủ, sau đó đẩy xuống **Vector Database (Qdrant)**.
        *   Phát hiện các mối quan hệ pháp lý chéo (ví dụ: các điều luật viện dẫn lẫn nhau, mối quan hệ giữa "Quy định chung" như Điều 51/52 với các "Tội danh cụ thể"), sau đó cấu trúc và đẩy các quan hệ này vào **Graph Database (Neo4j)** để tạo mạng lưới GraphRAG.
*   **Input:** 
    *   Thư mục chứa các file `.json` đã chuẩn hóa metadata từ Agent 1.
    *   Cấu hình kết nối tới Vector DB (Qdrant) và Graph DB (Neo4j).
*   **Output:** 
    *   Hệ thống cơ sở dữ liệu hợp nhất (`data_law.db` bao gồm Vector Store index và Graph Database) đã sẵn sàng hoạt động tối ưu cho việc truy vấn có điều kiện.

---

## AGENT 3: API SERVICE & EXPOSURE AGENT (Agent Đóng gói và Phơi bày Endpoint)

*   **Chức năng chính:** 
    *   Xây dựng tầng giao tiếp chuẩn hóa bằng **FastAPI** để đóng gói toàn bộ logic truy xuất dữ liệu từ LlamaIndex/Qdrant/Neo4j.
    *   Thiết kế các API Endpoints cho phép các hệ thống Chatbot/Runtime Agent bên ngoài gọi vào để khai thác dữ liệu pháp lý một cách linh hoạt (hỗ trợ cả lọc theo metadata, tìm kiếm ngữ nghĩa, lẫn mở rộng đồ thị tri thức).
*   **Input:** 
    *   Cơ sở dữ liệu tri thức đã hoàn thiện từ Agent 2 (`Qdrant Index` + `Neo4j Graph`).
    *   Định nghĩa các yêu cầu nghiệp vụ về tham số đầu vào cho API (ví dụ: lọc theo `loai_trach_nhiem`, `nhom_hanh_vi`, hoặc câu hỏi truy vấn thuần túy).
*   **Output:** 
    *   Hệ thống RESTful API hoàn chỉnh với các Endpoint chính:
        *   `POST /api/v1/legal/search`: Truy vấn kết hợp Hybrid Search + Metadata Pre-filtering.
        *   `POST /api/v1/legal/graph-expand`: Truy vấn mở rộng điều luật liên quan qua Knowledge Graph.
        *   `GET /api/v1/legal/article/{id}`: Tra cứu chi tiết một điều luật bằng mã định danh (`chunk_id`).