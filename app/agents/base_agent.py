"""
Base Agent - Abstract base class for all agents.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    All agents should inherit from this class and implement the process method.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize a new agent.
        
        Args:
            name: The name of the agent
            config: Configuration dictionary for the agent
        """
        self.name = name
        self.config = config
        self.llm_client = self._setup_llm_client()
        
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the context and return updated context.
        This method must be implemented by all agent subclasses.
        
        Args:
            context: The context to process
            
        Returns:
            Updated context
        """
        pass
        
    def _setup_llm_client(self) -> Any:
        """
        Set up the LLM client based on configuration.
        
        Returns:
            LLM client instance
        """
        # Default implementation returns None
        # Subclasses can override to provide a specific LLM client
        return None
        
    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with a default.
        
        Args:
            key: The configuration key
            default: Default value if the key is not found
            
        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)
        
    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info message with agent name.
        
        Args:
            message: The message to log
            extra: Extra information to include in the log
        """
        extra_dict = {"agent": self.name}
        if extra:
            extra_dict.update(extra)
        
        logger.info(message, extra=extra_dict)
        
    def log_error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error message with agent name.
        
        Args:
            message: The message to log
            extra: Extra information to include in the log
        """
        extra_dict = {"agent": self.name}
        if extra:
            extra_dict.update(extra)
        
        logger.error(message, extra=extra_dict)
        
    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning message with agent name.
        
        Args:
            message: The message to log
            extra: Extra information to include in the log
        """
        extra_dict = {"agent": self.name}
        if extra:
            extra_dict.update(extra)
        
        logger.warning(message, extra=extra_dict)
        
    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a debug message with agent name.
        
        Args:
            message: The message to log
            extra: Extra information to include in the log
        """
        extra_dict = {"agent": self.name}
        if extra:
            extra_dict.update(extra)
        
        logger.debug(message, extra=extra_dict) 