from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx, os

app = FastAPI(
    title="Notification Service",
    description="Sends notifications for the K11 platform. Consumes user-service for contact info.",
    version="1.0.0",
)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")


class Notification(BaseModel):
    id: str
    user_id: str
    channel: str
    message: str
    status: str = "sent"


class SendNotification(BaseModel):
    user_id: str
    channel: str  # email | sms | push
    message: str


@app.post("/api/v1/notifications", response_model=Notification, status_code=201, tags=["notifications"])
async def send_notification(body: SendNotification):
    """Send a notification to a user. Fetches contact info from user-service."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{USER_SERVICE_URL}/api/v2/users/{body.user_id}/contact")
        if resp.status_code == 404:
            raise HTTPException(status_code=422, detail="User contact info not found")
    return Notification(id="generated-id", **body.model_dump())


@app.get("/api/v1/notifications/{id}", response_model=Notification, tags=["notifications"])
async def get_notification(id: str):
    """Get a notification by ID."""
    raise HTTPException(status_code=404, detail="Notification not found")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification-svc", "version": "1.0.0"}
