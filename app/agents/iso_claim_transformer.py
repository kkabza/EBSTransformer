"""
ISO Claim Transformer Agent - Transforms ISO claim data using LLMs.
"""
import logging
import json
import os
import lxml.etree as ET
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)

class ISOClaimTransformerAgent(BaseAgent):
    """
    Agent for transforming ISO claims using LLM.
    This replaces the BizTalk XSLT transformation for ISO claims.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the ISO claim transformer agent.
        
        Args:
            name: Agent name
            config: Configuration dictionary
        """
        super().__init__(name, config)
        self.examples_path = config.get("examples_path")
        self.xslt_path = config.get("xslt_path")
        self.examples = self._load_examples()
        self.xslt_transformer = self._setup_xslt() if self.xslt_path else None
        
    def _setup_llm_client(self) -> LLMClient:
        """
        Set up the LLM client.
        
        Returns:
            LLM client instance
        """
        from app.services.llm_client import OpenAIClient, AzureOpenAIClient, MockLLMClient
        
        llm_config = self.config.get("llm", {})
        llm_type = llm_config.get("type", "openai")
        
        if llm_type == "openai":
            return OpenAIClient(llm_config)
        elif llm_type == "azure_openai":
            return AzureOpenAIClient(llm_config)
        elif llm_type == "mock":
            return MockLLMClient(llm_config)
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")
            
    def _load_examples(self) -> List[Dict[str, Any]]:
        """
        Load examples from the examples path.
        
        Returns:
            List of example dictionaries
        """
        examples = []
        
        if not self.examples_path or not os.path.exists(self.examples_path):
            self.log_warning(f"Examples path {self.examples_path} not found or not provided")
            return examples
            
        try:
            # Check if the examples path is a directory or a file
            if os.path.isdir(self.examples_path):
                # Load all JSON files in the directory
                for filename in os.listdir(self.examples_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(self.examples_path, filename)
                        with open(file_path, "r") as f:
                            example = json.load(f)
                            examples.append(example)
            else:
                # Load a single JSON file
                with open(self.examples_path, "r") as f:
                    if self.examples_path.endswith(".json"):
                        # Load as JSON
                        example_data = json.load(f)
                        if isinstance(example_data, list):
                            examples.extend(example_data)
                        else:
                            examples.append(example_data)
                            
            self.log_info(f"Loaded {len(examples)} examples")
        except Exception as e:
            self.log_error(f"Error loading examples: {str(e)}")
            
        return examples
        
    def _setup_xslt(self) -> Optional[ET.XSLT]:
        """
        Set up the XSLT transformer for fallback.
        
        Returns:
            XSLT transformer or None if not available
        """
        if not self.xslt_path or not os.path.exists(self.xslt_path):
            self.log_warning(f"XSLT path {self.xslt_path} not found or not provided")
            return None
            
        try:
            xslt_doc = ET.parse(self.xslt_path)
            xslt_transformer = ET.XSLT(xslt_doc)
            self.log_info("Loaded XSLT transformer for fallback")
            return xslt_transformer
        except Exception as e:
            self.log_error(f"Error loading XSLT transformer: {str(e)}")
            return None
            
    def _format_examples(self) -> str:
        """
        Format examples for few-shot learning.
        
        Returns:
            Formatted examples string
        """
        if not self.examples:
            return ""
            
        formatted_examples = "Here are examples of transformations:\n\n"
        
        for i, example in enumerate(self.examples[:3]):  # Use up to 3 examples
            source = example.get("source", "")
            target = example.get("target", "")
            
            formatted_examples += f"Example {i+1}:\n"
            formatted_examples += "Source:\n"
            formatted_examples += f"{source}\n\n"
            formatted_examples += "Target:\n"
            formatted_examples += f"{target}\n\n"
            
        return formatted_examples
        
    def _apply_xslt(self, xml_content: str) -> str:
        """
        Apply XSLT transformation as fallback.
        
        Args:
            xml_content: XML content to transform
            
        Returns:
            Transformed XML content
        """
        if not self.xslt_transformer:
            self.log_error("XSLT transformer not available for fallback")
            return ""
            
        try:
            xml_doc = ET.fromstring(xml_content.encode('utf-8'))
            result = self.xslt_transformer(xml_doc)
            return str(result)
        except Exception as e:
            self.log_error(f"Error applying XSLT transformation: {str(e)}")
            return ""
            
    def _validate_transformation(self, transformed_data: str) -> Dict[str, Any]:
        """
        Validate the transformation against expected schema.
        
        Args:
            transformed_data: Transformed data to validate
            
        Returns:
            Validation result dictionary
        """
        # This would be replaced with actual schema validation logic
        # For now, just check if it looks like XML
        try:
            if transformed_data.strip().startswith("<") and transformed_data.strip().endswith(">"):
                # Try to parse as XML
                ET.fromstring(transformed_data.encode('utf-8'))
                return {"valid": True}
            else:
                return {
                    "valid": False,
                    "errors": ["Result is not valid XML"]
                }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)]
            }
            
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process ISO claim data in the context.
        
        Args:
            context: Context dictionary with ISO claim data
            
        Returns:
            Updated context with transformed claim data
        """
        # Extract ISO claim data from context
        claim_data = context.get("claim_data")
        if not claim_data:
            self.log_error("No claim data found in context")
            context["status"] = "error"
            context["error"] = "No claim data found in context"
            return context
            
        self.log_info("Processing ISO claim data")
        
        # Prepare examples for few-shot learning
        examples_prompt = self._format_examples()
        
        # Build transformation prompt
        transform_prompt = f"""
        You are a data transformation expert. Transform the following ISO claim XML data
        according to the specified rules and examples.
        
        {examples_prompt}
        
        Source XML:
        {claim_data}
        
        Transformation Rules:
        1. Maintain the same basic XML structure but adapt to the target format.
        2. Ensure all claim IDs, policy numbers, and dates are preserved exactly.
        3. Format dates consistently as ISO 8601 (YYYY-MM-DD).
        4. Convert all monetary values to include two decimal places.
        5. Preserve all required fields from the source.
        
        Target format:
        """
        
        try:
            # Get LLM to perform transformation
            self.log_info("Sending transformation request to LLM")
            transformed_claim = await self.llm_client.complete(transform_prompt)
            
            # Validate the transformation
            validation_result = self._validate_transformation(transformed_claim)
            
            if validation_result.get("valid", False):
                self.log_info("LLM transformation successful")
                context["transformed_claim"] = transformed_claim
                context["transformation_method"] = "llm"
            else:
                # Log validation failure
                self.log_warning(
                    "LLM transformation validation failed", 
                    {"errors": validation_result.get("errors", [])}
                )
                
                # Fall back to XSLT if available
                if self.xslt_transformer:
                    self.log_info("Falling back to XSLT transformation")
                    xslt_result = self._apply_xslt(claim_data)
                    if xslt_result:
                        context["transformed_claim"] = xslt_result
                        context["transformation_method"] = "xslt_fallback"
                        context["llm_errors"] = validation_result.get("errors", [])
                    else:
                        context["status"] = "error"
                        context["error"] = "XSLT fallback transformation failed"
                else:
                    context["status"] = "error"
                    context["error"] = "LLM transformation failed and no XSLT fallback available"
                    context["llm_errors"] = validation_result.get("errors", [])
        except Exception as e:
            self.log_error(f"Error during transformation: {str(e)}")
            
            # Fall back to XSLT if available
            if self.xslt_transformer:
                self.log_info("Falling back to XSLT transformation due to exception")
                xslt_result = self._apply_xslt(claim_data)
                if xslt_result:
                    context["transformed_claim"] = xslt_result
                    context["transformation_method"] = "xslt_fallback"
                    context["llm_errors"] = [str(e)]
                else:
                    context["status"] = "error"
                    context["error"] = f"Transformation failed: {str(e)}"
            else:
                context["status"] = "error"
                context["error"] = f"Transformation failed: {str(e)}"
                
        return context 