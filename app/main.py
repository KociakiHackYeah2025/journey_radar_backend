from fastapi import FastAPI
from app.routers import auth
import os

app = FastAPI()
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)