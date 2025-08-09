from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List
import random
from datetime import datetime

from models import DrawingIdea, DrawingIdeaCreate, DrawingIdeaResponse
from data import DEFAULT_DRAWING_IDEAS

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Seed default ideas on startup
async def seed_default_ideas():
    """Seed the database with default drawing ideas if not already present"""
    try:
        # Check if we already have ideas
        existing_count = await db.drawing_ideas.count_documents({})
        if existing_count > 0:
            return
        
        # Insert default ideas
        default_ideas = []
        for idea_text in DEFAULT_DRAWING_IDEAS:
            idea = DrawingIdea(
                text=idea_text,
                user_submitted=False,
                created_at=datetime.utcnow()
            )
            default_ideas.append(idea.dict())
        
        await db.drawing_ideas.insert_many(default_ideas)
        logger.info(f"Seeded {len(default_ideas)} default drawing ideas")
    except Exception as e:
        logger.error(f"Error seeding default ideas: {e}")

# Drawing Ideas Routes
@api_router.get("/ideas", response_model=List[DrawingIdeaResponse])
async def get_all_ideas():
    """Get all drawing ideas"""
    try:
        ideas = await db.drawing_ideas.find().sort("created_at", -1).to_list(1000)
        return [DrawingIdeaResponse(**idea) for idea in ideas]
    except Exception as e:
        logger.error(f"Error fetching ideas: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch ideas")

@api_router.get("/ideas/random", response_model=DrawingIdeaResponse)
async def get_random_idea():
    """Get a random drawing idea"""
    try:
        # Get total count
        total = await db.drawing_ideas.count_documents({})
        if total == 0:
            raise HTTPException(status_code=404, detail="No ideas available")
        
        # Get random idea using aggregation
        pipeline = [{"$sample": {"size": 1}}]
        cursor = db.drawing_ideas.aggregate(pipeline)
        random_idea = await cursor.to_list(length=1)
        
        if not random_idea:
            raise HTTPException(status_code=404, detail="No ideas available")
        
        return DrawingIdeaResponse(**random_idea[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching random idea: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch random idea")

@api_router.post("/ideas", response_model=DrawingIdeaResponse)
async def create_idea(idea_input: DrawingIdeaCreate):
    """Create a new drawing idea"""
    try:
        # Check if idea already exists (case-insensitive)
        existing = await db.drawing_ideas.find_one({
            "text": {"$regex": f"^{idea_input.text.strip()}$", "$options": "i"}
        })
        if existing:
            raise HTTPException(status_code=409, detail="This idea already exists")
        
        # Create new idea
        new_idea = DrawingIdea(
            text=idea_input.text.strip(),
            user_submitted=True,
            created_at=datetime.utcnow()
        )
        
        # Insert to database
        result = await db.drawing_ideas.insert_one(new_idea.dict())
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create idea")
        
        return DrawingIdeaResponse(**new_idea.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating idea: {e}")
        raise HTTPException(status_code=500, detail="Failed to create idea")

# Health check route
@api_router.get("/")
async def root():
    return {"message": "EmalfDraw API is running!"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await db.command("ping")
        idea_count = await db.drawing_ideas.count_documents({})
        return {
            "status": "healthy",
            "database": "connected",
            "ideas_count": idea_count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Seed default ideas on startup"""
    await seed_default_ideas()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
