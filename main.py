from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Get DB connection string from environment variable
conn_str = os.getenv("DB_CONN_STR")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (for Swagger UI and frontend compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/events")
def get_events():
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Events")
            rows = cursor.fetchall()
            return [
                dict(zip([column[0] for column in cursor.description], row))
                for row in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events")
def create_event(
    name: str = Query(..., description="Name of the event"),
    description: str = Query(..., description="Description of the event"),
    date: str = Query(..., description="Date of the event"),
    location: str = Query(..., description="Location of the event"),
    capacity: int = Query(..., description="Capacity of the event")
):
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Events (name, description, date, location, capacity) VALUES (?, ?, ?, ?, ?)",
                name, description, date, location, capacity
            )
            conn.commit()
            return {"message": "Event created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)