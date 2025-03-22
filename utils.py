"""
Utility functions for the ESB LLM Orchestrator.
"""
import logging
import os
import json
import re
import time
import lxml.etree as ET
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Configure logging
def setup_logging(log_file: str = "app.log", level=logging.INFO) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file: Path to the log file
        level: Logging level
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

# XML validation functions
def is_valid_xml(xml_content: str) -> bool:
    """
    Check if the XML content is valid.
    
    Args:
        xml_content: XML content to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Remove XML declaration if present to avoid Unicode encoding issues
        if xml_content.strip().startswith('<?xml'):
            # Find the end of the XML declaration
            decl_end = xml_content.find('?>')
            if decl_end > 0:
                xml_content = xml_content[decl_end + 2:].strip()
        
        ET.fromstring(xml_content)
        return True
    except ET.XMLSyntaxError as e:
        print(f"XML validation error: {e}")
        return False

def validate_against_schema(xml_content: str, xsd_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate XML content against an XSD schema.
    
    Args:
        xml_content: XML content to validate
        xsd_path: Path to the XSD schema file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        xmlschema_doc = ET.parse(xsd_path)
        xmlschema = ET.XMLSchema(xmlschema_doc)
        
        doc = ET.fromstring(xml_content)
        xmlschema.assertValid(doc)
        return True, None
    except ET.XMLSyntaxError as e:
        return False, f"Invalid XML syntax: {str(e)}"
    except ET.DocumentInvalid as e:
        return False, f"XML does not conform to schema: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

# File operations
def ensure_dir(directory: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory: Directory path to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_trace(trace_data: Dict[str, Any], filename: str, trace_dir: str = "traces") -> str:
    """
    Save trace information to a file.
    
    Args:
        trace_data: Trace data to save
        filename: Base filename
        trace_dir: Directory to save traces
        
    Returns:
        str: Path to the saved trace file
    """
    ensure_dir(trace_dir)
    timestamp = int(time.time())
    trace_file = os.path.join(trace_dir, f"{filename}_{timestamp}.json")
    
    with open(trace_file, 'w', encoding='utf-8') as f:
        json.dump(trace_data, f, indent=2)
    
    return trace_file

def load_examples(path: str) -> List[Dict[str, str]]:
    """
    Load example transformations from a directory or file.
    
    Args:
        path: Path to examples directory or file
        
    Returns:
        List of examples as dictionaries with input/output keys
    """
    examples = []
    
    if os.path.isdir(path):
        files = os.listdir(path)
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                    examples.append(json.load(f))
    elif os.path.isfile(path) and path.endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                examples.extend(data)
            else:
                examples.append(data)
                
    return examples

# XSLT functions
def format_tag_if_needed(xml_content: str) -> str:
    """
    This function previously modified XML tags but is now a pass-through.
    The XSLT and XML files already use consistent <n> tags, so no replacement is needed.
    """
    # No changes needed - the XML tags are already in the correct format
    return xml_content

def apply_xslt_transformation(xml_content: str, xslt_path: str) -> str:
    """Apply XSLT transformation to XML content."""
    try:
        # XML content already has proper tags, no need for format_tag_if_needed
        
        # Parse the XSLT file
        xslt_doc = ET.parse(xslt_path)
        transform = ET.XSLT(xslt_doc)
        
        # Parse the XML content
        xml_doc = ET.fromstring(xml_content.encode('utf-8'))
        
        # Apply the transformation
        result_tree = transform(xml_doc)
        
        # Convert to string
        result = ET.tostring(result_tree, pretty_print=True, encoding='utf-8').decode('utf-8')
        return result
    except Exception as e:
        logging.error(f"XSLT transformation error: {str(e)}")
        return ""

# Performance tracking
class PerformanceTracker:
    """Class to track performance metrics for transformations."""
    
    def __init__(self):
        self.transformations = []
        
    def add_transformation(self, duration, input_size, output_size):
        """
        Add a transformation record.
        
        Args:
            duration: Time taken to process in seconds
            input_size: Size of the input data in characters
            output_size: Size of the output data in characters
        """
        self.transformations.append({
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'input_size': input_size,
            'output_size': output_size,
            'success': True
        })
    
    def get_avg_processing_time(self) -> float:
        """Calculate average processing time for all transformations."""
        if not self.transformations:
            return 0.0
        return sum(t.get('duration', t.get('processing_time', 0)) for t in self.transformations) / len(self.transformations)
    
    def get_success_rate(self) -> float:
        """Calculate success rate for all transformations."""
        if not self.transformations:
            return 0.0
        successful = sum(1 for t in self.transformations if t.get('success', False))
        return successful / len(self.transformations)
    
    def get_llm_usage_rate(self) -> float:
        """Calculate rate of LLM usage for transformations."""
        if not self.transformations:
            return 0.0
        llm_used = sum(1 for t in self.transformations if t.get('used_llm', True))
        return llm_used / len(self.transformations)
    
    def get_xslt_fallback_rate(self) -> float:
        """Calculate rate of XSLT fallback for transformations."""
        if not self.transformations:
            return 0.0
        xslt_used = sum(1 for t in self.transformations if t.get('used_xslt', False))
        return xslt_used / len(self.transformations)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        if not self.transformations:
            return {
                'count': 0,
                'avg_duration': 0,
                'max_duration': 0,
                'min_duration': 0,
                'total_duration': 0,
                'avg_input_size': 0,
                'avg_output_size': 0,
                'success_rate': 0
            }
            
        # Calculate metrics
        durations = [t.get('duration', t.get('processing_time', 0)) for t in self.transformations]
        input_sizes = [t.get('input_size', 0) for t in self.transformations]
        output_sizes = [t.get('output_size', 0) for t in self.transformations]
        
        return {
            'count': len(self.transformations),
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'total_duration': sum(durations),
            'avg_input_size': sum(input_sizes) / len(input_sizes) if input_sizes else 0,
            'avg_output_size': sum(output_sizes) / len(output_sizes) if output_sizes else 0,
            'success_rate': self.get_success_rate() * 100,
            'transformations': self.transformations[-10:] if self.transformations else []
        }
        
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of performance metrics for the metrics endpoint.
        
        Returns:
            Dict: Performance metrics summary
        """
        metrics = self.get_metrics()
        
        return {
            'total': metrics['count'],
            'completed': int(metrics['count'] * metrics['success_rate'] / 100),
            'pending': 0,
            'errors': metrics['count'] - int(metrics['count'] * metrics['success_rate'] / 100),
            'avg_processing_time': metrics['avg_duration'],
            'success_rate': metrics['success_rate']
        } 