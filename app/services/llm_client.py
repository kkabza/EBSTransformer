"""
LLM Client - Interface for LLM providers.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Base class for LLM clients.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM client.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate a completion from the LLM.
        
        Args:
            prompt: The prompt to complete
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            The generated completion
        """
        raise NotImplementedError("Subclasses must implement complete")
        
    async def complete_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a JSON completion from the LLM.
        
        Args:
            prompt: The prompt to complete
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            The generated completion as a dictionary
        """
        raise NotImplementedError("Subclasses must implement complete_with_json")

class OpenAIClient(LLMClient):
    """
    OpenAI API client.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OpenAI client.
        
        Args:
            config: Configuration dictionary with api_key and model
        """
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=config["api_key"])
            self.model = config.get("model", "gpt-4")
            self.temperature = config.get("temperature", 0.0)
            self.max_tokens = config.get("max_tokens", 1000)
            logger.info(f"Initialized OpenAI client with model {self.model}")
        except ImportError:
            logger.error("OpenAI package not installed. Please install it with 'pip install openai'")
            raise
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise
        
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate a completion from the OpenAI API.
        
        Args:
            prompt: The prompt to complete
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The generated completion
        """
        try:
            # Override default parameters with kwargs
            model = kwargs.get("model", self.model)
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise
        
    async def complete_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a JSON completion from the OpenAI API.
        
        Args:
            prompt: The prompt to complete
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The generated completion as a dictionary
        """
        try:
            # Add instruction to return JSON
            json_prompt = f"{prompt}\n\nPlease respond with valid JSON only, with no other text."
            
            # Override default parameters with kwargs
            model = kwargs.get("model", self.model)
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": json_prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            json_str = response.choices[0].message.content
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from OpenAI API")
            # Try to extract JSON from the response if it's not pure JSON
            try:
                json_str = response.choices[0].message.content
                # Find JSON-like content between curly braces
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                if start >= 0 and end > start:
                    extracted_json = json_str[start:end]
                    return json.loads(extracted_json)
                else:
                    # Return empty dict if no JSON found
                    return {}
            except Exception:
                # Return empty dict if extraction fails
                return {}
        except Exception as e:
            logger.error(f"Error generating JSON completion: {str(e)}")
            raise

class AzureOpenAIClient(OpenAIClient):
    """
    Azure OpenAI API client.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Azure OpenAI client.
        
        Args:
            config: Configuration dictionary with api_key, model, endpoint
        """
        # Call parent constructor with config
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncAzureOpenAI(
                api_key=config["api_key"],
                api_version=config.get("api_version", "2023-12-01-preview"),
                azure_endpoint=config["endpoint"]
            )
            logger.info(f"Initialized Azure OpenAI client with model {self.model}")
        except ImportError:
            logger.error("OpenAI package not installed. Please install it with 'pip install openai'")
            raise
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI client: {str(e)}")
            raise

class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the mock LLM client.
        
        Args:
            config: Configuration dictionary with responses
        """
        super().__init__(config)
        self.responses = config.get("responses", {})
        logger.info("Initialized mock LLM client")
        
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate a completion from the mock client.
        
        Args:
            prompt: The prompt to complete
            **kwargs: Additional arguments (ignored)
            
        Returns:
            The pre-configured mock response or a default response
        """
        # Check if we have a pre-configured response for this prompt
        for key, response in self.responses.items():
            if key in prompt:
                logger.info(f"Using pre-configured response for prompt containing '{key}'")
                return response
        
        # Return a default response
        logger.info("Using default mock response")
        return f"Mock response for: {prompt[:50]}..."
        
    async def complete_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a JSON completion from the mock client.
        
        Args:
            prompt: The prompt to complete
            **kwargs: Additional arguments (ignored)
            
        Returns:
            The pre-configured mock response as a dictionary or a default response
        """
        # Check if we have a pre-configured response for this prompt
        for key, response in self.responses.items():
            if key in prompt:
                logger.info(f"Using pre-configured JSON response for prompt containing '{key}'")
                if isinstance(response, str):
                    try:
                        return json.loads(response)
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON in mock response"}
                elif isinstance(response, dict):
                    return response
        
        # Return a default response
        logger.info("Using default mock JSON response")
        return {"mock": True, "prompt": prompt[:50]} 