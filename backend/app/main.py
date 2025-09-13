from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, properties
from app.core.config import settings

app = FastAPI(
    title="Georgia Properties API",
    description="AI-powered property search with natural language processing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(properties.router, prefix="/api/properties", tags=["properties"])

@app.get("/")
async def root():
    return {
        "message": "Georgia Properties API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)