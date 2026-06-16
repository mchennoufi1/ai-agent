from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent import reasoning_agent
from memory import ConversationMemory
from fastapi.responses import StreamingResponse

app = FastAPI(title="AI Research Agent")
app.mount("/static", StaticFiles(directory="static"), name="static")
memory = ConversationMemory()

class Query(BaseModel):
    question: str
    use_memory: bool = False

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.post("/agent")
def run_agent(q: Query):
    try:
        if q.use_memory:
            memory.add("user", q.question)

        result = reasoning_agent(q.question)

        if q.use_memory:
            memory.add("assistant", result["answer"])

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "plan": result["plan"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/agent/stream")
def run_agent_stream(q: Query):
    return StreamingResponse(
        reasoning_agent_stream(q.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )        

@app.delete("/memory")
def clear_memory():
    memory.clear()
    return {"status": "Memory cleared"}