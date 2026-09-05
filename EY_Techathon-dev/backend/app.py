import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Agents.Competitor_analysis.routers import router as competitor_router
from Agents.Drug_Repurposing.router import router as repurposing_router
from Agents.Clinical_Trials.router import router as clinical_trials_router
from Agents.Market_Insights.router import router as market_insights_router
from Agents.Web_search.router import router as web_search_router
from Agents.Drug_Discovery.router import router as drug_discovery_router
from Agents.ESG_Report_Generator.router import router as esg_router
from Agents.Medicine_Validation.router import router as medicine_validation_router
from Deep_Research.router import router as deep_research_router
from Agents.News.router import router as news_router, fetch_and_cache_news

# Load environment variables from parent directory .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
print(f"📝 Loading .env from: {env_path}")
print(f"🔑 NEWS_API_KEY loaded: {'Yes' if os.getenv('NEWS_API_KEY') else 'No'}")


# Scheduler for background tasks
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start scheduler and fetch initial news
    scheduler.add_job(fetch_and_cache_news, 'interval', minutes=10, id='news_fetcher')
    scheduler.start()
    # Fetch immediately on startup
    await fetch_and_cache_news()
    print("✅ News cron job started (runs every 10 minutes)")
    yield
    # Shutdown: Stop scheduler
    scheduler.shutdown()


app = FastAPI(title="EY Techathon API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure reports directory exists and mount it for static file serving
reports_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"
)
if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)
app.mount("/reports", StaticFiles(directory=reports_dir), name="reports")

# Include routers
app.include_router(competitor_router)
app.include_router(repurposing_router)
app.include_router(clinical_trials_router)
app.include_router(market_insights_router)
app.include_router(web_search_router)
app.include_router(drug_discovery_router)
app.include_router(esg_router)
app.include_router(deep_research_router)
app.include_router(news_router)
app.include_router(medicine_validation_router)
# app.include_router(report_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to EY Techathon API"}




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
