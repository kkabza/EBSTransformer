"""
API - FastAPI application for CCS integration.
"""
import logging
import os
from typing import Dict, Any, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Response, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import core components
from app.core.orchestrator import LLMOrchestrator
from app.core.agent_registry import AgentRegistry
from app.core.event_bus import EventBus, KafkaEventBus, AzureServiceBusEventBus
from app.services.ccs_integration_orchestrator import CCSIntegrationOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CCS Integration API",
    description="API for CCS integration with LLM orchestration",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests and responses
class ISOClaimRequest(BaseModel):
    claim_data: str

class ISOClaimResponse(BaseModel):
    message_id: str
    status: str
    processed_claim: Optional[str] = None
    destination: Optional[str] = None
    errors: Optional[List[str]] = None

class BatchRequest(BaseModel):
    batch_data: str
    batch_type: str

class BatchResponse(BaseModel):
    message_id: str
    status: str
    file_path: Optional[str] = None
    errors: Optional[List[str]] = None

class AcknowledgmentRequest(BaseModel):
    ack_data: Dict[str, Any]

class AcknowledgmentResponse(BaseModel):
    message_id: str
    status: str
    notification_sent: bool
    errors: Optional[List[str]] = None

class AddressVerificationRequest(BaseModel):
    address_data: Dict[str, Any]

class AddressVerificationResponse(BaseModel):
    message_id: str
    status: str
    verified_address: Optional[Dict[str, Any]] = None
    verification_score: Optional[float] = None
    errors: Optional[List[str]] = None

# Global variable to store application components
components = {}

# Dependency to get orchestrator
def get_orchestrator():
    return components.get("orchestrator")

# Dependency to get CCS integration orchestrator
def get_ccs_orchestrator():
    return components.get("ccs_orchestrator")

@app.on_event("startup")
async def startup_event():
    """Initialize application components on startup."""
    # Initialize event bus
    event_bus_type = os.environ.get("EVENT_BUS_TYPE", "memory")
    if event_bus_type == "kafka":
        bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        event_bus = KafkaEventBus(bootstrap_servers)
    elif event_bus_type == "azure":
        connection_string = os.environ.get("AZURE_SERVICE_BUS_CONNECTION_STRING", "")
        event_bus = AzureServiceBusEventBus(connection_string)
    else:
        event_bus = EventBus()
    
    # Initialize agent registry
    agent_registry = AgentRegistry()
    
    # Initialize orchestrator
    orchestrator = LLMOrchestrator(event_bus, agent_registry)
    
    # Initialize CCS integration orchestrator
    ccs_orchestrator = CCSIntegrationOrchestrator(
        orchestrator,
        {
            "api_base_url": os.environ.get("CCS_API_BASE_URL", "http://localhost:8000")
        }
    )
    
    # TODO: Register agents
    # This would be done in a production application
    
    # Store components for use in API handlers
    components["event_bus"] = event_bus
    components["agent_registry"] = agent_registry
    components["orchestrator"] = orchestrator
    components["ccs_orchestrator"] = ccs_orchestrator
    
    logger.info("Application components initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up application components on shutdown."""
    # Clean up code would go here
    logger.info("Application shutting down")

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "CCS Integration API is running"}

@app.post("/iso-claim", response_model=ISOClaimResponse, tags=["ISO Claims"])
async def process_iso_claim(
    request: ISOClaimRequest,
    ccs_orchestrator: CCSIntegrationOrchestrator = Depends(get_ccs_orchestrator)
):
    """Process an ISO claim from CCS."""
    try:
        result = await ccs_orchestrator.handle_iso_claim(request.claim_data)
        
        return {
            "message_id": result.get("message_id", ""),
            "status": result.get("status", "error"),
            "processed_claim": result.get("processed_claim"),
            "destination": result.get("destination"),
            "errors": [result.get("errors")] if result.get("errors") else None
        }
    except Exception as e:
        logger.error(f"Error processing ISO claim: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch/inbound", response_model=BatchResponse, tags=["Batch Processing"])
async def process_batch_inbound(
    request: BatchRequest,
    ccs_orchestrator: CCSIntegrationOrchestrator = Depends(get_ccs_orchestrator)
):
    """Process an inbound batch file."""
    try:
        result = await ccs_orchestrator.handle_batch_inbound(
            request.batch_data,
            request.batch_type
        )
        
        return {
            "message_id": result.get("message_id", ""),
            "status": result.get("status", "error"),
            "file_path": result.get("file_path"),
            "errors": [result.get("errors")] if result.get("errors") else None
        }
    except Exception as e:
        logger.error(f"Error processing inbound batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch/outbound", response_model=BatchResponse, tags=["Batch Processing"])
async def process_batch_outbound(
    request: dict,
    ccs_orchestrator: CCSIntegrationOrchestrator = Depends(get_ccs_orchestrator)
):
    """Process an outbound batch file."""
    try:
        result = await ccs_orchestrator.handle_batch_outbound(
            request.get("items", []),
            request.get("batch_type", "")
        )
        
        return {
            "message_id": result.get("message_id", ""),
            "status": result.get("status", "error"),
            "file_path": result.get("file_path"),
            "errors": [result.get("errors")] if result.get("errors") else None
        }
    except Exception as e:
        logger.error(f"Error processing outbound batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/acknowledgment", response_model=AcknowledgmentResponse, tags=["Acknowledgments"])
async def process_acknowledgment(
    request: AcknowledgmentRequest,
    ccs_orchestrator: CCSIntegrationOrchestrator = Depends(get_ccs_orchestrator)
):
    """Process an acknowledgment from CCS."""
    try:
        result = await ccs_orchestrator.handle_acknowledgment(request.ack_data)
        
        return {
            "message_id": result.get("message_id", ""),
            "status": result.get("status", "error"),
            "notification_sent": result.get("notification_sent", False),
            "errors": [result.get("errors")] if result.get("errors") else None
        }
    except Exception as e:
        logger.error(f"Error processing acknowledgment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/address-verification", response_model=AddressVerificationResponse, tags=["Address Verification"])
async def verify_address(
    request: AddressVerificationRequest,
    ccs_orchestrator: CCSIntegrationOrchestrator = Depends(get_ccs_orchestrator)
):
    """Verify an address from CCS."""
    try:
        result = await ccs_orchestrator.handle_address_verification(request.address_data)
        
        return {
            "message_id": result.get("message_id", ""),
            "status": result.get("status", "error"),
            "verified_address": result.get("verified_address"),
            "verification_score": result.get("verification_score"),
            "errors": [result.get("errors")] if result.get("errors") else None
        }
    except Exception as e:
        logger.error(f"Error verifying address: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True) 