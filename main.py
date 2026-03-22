from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.llm_agent import LLMAgent

app = FastAPI()

agent = LLMAgent()


# ---------------- REQUEST MODEL ---------------- #

class ChatRequest(BaseModel):
    message: str
    user_id: int = 1


# ---------------- ROUTES ---------------- #

@app.get("/")
def home():
    return {"message": "AI Fitness Coach API running 🚀"}


@app.post("/chat")
def chat(req: ChatRequest):
    response = agent.run(req.message, req.user_id)
    return {"response": response}


@app.post("/workout")
def workout():
    response = agent.run("generate workout")
    return {"workout": response}


@app.post("/diet")
def diet():
    response = agent.run("generate diet")
    return {"diet": response}


@app.get("/progress")
def progress():
    response = agent.run("show progress")
    return {"progress": response}


@app.get("/insights")
def insights():
    response = agent.run("analyze my progress")
    return {"insights": response}


@app.get("/nudges")
def nudges():
    response = agent.run("any advice for today")
    return {"nudges": response}