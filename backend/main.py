from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# Allow CORS for React frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<h1>Welcome to FastAPI!</h1>"

@app.get("/api/data")
async def get_data():
    return {"message": "Hello from FastAPI!"}

# Using a simple Python HTTP server to run the app
if __name__ == "__main__":
    import os
    import subprocess

    # Use a subprocess to run the FastAPI application
    subprocess.run(["python", "-m", "http.server", "8000"])
