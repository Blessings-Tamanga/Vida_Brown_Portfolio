from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine, Base
from routes import routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vida Brown API",
    description="API for Vida Brown's official website - Music, Videos, and More",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Vida Brown API",
        "docs": "/docs",
        "endpoints": {
            "artist": "/api/artist/profile",
            "videos": "/api/videos",
            "music": "/api/music/tracks",
            "gallery": "/api/gallery",
            "products": "/api/products"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)