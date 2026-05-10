"""
KitchenOS-AI — FastAPI entry point.

Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from loguru import logger
import uuid

from agents.orchestrator import orchestrator, AgentType
from agents.kitchen_ops import handle_kitchen_ops
from agents.finance_agent import handle_finance
from agents.file_gen_agent import handle_file_gen
from agents.web_search_agent import handle_web_search
from agents.career_ops_agent import handle_career_ops
from agents.general_agent import handle_general
from agents.rag_agent import handle_rag
from agents.recommendation_agent import handle_recommendation
from services.memory import memory_store

app = FastAPI(title="KitchenOS-AI", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Register agent handlers
orchestrator.register(AgentType.KITCHEN_OPS, handle_kitchen_ops)
orchestrator.register(AgentType.FINANCE, handle_finance)
orchestrator.register(AgentType.FILE_GEN, handle_file_gen)
orchestrator.register(AgentType.WEB_SEARCH, handle_web_search)
orchestrator.register(AgentType.CAREER_OPS, handle_career_ops)
orchestrator.register(AgentType.RAG, handle_rag)
orchestrator.register(AgentType.RECOMMENDATION, handle_recommendation)
orchestrator.register(AgentType.GENERAL, handle_general)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    tone: str | None = None  # "formal", "casual", "friendly"
    context: dict | None = None


class ChatResponse(BaseModel):
    agent: str
    response: str | dict
    status: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chat endpoint — routes to the appropriate agent with memory."""
    session_id = req.session_id or str(uuid.uuid4())

    # Store user message in memory
    memory_store.add(session_id, "user", req.message)

    # Get conversation history
    history = memory_store.get_history(session_id)

    # Build context with memory + tone
    context = req.context or {}
    context["history"] = history[:-1]  # exclude current message
    context["tone"] = req.tone or "friendly"
    context["session_id"] = session_id

    result = await orchestrator.dispatch(req.message, context)

    # Store assistant response in memory
    resp_text = result["response"]
    if isinstance(resp_text, dict):
        resp_text = resp_text.get("message", str(resp_text))
    memory_store.add(session_id, "assistant", resp_text)

    return ChatResponse(**result, session_id=session_id)


@app.post("/chat/image")
async def chat_with_image(
    message: str = "",
    file: UploadFile = File(...),
    session_id: str = Query(default=""),
    tone: str = Query(default="friendly"),
):
    """Chat endpoint with image upload (for OCR/vision tasks)."""
    sid = session_id or str(uuid.uuid4())
    contents = await file.read()
    context = {
        "image_bytes": contents,
        "filename": file.filename,
        "tone": tone,
        "session_id": sid,
        "history": memory_store.get_history(sid),
    }

    memory_store.add(sid, "user", message or "Analyze this image")
    result = await orchestrator.dispatch(message or "Analyze this image", context)

    resp_text = result["response"]
    if isinstance(resp_text, dict):
        resp_text = resp_text.get("message", str(resp_text))
    memory_store.add(sid, "assistant", resp_text)

    result["session_id"] = sid
    return result


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    return {"session_id": session_id, "messages": memory_store.get_history(session_id)}


