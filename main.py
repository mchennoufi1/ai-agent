from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import reasoning_agent
from memory import ConversationMemory

app = FastAPI(title="AI Research Agent")
memory = ConversationMemory()

class Query(BaseModel):
    question: str
    use_memory: bool = False

@app.get("/")
def health_check():
    return {"status": "Agent is running"}

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

@app.delete("/memory")
def clear_memory():
    memory.clear()
    return {"status": "Memory cleared"}
