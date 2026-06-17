"""
main.py — Application entry point. Wires FastAPI + routes to slack.

Run:
    cd notification_project
    uvicorn main:app
    # Python 3.6 without --reload:
    python main.py
"""

import uvicorn
from fastapi import FastAPI

from routes import router

app = FastAPI(
    title="Notification Forwarding Service",
    description=(
        "Receives notifications and forwards **Warning** types to "
        "Microsoft Teams and Email. **Info** types are stored only."
    ),
    version="2.0.0",
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
