from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)