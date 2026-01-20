# CIC LightRAG Telegram Chatbot

Dự án chatbot Telegram thông minh tích hợp **LightRAG** và **n8n**, sử dụng **Supabase** làm backend lưu trữ tri thức.

## Thành phần hệ thống
- **LightRAG API**: Dịch vụ FastAPI xử lý truy vấn Knowledge Graph và nạp dữ liệu.
- **Supabase**: Lưu trữ Vector Embeddings (pgvector) và Graph data.
- **n8n**: Điều phối luồng (Orchestration), nhận tin nhắn và file từ Telegram.

## Hướng dẫn cài đặt

### 1. Server LightRAG
- Cài đặt thư viện: `pip install -r requirements.txt`
- Cấu hình biến môi trường trong file `.env`:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `DB_CONNECTION_STRING`
- Chạy server: `python lightrag_api_supabase.py`

### 2. n8n Workflow
- Import file `n8n_telegram_lightrag.json` vào n8n.
- Cấu hình Telegram Bot Token và OpenAI API Key.

## Tính năng
- [x] Trả lời câu hỏi thông minh (Hybrid Search: Graph + Vector).
- [x] Nạp dữ liệu tự động từ file (PDF, Docx, TXT) gửi qua Telegram.
- [x] Lưu trữ tri thức tập trung trên Supabase.
- [x] Hỗ trợ triển khai nhanh lên Railway/Render.
