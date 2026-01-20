import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lightrag import LightRAG, QueryParam
from lightrag.storage import SupabaseStorage # Giả định bundle hoặc extension hỗ trợ

# Cấu hình Web Server
app = FastAPI(title="LightRAG Enterprise API")

# Cấu hình Supabase (Lấy từ môi trường hoặc điền trực tiếp)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-key")

# Khởi tạo LightRAG với Supabase Storage
# Lưu ý: LightRAG cần được cấu hình để trỏ vào Postgres của Supabase
rag = LightRAG(
    working_dir="./lightrag_cache",
    # Đây là nơi cấu hình Supabase làm backend
    # Thông thường LightRAG sẽ cần chuỗi kết nối Postgres (có pgvector)
    kv_storage="postgres", 
    vector_storage="pgvector",
    graph_storage="networkx", # Hoặc neo4j nếu anh muốn dùng Graph DB riêng
    db_config={
        "connection_string": "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres"
    }
)

class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid" # naive, local, global, hybrid

@app.post("/api/lightrag/query")
async def query_lightrag(request: QueryRequest):
    try:
        # Thực hiện truy vấn qua LightRAG
        response = rag.query(
            request.query, 
            param=QueryParam(mode=request.mode)
        )
        return {"output": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lightrag/insert")
async def insert_text(text: str):
    try:
        # Chèn thêm kiến thức mới vào hệ thống
        rag.insert(text)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
