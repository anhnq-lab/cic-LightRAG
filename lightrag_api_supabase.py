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

# Khởi tạo LightRAG với PostgreSQL Storage
try:
    # Ưu tiên các biến môi trường POSTGRES_... cho lightrag-hku
    # Nếu không có, có thể cấu hình qua db_config
    rag = LightRAG(
        working_dir=WORKING_DIR,
        kv_storage="PGKVStorage",
        vector_storage="PGVectorStorage",
        graph_storage="PGGraphStorage",
        doc_status_storage="PGDocStatusStorage",
        # Một số phiên bản lightrag-hku hỗ trợ cấu hình DB qua db_config nếu env ko có
        db_config={
            "host": os.getenv("POSTGRES_HOST"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "database": os.getenv("POSTGRES_DATABASE"),
        }
    )
    logger.info("LightRAG initialized successfully with PostgreSQL backend.")
except Exception as e:
    logger.error(f"Failed to initialize LightRAG: {str(e)}")

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
