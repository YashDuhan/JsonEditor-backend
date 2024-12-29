from fastapi import FastAPI, HTTPException, Depends
from .db import get_db, JsonMetadata
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Any
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI();

# ------------- Push Logs  -------------
class PushSchema(BaseModel):
    json_data: str

@app.post("/push")
async def push_logs(
    push: PushSchema,
    db: Session = Depends(get_db)
):
    try:
        # Store in DB
        logs = JsonMetadata(
            file_content=push.json_data,
            uploaddate=datetime.now()
        )
        db.add(logs)
        db.commit()
        return {"message": "Pushed to DB"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
# ------------- Fetch Logs -------------
@app.get("/fetch")
async def fetch_logs(
    db: Session = Depends(get_db)
):
    try:
        # Latest record
        last_log = db.query(JsonMetadata)\
            .order_by(JsonMetadata.uploaddate.desc())\
            .first()
        
        if not last_log:
            raise HTTPException(
                status_code=404,
                detail="No logs found in database"
            )
            
        return {
            "file_content": last_log.file_content,
            "uploaddate": last_log.uploaddate
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# ------------- Ask Question from AI  -------------
# Ask schema
class AskSchema(BaseModel):
    full_json: str
    selected_json: str
    question: str


# Endpoint for /ask
@app.post("/ask")
async def ask_ai(request: AskSchema):
    try:
        # req to groq
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {"role": "user", "content": 
                """
                    General Instructions : I've created an app that generates HTML from a provided JSON file. You will receive:
                    1. The full JSON (the user's entire JSON file).
                    2. The selected JSON (the part the user wants to modify)
                    3. The user's question (which may also include specific actions or commands to perform).
                    When responding, please provide only the relevant snippet of the modified JSON. There's no need to include the full JSON; just the updated portion will suffice.
                """
                },
                {"role": "user", "content": f"Full Json: {request.full_json}"},
                {"role": "user", "content": f"Selected Json: {request.selected_json}"},
                {"role": "user", "content": f"Question: {request.question}"}
            ],
            temperature=1,
            max_tokens=500,
            top_p=1,
            stream=False  # get full response at once
        )

        answer = completion.choices[0].message.content if completion.choices else None
        if answer:
            return {"answer": answer}
        else:
            raise HTTPException(status_code=500, detail="No response")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
