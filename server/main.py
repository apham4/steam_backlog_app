from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title = "Steam Backlog API")
app.add_middleware(
    CORSMiddleware, # CORS to allow React frontend to talk to FastAPI app
    allow_origins = ["http: //localhost:5173"], # default vite port
    allow_credentials = True,
    allow_methods = ["*"], # all methods
    allow_headers = ["*"], # all headers
)

# test
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "FastAPI Backend is running."
    }