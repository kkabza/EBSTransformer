"""
Configuration - Application configuration.
"""
import os
from typing import Dict, Any, Optional, List
import json

class Config:
    """Application configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = {}
        
        # Load from config file if provided
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
            
        # Override with environment variables
        self._load_from_env()
        
    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, "r") as f:
                if config_path.endswith(".json"):
                    self.config = json.load(f)
                else:
                    # Simple key=value file
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        key, value = line.split("=", 1)
                        self.config[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error loading configuration file: {str(e)}")
            
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Event bus configuration
        self.config["EVENT_BUS_TYPE"] = os.environ.get("EVENT_BUS_TYPE", self.config.get("EVENT_BUS_TYPE", "memory"))
        self.config["KAFKA_BOOTSTRAP_SERVERS"] = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", self.config.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
        self.config["AZURE_SERVICE_BUS_CONNECTION_STRING"] = os.environ.get("AZURE_SERVICE_BUS_CONNECTION_STRING", self.config.get("AZURE_SERVICE_BUS_CONNECTION_STRING", ""))
        
        # LLM configuration
        self.config["LLM_TYPE"] = os.environ.get("LLM_TYPE", self.config.get("LLM_TYPE", "openai"))
        self.config["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", self.config.get("OPENAI_API_KEY", ""))
        self.config["OPENAI_MODEL"] = os.environ.get("OPENAI_MODEL", self.config.get("OPENAI_MODEL", "gpt-4"))
        self.config["AZURE_OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY", self.config.get("AZURE_OPENAI_API_KEY", ""))
        self.config["AZURE_OPENAI_ENDPOINT"] = os.environ.get("AZURE_OPENAI_ENDPOINT", self.config.get("AZURE_OPENAI_ENDPOINT", ""))
        self.config["AZURE_OPENAI_API_VERSION"] = os.environ.get("AZURE_OPENAI_API_VERSION", self.config.get("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"))
        
        # CCS interface configuration
        self.config["CCS_API_BASE_URL"] = os.environ.get("CCS_API_BASE_URL", self.config.get("CCS_API_BASE_URL", "http://localhost:8080"))
        
        # Agent configuration paths
        self.config["EXAMPLES_PATH"] = os.environ.get("EXAMPLES_PATH", self.config.get("EXAMPLES_PATH", "examples"))
        self.config["XSLT_PATH"] = os.environ.get("XSLT_PATH", self.config.get("XSLT_PATH", "xslt"))
        
        # API configuration
        self.config["API_HOST"] = os.environ.get("API_HOST", self.config.get("API_HOST", "0.0.0.0"))
        self.config["API_PORT"] = int(os.environ.get("API_PORT", self.config.get("API_PORT", "8000")))
        self.config["API_DEBUG"] = os.environ.get("API_DEBUG", self.config.get("API_DEBUG", "true")).lower() == "true"
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with default.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
        
    def get_event_bus_config(self) -> Dict[str, Any]:
        """
        Get event bus configuration.
        
        Returns:
            Event bus configuration dictionary
        """
        event_bus_type = self.get("EVENT_BUS_TYPE")
        
        if event_bus_type == "kafka":
            return {
                "type": "kafka",
                "bootstrap_servers": self.get("KAFKA_BOOTSTRAP_SERVERS")
            }
        elif event_bus_type == "azure":
            return {
                "type": "azure",
                "connection_string": self.get("AZURE_SERVICE_BUS_CONNECTION_STRING")
            }
        else:
            return {
                "type": "memory"
            }
            
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM configuration.
        
        Returns:
            LLM configuration dictionary
        """
        llm_type = self.get("LLM_TYPE")
        
        if llm_type == "openai":
            return {
                "type": "openai",
                "api_key": self.get("OPENAI_API_KEY"),
                "model": self.get("OPENAI_MODEL"),
                "temperature": 0.0
            }
        elif llm_type == "azure_openai":
            return {
                "type": "azure_openai",
                "api_key": self.get("AZURE_OPENAI_API_KEY"),
                "endpoint": self.get("AZURE_OPENAI_ENDPOINT"),
                "api_version": self.get("AZURE_OPENAI_API_VERSION"),
                "model": self.get("OPENAI_MODEL"),
                "temperature": 0.0
            }
        elif llm_type == "mock":
            return {
                "type": "mock",
                "responses": {}
            }
        else:
            # Default to mock for testing
            return {
                "type": "mock",
                "responses": {}
            }
            
    def get_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get agent configurations.
        
        Returns:
            Dictionary of agent configurations
        """
        examples_path = self.get("EXAMPLES_PATH")
        xslt_path = self.get("XSLT_PATH")
        llm_config = self.get_llm_config()
        
        # Configuration for ISO claim transformer agent
        iso_claim_transformer_config = {
            "type": "transformer",
            "examples_path": os.path.join(examples_path, "iso_claim"),
            "xslt_path": os.path.join(xslt_path, "iso_claim.xslt"),
            "llm": llm_config
        }
        
        # Configuration for batch processor agent
        batch_processor_config = {
            "type": "processor",
            "llm": llm_config
        }
        
        # Configuration for validator agent
        validator_config = {
            "type": "validator",
            "llm": llm_config
        }
        
        # Return all agent configurations
        return {
            "validator.iso_claim": validator_config,
            "transformer.iso_claim": iso_claim_transformer_config,
            "process.claim_routing": batch_processor_config,
            "integration.destination_system": {
                "type": "integration",
                "llm": llm_config
            }
        }
        
    def get_api_config(self) -> Dict[str, Any]:
        """
        Get API configuration.
        
        Returns:
            API configuration dictionary
        """
        return {
            "host": self.get("API_HOST"),
            "port": self.get("API_PORT"),
            "debug": self.get("API_DEBUG")
        } 