@app.get("/sessions")
async def list_sessions():
    """List all chat sessions."""
    sessions = memory_store.list_sessions()
    result = []
    for sid in sessions:
        msgs = memory_store.get_history(sid)
        if msgs:
            result.append({
                "session_id": sid,
                "message_count": len(msgs),
                "last_message": msgs[-1]["content"][:80] if msgs else "",
                "first_message": msgs[0]["content"][:80] if msgs else "",
            })
    return {"sessions": result}


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session."""
    memory_store.clear(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "kitchenos-ai", "version": "0.2.0"}


# === API Key Management ===
from utils.config import gemini_keys, groq_keys


class APIKeyRequest(BaseModel):
    provider: str  # "gemini" or "groq"
    key: str


class APIKeyToggleRequest(BaseModel):
    provider: str
    index: int


@app.get("/settings/api-keys")
async def list_api_keys():
    """List all API keys (masked) with status."""
    return {
        "gemini": gemini_keys.list_keys(),
        "groq": groq_keys.list_keys(),
    }


@app.post("/settings/api-keys/add")
async def add_api_key(req: APIKeyRequest):
    """Add a new API key."""
    mgr = gemini_keys if req.provider == "gemini" else groq_keys
    mgr.add_key(req.key)
    return {"status": "ok", "keys": mgr.list_keys()}


@app.post("/settings/api-keys/toggle")
async def toggle_api_key(req: APIKeyToggleRequest):
    """Toggle API key active/inactive."""
    mgr = gemini_keys if req.provider == "gemini" else groq_keys
    new_state = mgr.toggle_key(req.index)
    if new_state is None:
        return {"status": "error", "message": "Invalid index"}
    return {"status": "ok", "enabled": new_state, "keys": mgr.list_keys()}


@app.post("/settings/api-keys/delete")
async def delete_api_key(req: APIKeyToggleRequest):
    """Delete an API key by index."""
    mgr = gemini_keys if req.provider == "gemini" else groq_keys
    success = mgr.remove_key(req.index)
    if not success:
        return {"status": "error", "message": "Invalid index"}
    return {"status": "ok", "keys": mgr.list_keys()}


# === Finance & Waste Endpoints ===
from services.finance import calculate_food_cost, calculate_menu_price
from services.waste import waste_tracker


class FoodCostRequest(BaseModel):
    cost_of_goods: float
    revenue: float


class MenuPriceRequest(BaseModel):
    cost_per_portion: float
    target_food_cost_pct: float


class WasteEntryRequest(BaseModel):
    item: str
    qty: float
    unit: str
    cost_per_unit: float
    reason: str


@app.post("/finance/food-cost")
async def api_food_cost(req: FoodCostRequest):
    """Calculate food cost percentage."""
    result = calculate_food_cost(req.cost_of_goods, req.revenue)
    return {"food_cost_pct": result.food_cost_pct, "gross_profit": result.gross_profit, "revenue": result.revenue, "cost_of_goods": result.cost_of_goods}


@app.post("/finance/menu-price")
async def api_menu_price(req: MenuPriceRequest):
    """Calculate recommended menu price."""
    price = calculate_menu_price(req.cost_per_portion, req.target_food_cost_pct)
    return {"menu_price": price, "cost_per_portion": req.cost_per_portion, "target_food_cost_pct": req.target_food_cost_pct}


@app.post("/waste/add")
async def api_waste_add(req: WasteEntryRequest):
    """Log a waste entry."""
    entry = waste_tracker.add(req.item, req.qty, req.unit, req.cost_per_unit, req.reason)
    return {"status": "logged", "item": entry.item, "loss": entry.loss}


@app.get("/waste/summary")
async def api_waste_summary():
    """Get today's waste summary."""
    return waste_tracker.daily_summary()


@app.get("/waste/weekly")
async def api_waste_weekly():
    """Get weekly waste summary."""
    return waste_tracker.weekly_summary()


# === RAG Knowledge Base Endpoints ===
from services.rag import add_document, add_documents_batch, list_documents, get_doc_count, delete_document


class RAGDocument(BaseModel):
    id: str
    text: str
    metadata: dict | None = None


class RAGBatchRequest(BaseModel):
    documents: list[RAGDocument]


@app.post("/rag/add")
async def rag_add(doc: RAGDocument):
    """Add a single document to the RAG knowledge base."""
    add_document(doc.id, doc.text, doc.metadata)
    return {"status": "added", "id": doc.id}


@app.post("/rag/upload")
async def rag_upload(file: UploadFile = File(...)):
    """Upload a file (PDF, DOCX, TXT, CSV, XLSX) to the RAG knowledge base."""
    from services.document_loader import parse_file, chunk_text, SUPPORTED_EXTENSIONS
    import os

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"status": "error", "message": f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}"}

    content = await file.read()
    try:
        text = parse_file(file.filename, content)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Split into chunks and add to knowledge base
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    base_id = os.path.splitext(file.filename)[0].replace(" ", "-").lower()

    docs = []
    for i, chunk in enumerate(chunks):
        doc_id = f"{base_id}-chunk-{i}" if len(chunks) > 1 else base_id
        docs.append({"id": doc_id, "text": chunk, "metadata": {"source": file.filename, "chunk": i}})

    add_documents_batch(docs)
    return {
        "status": "added",
        "filename": file.filename,
        "chunks": len(chunks),
        "total_chars": len(text),
    }


@app.post("/rag/batch")
async def rag_batch(req: RAGBatchRequest):
    """Add multiple documents to the RAG knowledge base."""
    docs = [{"id": d.id, "text": d.text, "metadata": d.metadata} for d in req.documents]
    add_documents_batch(docs)
    return {"status": "added", "count": len(docs)}


@app.get("/rag/documents")
async def rag_list():
    """List all documents in the knowledge base."""
    return {"count": get_doc_count(), "documents": list_documents()}


@app.delete("/rag/{doc_id}")
async def rag_delete(doc_id: str):
    """Delete a document from the knowledge base."""
    delete_document(doc_id)
    return {"status": "deleted", "id": doc_id}

