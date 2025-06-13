from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
import asyncio
from pydantic import BaseModel
from typing import Any, List
from datetime import timedelta
import json
from utils.agents import Agents
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("APIEndpoint")

agents = Agents()

class APIEndpoint:
    """
    A class to define and manage a FastAPI application with specific routes and background task handling.
    """
    def __init__(self):
        self.app = FastAPI()
        self.background_tasks = set()        
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/agent_task")
        async def process_payload(request: Request):
            try:
                #self.agents = Agents()
                #await agents.initialize()

                # Read the request body
                payload = await request.json()

                # Convert the JSON payload to a string
                event_str = json.dumps(payload)
                
                # Use the new TaskRunner
                task = asyncio.create_task(agents.run_task(event_str))
                
                # Add the created task to the set of background tasks
                self.background_tasks.add(task)
                
                # Ensure the task is removed from the set once it is completed
                task.add_done_callback(self.background_tasks.discard)
                
                # Return a success response with HTTP status 200
                return {"status": "success"}, 200

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing payload: {str(e)}"
                )
    
    # Method to return the FastAPI application instance
    def get_app(self):
        return self.app
    
# Create an instance of the APIEndpoint class
api = APIEndpoint()

# Retrieve the FastAPI application instance from the APIEndpoint instance
app = api.get_app()

# Define an event handler for the "startup" event
@app.on_event("startup")
async def startup_event():
    # Call async initialization for agents
    await agents.initialize()
    logger.info("Agents initialized successfully.")

# Define an event handler for the "shutdown" event
@app.on_event("shutdown")
async def shutdown_event():
    # Check if there are any background tasks still running
    if api.background_tasks:
        # Wait for all background tasks to complete before shutting down
        await asyncio.gather(*api.background_tasks)