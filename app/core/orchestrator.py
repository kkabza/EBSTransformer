"""
LLM Orchestrator - Core component for managing agent workflows and message processing.
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LLMOrchestrator:
    """
    LLM Orchestrator manages agent workflows and message processing.
    This replaces the BizTalk ESB Core infrastructure described in the architecture doc.
    """
    def __init__(self, event_bus_client, agent_registry):
        self.event_bus = event_bus_client
        self.agent_registry = agent_registry
        self.workflows = {}
        self.context_store = {}
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message through the appropriate workflow.
        
        Args:
            message: The message to process
            
        Returns:
            Dict containing the processing result
        """
        # Generate unique message ID if not provided
        if "message_id" not in message:
            message["message_id"] = str(uuid.uuid4())
            
        logger.info(f"Processing message {message['message_id']}")
        
        # Determine which workflow to use
        workflow_id = self.determine_workflow(message)
        
        # Create or retrieve workflow context
        context = self.get_or_create_context(workflow_id, message)
        
        # Select appropriate agents
        agents = self.select_agents(context)
        
        # Execute agent chain
        result = await self.execute_agent_chain(agents, context)
        
        # Handle result
        return await self.handle_result(result, context)
        
    def determine_workflow(self, message: Dict[str, Any]) -> str:
        """
        Determine which workflow to use based on message content.
        
        Args:
            message: The message to analyze
            
        Returns:
            Workflow ID string
        """
        # For ISO claim, use the iso_claim workflow
        if message.get("message_type") == "iso_claim":
            return "iso_claim_workflow"
            
        # For batch processing, use the batch workflow
        if message.get("message_type") in ["batch_inbound", "batch_outbound"]:
            return f"{message['message_type']}_workflow"
            
        # Default to a generic workflow
        logger.warning(f"No specific workflow for message type {message.get('message_type')}, using default")
        return "default_workflow"
        
    def get_or_create_context(self, workflow_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get or create a workflow context based on the workflow ID and message.
        
        Args:
            workflow_id: The ID of the workflow
            message: The message to process
            
        Returns:
            Context dictionary
        """
        message_id = message["message_id"]
        
        # Check if we already have a context for this message
        if message_id in self.context_store:
            logger.info(f"Retrieved existing context for message {message_id}")
            return self.context_store[message_id]
            
        # Create new context
        context = {
            "message_id": message_id,
            "workflow_id": workflow_id,
            "original_message": message,
            "created_at": datetime.utcnow().isoformat(),
            "status": "processing",
            "processing_history": []
        }
        
        # Store context
        self.context_store[message_id] = context
        
        logger.info(f"Created new context for message {message_id} with workflow {workflow_id}")
        return context
        
    def select_agents(self, context: Dict[str, Any]) -> List[str]:
        """
        Select appropriate agents based on the context.
        
        Args:
            context: The workflow context
            
        Returns:
            List of agent IDs to execute
        """
        workflow_id = context["workflow_id"]
        
        # ISO claim workflow
        if workflow_id == "iso_claim_workflow":
            return [
                "validator.iso_claim",
                "transformer.iso_claim",
                "process.claim_routing",
                "integration.destination_system"
            ]
            
        # Batch inbound workflow
        if workflow_id == "batch_inbound_workflow":
            return [
                "validator.batch",
                "splitter.batch",
                "transformer.batch",
                "process.batch_routing",
                "integration.destination_system"
            ]
            
        # Batch outbound workflow
        if workflow_id == "batch_outbound_workflow":
            return [
                "validator.outbound",
                "aggregator.batch",
                "transformer.outbound",
                "process.file_generation",
                "integration.file_system"
            ]
            
        # Default workflow
        logger.warning(f"No specific agents for workflow {workflow_id}, using generic agents")
        return [
            "validator.generic",
            "transformer.generic",
            "process.generic",
            "integration.generic"
        ]
        
    async def execute_agent_chain(self, agents: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agents in sequence, passing context between them.
        
        Args:
            agents: List of agent IDs to execute
            context: The workflow context
            
        Returns:
            Updated context dictionary after agent execution
        """
        current_context = context.copy()
        
        for agent_id in agents:
            # Record the start of agent processing
            step_start = datetime.utcnow().isoformat()
            
            try:
                # Look up the agent in the registry
                agent = self.agent_registry.get_agent(agent_id)
                if not agent:
                    raise ValueError(f"Agent {agent_id} not found in registry")
                
                logger.info(f"Executing agent {agent_id} for message {context['message_id']}")
                
                # Process the context with the agent
                current_context = await agent.process(current_context)
                status = "success"
                error = None
                
            except Exception as e:
                # Handle any errors during agent execution
                status = "error"
                error = str(e)
                logger.error(f"Error executing agent {agent_id}: {error}")
                
                # Check if we should continue despite errors
                if not current_context.get("continue_on_error", False):
                    break
            
            # Record the agent execution in the processing history
            current_context["processing_history"].append({
                "agent_id": agent_id,
                "start_time": step_start,
                "end_time": datetime.utcnow().isoformat(),
                "status": status,
                "error": error
            })
        
        # Update the context status
        if any(step["status"] == "error" for step in current_context["processing_history"]):
            current_context["status"] = "error"
        else:
            current_context["status"] = "completed"
        
        # Return the updated context
        return current_context
        
    async def handle_result(self, result: Dict[str, Any], original_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the result of agent chain execution.
        
        Args:
            result: The updated context after agent execution
            original_context: The original context before agent execution
            
        Returns:
            Result dictionary
        """
        # Update the context store with the result
        self.context_store[result["message_id"]] = result
        
        # If there was an error, publish to the error topic
        if result["status"] == "error":
            await self.event_bus.publish("error", {
                "message_id": result["message_id"],
                "error": "Error during agent execution",
                "context": result
            })
        
        # Return the final result
        return {
            "message_id": result["message_id"],
            "status": result["status"],
            "result": result.get("result"),
            "errors": [step["error"] for step in result["processing_history"] if step["error"]]
        }
    
    async def execute_workflow(self, workflow: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a predefined workflow with provided context.
        
        Args:
            workflow: List of agent IDs to execute
            context: Initial context dictionary
            
        Returns:
            Updated context after workflow execution
        """
        # Ensure message_id exists
        if "message_id" not in context:
            context["message_id"] = str(uuid.uuid4())
            
        # Store the context
        self.context_store[context["message_id"]] = context
        
        # Execute the agent chain
        result = await self.execute_agent_chain(workflow, context)
        
        # Handle the result
        await self.handle_result(result, context)
        
        return result 