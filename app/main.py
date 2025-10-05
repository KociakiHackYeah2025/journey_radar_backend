from fastapi import FastAPI
from app.routers import auth, sync, search, report, route, trip
import os
from app.database import synchronization
from apscheduler.schedulers.background import BackgroundScheduler
import pytz


app = FastAPI()
app.include_router(auth.router)
app.include_router(sync.router)
app.include_router(search.router)
app.include_router(report.router)
app.include_router(route.router)
app.include_router(trip.router)

# Scheduler do automatycznego wywołania synchronizacji
def start_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Warsaw"))
    scheduler.add_job(synchronization, 'cron', hour=2, minute=0)
    scheduler.start()
    return scheduler

start_scheduler()

@app.get("/")
def read_root():
    return {"message": "Kociaki HackYeah 2025 - Journey Radar Backend"}

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)