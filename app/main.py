from fastapi import FastAPI

from app.api import api_router

app = FastAPI(title="Validia API")

# Include API routers
app.include_router(api_router)


@app.get("/")
async def read_root():
    """Health check endpoint."""
    return {"message": "Validia API is up"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
