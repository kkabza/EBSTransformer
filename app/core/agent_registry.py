"""
Agent Registry - Manages registration and retrieval of agents.
"""
import logging
from typing import Dict, Any, Optional, Type

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Registry for agents used by the LLM Orchestrator.
    Allows registration and retrieval of agents by ID.
    """
    
    def __init__(self):
        self.agents = {}
        
    def register_agent(self, agent_id: str, agent_instance: Any) -> None:
        """
        Register an agent instance with the registry.
        
        Args:
            agent_id: The ID to register the agent under
            agent_instance: The agent instance to register
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered, overwriting")
            
        self.agents[agent_id] = agent_instance
        logger.info(f"Registered agent {agent_id}")
        
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """
        Get an agent instance by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve
            
        Returns:
            The agent instance, or None if not found
        """
        agent = self.agents.get(agent_id)
        if not agent:
            logger.warning(f"Agent {agent_id} not found in registry")
            return None
            
        return agent
        
    def list_agents(self) -> Dict[str, Any]:
        """
        List all registered agents.
        
        Returns:
            Dictionary of agent IDs to agent instances
        """
        return self.agents.copy()
        
    def register_agents_from_config(self, agent_configs: Dict[str, Dict[str, Any]], agent_factories: Dict[str, Type]) -> None:
        """
        Register multiple agents from a configuration dictionary.
        
        Args:
            agent_configs: Dictionary mapping agent IDs to configuration dictionaries
            agent_factories: Dictionary mapping agent types to agent factory classes
        """
        for agent_id, config in agent_configs.items():
            agent_type = config.get("type")
            if not agent_type:
                logger.error(f"Agent {agent_id} missing type in configuration")
                continue
                
            factory = agent_factories.get(agent_type)
            if not factory:
                logger.error(f"No factory found for agent type {agent_type}")
                continue
                
            try:
                agent_instance = factory(agent_id, config)
                self.register_agent(agent_id, agent_instance)
            except Exception as e:
                logger.error(f"Error creating agent {agent_id}: {str(e)}")
                
    def register_multiple(self, agents: Dict[str, Any]) -> None:
        """
        Register multiple agents from a dictionary.
        
        Args:
            agents: Dictionary mapping agent IDs to agent instances
        """
        for agent_id, agent_instance in agents.items():
            self.register_agent(agent_id, agent_instance) 