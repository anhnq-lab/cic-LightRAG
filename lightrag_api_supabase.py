import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lightrag import LightRAG, QueryParam

# Cấu hình Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lightrag-api")

app = FastAPI(title="LightRAG CIC Enterprise API")

# Cấu hình Thư mục làm việc
WORKING_DIR = "./lightrag_cache"
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)

# Khởi tạo LightRAG với PostgreSQL Storage
# Lưu ý: Thư viện lightrag-hku sẽ tự động tìm các biến môi trường POSTGRES_...
# Nếu anh đã cấu hình POSTGRES_HOST, POSTGRES_USER, v.v. trên Railway/Render, 
# các lớp PGKVStorage, PGVectorStorage sẽ tự động kết nối.

try:
    rag = LightRAG(
        working_dir=WORKING_DIR,
        # Sử dụng PostgreSQL cho tất cả các loại lưu trữ
        kv_storage="PGKVStorage",
        vector_storage="PGVectorStorage",
        graph_storage="PGGraphStorage",
        doc_status_storage="PGDocStatusStorage",
        # Các tham số khác như LLM, Embedding sẽ lấy từ biến môi trường mặc định (OpenAI)
    )
    logger.info("LightRAG initialized successfully with PostgreSQL backend.")
except Exception as e:
    logger.error(f"Failed to initialize LightRAG: {str(e)}")
    # Fallback hoặc thông báo lỗi cụ thể hơn ở đây nếu cần

class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"

@app.get("/")
async def root():
    return {"message": "LightRAG API is running", "storage": "PostgreSQL"}

@app.post("/api/lightrag/query")
async def query_lightrag(request: QueryRequest):
    try:
        response = rag.query(
            request.query, 
            param=QueryParam(mode=request.mode)
        )
        return {"output": response}
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lightrag/insert")
async def insert_text(text: str):
    try:
        rag.insert(text)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Insert error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Lấy port từ biến môi trường của Railway/Render
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
