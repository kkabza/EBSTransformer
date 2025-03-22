"""
Main entry point for the ESB LLM Orchestrator Application with OpenAI Agents SDK.
"""
import os
import asyncio
import sys
from threading import Thread
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import uuid
import time
from datetime import datetime
import json
from dotenv import load_dotenv
import logging
import re

# Import OpenAI Agents SDK - required for this application (no fallback)
try:
    from openai import OpenAI
    from agents import Agent, Runner, function_tool
    print("Successfully imported OpenAI Agents SDK")
except ImportError:
    print("ERROR: OpenAI Agents SDK not found. Please install it with 'pip install openai-agents'")
    print("Refer to: https://github.com/openai/openai-agents-python/blob/main/README.md")
    sys.exit(1)

from utils import (
    setup_logging, 
    is_valid_xml, 
    apply_xslt_transformation, 
    load_examples, 
    save_trace,
    ensure_dir,
    PerformanceTracker
)

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'xml', 'json', 'txt', 'csv'}
app.config['TRACES_FOLDER'] = 'traces'
app.config['SCHEMAS_FOLDER'] = 'schemas'

# Ensure directories exist
ensure_dir(app.config['UPLOAD_FOLDER'])
ensure_dir(app.config['TRACES_FOLDER'])
ensure_dir('examples')
ensure_dir('xslt')
ensure_dir(app.config['SCHEMAS_FOLDER'])

# Store transformation results
transformation_results = {}

# Initialize performance tracker
performance_tracker = PerformanceTracker()

# Create a folder for schema uploads
os.makedirs('schema_uploads', exist_ok=True)

def allowed_file(filename, allowed_extensions=None):
    """Check if file has an allowed extension"""
    if allowed_extensions is None:
        allowed_extensions = app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@function_tool
def load_xslt_transformer(xslt_path: str) -> str:
    """
    Load an XSLT transformer from a file
    
    Parameters:
    xslt_path (str): Path to the XSLT file
    
    Returns:
    str: Content of the XSLT file
    """
    with open(xslt_path, 'r') as f:
        return f.read()

@function_tool
def apply_xslt_transformation_tool(xml_content: str, xslt_path: str) -> str:
    """Apply XSLT transformation to XML content"""
    result = apply_xslt_transformation(xml_content, xslt_path)
    if result.startswith("Error"):
        return result
    return f"Successfully applied XSLT transformation. Result: {result[:100]}..."

@function_tool
def load_example_transformations_tool(examples_path: str) -> str:
    """Load example transformations from a path"""
    examples = load_examples(examples_path)
    return f"Loaded {len(examples)} example transformations from {examples_path}"

@function_tool
def validate_xml_tool(xml_content: str) -> str:
    """Validate XML content"""
    if is_valid_xml(xml_content):
        return "XML is valid"
    else:
        return "XML validation error: The XML is not well-formed"

@function_tool
def parse_csv_tool(csv_content: str) -> str:
    """Parse CSV data and return structured format"""
    try:
        import csv
        from io import StringIO
        import json
        
        # Parse CSV
        csv_io = StringIO(csv_content.strip())
        reader = csv.reader(csv_io)
        
        # Get headers from first row
        headers = next(reader)
        
        # Parse rows
        rows = []
        for row in reader:
            if len(row) == len(headers):
                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                rows.append(row_dict)
        
        # Return structured data as JSON string for easy parsing
        result = {
            "headers": headers,
            "rows": rows,
            "row_count": len(rows)
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error parsing CSV: {str(e)}"

def create_transformer_agent(examples_path=None, xslt_path=None):
    """
    Create an Agent for data transformation using the OpenAI Agents SDK
    
    Args:
        examples_path: Path to example files
        xslt_path: Path to XSLT templates
        
    Returns:
        Agent: Configured Agent instance
    """
    # Set up instructions for the agent
    instructions = """
    You are an expert data transformation specialist. Your expertise is in converting data between different formats 
    while ensuring data integrity and structural correctness.
    
    Your task is to transform the provided data file to the target format. Depending on the source file type:
    
    1. For XML input files:
       - Transform them to the target XML structure
       - Preserve all data elements
       - Ensure proper XML syntax and element nesting
       
    2. For JSON input files:
       - Convert JSON to the target XML format
       - Map JSON properties to appropriate XML elements
       - Create a properly structured XML document
       
    3. For CSV input files:
       - Convert CSV data to XML
       - Use appropriate element names based on column headers
       - Properly structure the XML hierarchy
    
    Always ensure your output is valid, well-formed XML. Validate the XML structure before returning it.
    If provided with example data or schemas, use those as guides for the required output format.
    
    IMPORTANT: Your final response should ONLY contain the XML output. Do NOT include any explanatory text, markdown formatting,
    or code blocks. Return ONLY the raw XML content, starting with the XML declaration if needed.
    """
    
    # Create the agent with the OpenAI Agents SDK
    agent = Agent(
        name="Transformer",
        instructions=instructions,
        tools=[
            load_xslt_transformer,
            apply_xslt_transformation_tool,
            load_example_transformations_tool,
            validate_xml_tool,
            parse_csv_tool
        ]
    )
    
    return agent

async def process_file_transformation(file_path, result_id, examples_path=None, xslt_path=None, schema_path=None):
    """Process a file transformation using the OpenAI Agents SDK"""
    start_time = time.time()
    
    # Re-initialize the logger in this thread
    thread_logger = logging.getLogger('main')
    
    with open("debug.log", "a") as debug_file:
        debug_file.write(f"{datetime.now().isoformat()} - Starting process_file_transformation for result_id: {result_id}\n")
        debug_file.write(f"File path: {file_path}\n")
        debug_file.write(f"Examples path: {examples_path}\n")
        debug_file.write(f"XSLT path: {xslt_path}\n")
        debug_file.write(f"Schema path: {schema_path}\n")
        
    transformation_results[result_id] = {
        'status': 'processing',
        'start_time': start_time,
    }
    
    try:
        # Create the transformer agent
        with open("debug.log", "a") as debug_file:
            debug_file.write(f"{datetime.now().isoformat()} - Creating transformer agent...\n")
            debug_file.write(f"OpenAI API Key status: {os.environ.get('OPENAI_API_KEY', 'Not set')[:5]}...\n")
            
        agent = create_transformer_agent(examples_path, xslt_path)
        
        with open("debug.log", "a") as debug_file:
            debug_file.write(f"{datetime.now().isoformat()} - Transformer agent created successfully\n")
            
        # Read the file content
        with open("debug.log", "a") as debug_file:
            debug_file.write(f"{datetime.now().isoformat()} - Reading file content from {file_path}\n")
            
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            
        with open("debug.log", "a") as debug_file:
            debug_file.write(f"{datetime.now().isoformat()} - File content read successfully, length: {len(file_content)} characters\n")
            
        # Determine file type based on extension
        file_type = os.path.splitext(file_path)[1].lower()
        is_csv = file_type == '.csv'
        is_json = file_type == '.json'
        is_xml = file_type in ['.xml', '.txt']
            
        # Prepare the input message
        input_message = f"Transform the following claim data file of type {file_type[1:].upper()}."
        
        if examples_path:
            if os.path.exists(examples_path):
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Examples path exists: {examples_path}\n")
                input_message += f" First load the example transformations at {examples_path} for reference."
            else:
                thread_logger.warning(f"Examples path does not exist: {examples_path}")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - WARNING: Examples path does not exist: {examples_path}\n")
                    
        if xslt_path:
            if os.path.exists(xslt_path):
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - XSLT path exists: {xslt_path}\n")
                input_message += f" Use XSLT templates from {xslt_path} if appropriate."
            else:
                thread_logger.warning(f"XSLT path does not exist: {xslt_path}")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - WARNING: XSLT path does not exist: {xslt_path}\n")
                    
        if schema_path:
            if os.path.exists(schema_path):
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Schema path exists: {schema_path}\n")
                
                # Add specific instructions based on the file type and schema
                if is_csv and 'safelite' in schema_path.lower():
                    input_message += f" This is a Safelite glass claim CSV. Transform it into the SafeliteClaimsBatch XML format following the schema at {schema_path}."
                elif is_json and 'iso' in schema_path.lower():
                    input_message += f" This is an ISO format JSON claim. Transform it into the proper XML format following the schema at {schema_path}."
                else:
                    input_message += f" Validate against the schema at {schema_path}."
            else:
                thread_logger.warning(f"Schema path does not exist: {schema_path}")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - WARNING: Schema path does not exist: {schema_path}\n")
                    
        # Add the file content to the input message
        input_message += f"\n\nFile content:\n```\n{file_content}\n```"
        
        thread_logger.info(f"Input message prepared, length: {len(input_message)} characters")
        
        # Run the agent
        with open("debug.log", "a") as debug_file:
            debug_file.write(f"{datetime.now().isoformat()} - About to run agent with Runner.run for result_id: {result_id}\n")
            debug_file.write(f"OpenAI API Key status: {os.environ.get('OPENAI_API_KEY', 'Not set')[:5]}...\n")
            
        thread_logger.info(f"Running agent with Runner.run for result_id: {result_id}")
        thread_logger.info("OpenAI API Key status: " + ("Set" if os.environ.get('OPENAI_API_KEY') else "Not Set"))
        
        try:
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - Calling Runner.run now...\n")
                
            result = await Runner.run(agent, input=input_message)
            
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - Agent run completed successfully for result_id: {result_id}\n")
                
            thread_logger.info(f"Agent run completed successfully for result_id: {result_id}")
            
            # Extract content from result - using the official OpenAI Agents SDK format
            if hasattr(result, 'final_output'):
                transformed_content = result.final_output
            else:
                # If the result doesn't have the expected format, check for content in the standard OpenAI response
                thread_logger.warning("Final output not found, checking last message content")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Final output not found, checking last message content\n")
                
                if hasattr(result, 'messages') and result.messages:
                    transformed_content = result.messages[-1].content
                else:
                    thread_logger.error("Unexpected result format from OpenAI agent")
                    with open("debug.log", "a") as debug_file:
                        debug_file.write(f"{datetime.now().isoformat()} - ERROR: Unexpected result format from OpenAI agent\n")
                    raise RuntimeError("Unexpected result format from OpenAI agent")
            
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - Transformed content extracted, length: {len(transformed_content)} characters\n")
                
            thread_logger.info(f"Transformed content extracted, length: {len(transformed_content)} characters")
            
            # Check if the content is wrapped in markdown code blocks and extract the XML
            xml_pattern = re.compile(r'```(?:xml)?\s*([\s\S]*?)```')
            markdown_match = xml_pattern.search(transformed_content)
            
            if markdown_match:
                xml_content = markdown_match.group(1).strip()
                thread_logger.info(f"Extracted XML content from markdown, length: {len(xml_content)} characters")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Extracted XML content from markdown\n")
                transformed_content = xml_content
            
            # For CSV to XML transformations, ensure the proper root element structure
            if file_path.lower().endswith('.csv') and schema_path and 'safelite' in schema_path.lower():
                # Check if the XML is missing the SafeliteClaimsBatch root element
                if not transformed_content.strip().startswith('<?xml') and not transformed_content.strip().startswith('<SafeliteClaimsBatch'):
                    
                    # If it's just Claims or Claim elements, wrap it properly
                    if '<Claims>' in transformed_content or '<Claim>' in transformed_content:
                        batch_id = f"SFB{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        claims_count = transformed_content.count('<Claim>')
                        
                        # If we have only Claim elements but no Claims wrapper
                        if '<Claims>' not in transformed_content and '<Claim>' in transformed_content:
                            transformed_content = f"<Claims>\n{transformed_content}\n</Claims>"
                        
                        # Now wrap in SafeliteClaimsBatch
                        transformed_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<SafeliteClaimsBatch>
    <BatchInfo>
        <BatchId>{batch_id}</BatchId>
        <GeneratedDate>{datetime.now().isoformat()}</GeneratedDate>
        <ClaimCount>{claims_count}</ClaimCount>
    </BatchInfo>
    {transformed_content}
</SafeliteClaimsBatch>"""
                        
                        thread_logger.info(f"Enhanced XML structure for Safelite format, new length: {len(transformed_content)} characters")
                        with open("debug.log", "a") as debug_file:
                            debug_file.write(f"{datetime.now().isoformat()} - Enhanced XML structure for Safelite format\n")
            
            # Fix Customer/Name structure if needed (replace <n> with <Name>)
            if '<Customer>' in transformed_content and '<n>' in transformed_content:
                transformed_content = transformed_content.replace('<n>', '<Name>').replace('</n>', '</Name>')
                thread_logger.info("Fixed Customer/Name element structure")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Fixed Customer/Name element structure\n")
            
            # Validate the result as XML
            if is_valid_xml(transformed_content):
                thread_logger.info("Transformed content is valid XML")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Transformed content is valid XML\n")
                    
                # Save the result
                result_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{result_id}_result.xml")
                with open(result_file_path, 'w', encoding='utf-8') as result_file:
                    result_file.write(transformed_content)
                    
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Result saved to {result_file_path}\n")
                    
                thread_logger.info(f"Result saved to {result_file_path}")
                
                # Save trace
                trace_file_path = os.path.join(app.config['TRACES_FOLDER'], f"{result_id}_trace.json")
                
                # Create a simplified trace format using the result
                if hasattr(result, 'messages'):
                    messages = [{'role': msg.role, 'content': msg.content} for msg in result.messages]
                    trace = {
                        'messages': messages,
                        'result_id': result_id,
                        'timestamp': datetime.now().isoformat()
                    }
                    save_trace(trace_file_path, trace)
                    thread_logger.info(f"Trace saved to {trace_file_path}")
                else:
                    thread_logger.warning("No messages found in result, skipping trace saving")
                
                # Update the result
                end_time = time.time()
                duration = end_time - start_time
                transformation_results[result_id].update({
                    'status': 'completed',
                    'end_time': end_time,
                    'duration': duration,
                    'result_file': result_file_path,
                    'trace_file': trace_file_path if hasattr(result, 'messages') else None
                })
                
                # Update performance tracker
                performance_tracker.add_transformation(duration, len(file_content), len(transformed_content))
                
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Transformation completed successfully for result_id: {result_id}\n")
                    debug_file.write(f"{datetime.now().isoformat()} - Duration: {duration:.2f} seconds\n")
                    
                thread_logger.info(f"Transformation completed successfully for result_id: {result_id}")
                thread_logger.info(f"Duration: {duration:.2f} seconds")
                
            else:
                thread_logger.error("Transformed content is not valid XML")
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - ERROR: Transformed content is not valid XML\n")
                    
                # Save the result anyway for debugging
                result_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{result_id}_result.txt")
                with open(result_file_path, 'w', encoding='utf-8') as result_file:
                    result_file.write(transformed_content)
                    
                # Update the result
                end_time = time.time()
                transformation_results[result_id].update({
                    'status': 'error',
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'error': 'Invalid XML result',
                    'result_file': result_file_path
                })
                
                with open("debug.log", "a") as debug_file:
                    debug_file.write(f"{datetime.now().isoformat()} - Transformation failed for result_id: {result_id}\n")
                    
                thread_logger.error(f"Transformation failed for result_id: {result_id}")
                
        except Exception as e:
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - Error during agent execution: {str(e)}\n")
                
            thread_logger.error(f"Error during agent execution: {str(e)}")
            raise
            
    except Exception as e:
        with open("debug.log", "a") as debug_file:
            debug_file.write(f"{datetime.now().isoformat()} - Error during transformation: {str(e)}\n")
            import traceback
            debug_file.write(f"{datetime.now().isoformat()} - {traceback.format_exc()}\n")
            
        thread_logger.error(f"Error during transformation: {str(e)}")
        thread_logger.error(traceback.format_exc())
        
        # Update the result
        end_time = time.time()
        transformation_results[result_id].update({
            'status': 'error',
            'end_time': end_time,
            'duration': end_time - start_time,
            'error': str(e)
        })
        
    with open("debug.log", "a") as debug_file:
        debug_file.write(f"{datetime.now().isoformat()} - Async task completed successfully\n")
        debug_file.write(f"{datetime.now().isoformat()} - Async task thread ended\n")
        
    thread_logger.info("Async task completed successfully")
    thread_logger.info("Async task thread ended")

def run_async_task(coroutine, *args, **kwargs):
    """Run an async task in a new thread to avoid blocking the Flask app"""
    loop = asyncio.new_event_loop()
    
    def run_in_thread(loop, coro, *args, **kwargs):
        try:
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - Starting async task thread\n")
                debug_file.write(f"Args: {args}\n")
                debug_file.write(f"Kwargs: {kwargs}\n")
                
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro(*args, **kwargs))
            
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - Async task completed successfully\n")
                
        except Exception as e:
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - ERROR in async task: {str(e)}\n")
                import traceback
                debug_file.write(traceback.format_exc())
        finally:
            loop.close()
            with open("debug.log", "a") as debug_file:
                debug_file.write(f"{datetime.now().isoformat()} - Async task thread ended\n")
    
    with open("debug.log", "a") as debug_file:
        debug_file.write(f"{datetime.now().isoformat()} - Launching async task thread\n")
        
    thread = Thread(target=run_in_thread, args=(loop, coroutine, *args), kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/visualization')
def visualization():
    """
    Visualization page for transformation metrics
    """
    # Get the metrics for visualization
    metrics = performance_tracker.get_metrics()
    
    # Format timestamp for display
    for result_id, result in transformation_results.items():
        if "end_time" in result:
            result["formatted_time"] = datetime.fromtimestamp(result["end_time"]).strftime('%Y-%m-%d %H:%M:%S')
        else:
            result["formatted_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Sort results by timestamp (newest first)
    recent_transformations = sorted(
        transformation_results.items(),
        key=lambda x: x[1].get("end_time", 0),
        reverse=True
    )[:10]  # Get the 10 most recent
    
    return render_template(
        'visualization.html', 
        metrics=metrics, 
        transformations=recent_transformations
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload for transformation"""
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # If no file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Check if the file type is allowed
    if file and allowed_file(file.filename):
        # Store result ID and initial status
        result_id = str(uuid.uuid4())
        original_filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{result_id}_{original_filename}")
        
        # Create a logger specific to this thread
        thread_logger = logging.getLogger('main')
        
        # Determine file type
        file_extension = os.path.splitext(original_filename)[1].lower()
        if file_extension == '.json':
            file_type = "json"
        elif file_extension == '.csv':
            file_type = "csv"
        else:
            file_type = "xml"
        
        # Log the uploaded file
        thread_logger.info(f"File uploaded: {original_filename}, result_id: {result_id}")
        
        # Create a transformation result entry
        transformation_results[result_id] = {
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "filename": original_filename,
            "file_type": file_type
        }
        
        # Save the file
        file.save(file_path)
        
        # Get transformation parameters
        examples_path = request.form.get('examples_path', None)
        xslt_path = request.form.get('xslt_path', None)
        schema_path = request.form.get('schema_path', None)
        
        # Set default schema path based on file type if not provided
        if not schema_path and file_type == "csv":
            schema_path = os.path.join('schemas', 'safelite_batch.xsd')
            if not os.path.exists(schema_path):
                schema_path = os.path.join('examples', 'sample_safelite_batch.xml')
        elif not schema_path and file_type == "json":
            schema_path = os.path.join('schemas', 'iso_claim.xsd') 
            if not os.path.exists(schema_path):
                schema_path = os.path.join('examples', 'sample_iso_claim.xml')
        
        # Run the transformation process asynchronously
        run_async_task(process_file_transformation, file_path, result_id, examples_path, xslt_path, schema_path)
        
        return jsonify({
            "message": "File uploaded successfully, processing transformation",
            "result_id": result_id,
            "file_type": file_type
        }), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400

@app.route('/status/<result_id>')
def check_status(result_id):
    """
    Check the status of a transformation job
    
    Args:
        result_id: ID of the transformation job
        
    Returns:
        JSON response with the status of the job
    """
    if result_id in transformation_results:
        result = transformation_results[result_id]
        response = {
            "status": result.get("status", "unknown"),
            "result_id": result_id,
        }
        
        # Add timestamp if available, or use current time
        if "end_time" in result:
            response["timestamp"] = datetime.fromtimestamp(result["end_time"]).isoformat()
        else:
            response["timestamp"] = datetime.now().isoformat()
            
        # Add duration if available
        if "duration" in result:
            response["duration"] = result["duration"]
            
        # Add error message if there was an error
        if result.get("status") == "error" and "error" in result:
            response["error"] = result["error"]
            
        return jsonify(response)
    else:
        return jsonify({"status": "not_found", "result_id": result_id}), 404

@app.route('/result/<result_id>')
def get_result(result_id):
    """Get the result of a transformation"""
    if result_id not in transformation_results:
        return jsonify({"error": "Result ID not found"}), 404
    
    result = transformation_results[result_id]
    
    if result["status"] != "completed":
        return jsonify({"error": "Transformation not completed yet"}), 400
    
    return jsonify({
        "original_content": result["original_content"],
        "transformed_content": result["transformed_content"],
        "processing_time": result["processing_time"],
        "validation_result": result["validation_result"],
        "trace_id": result.get("trace_id")
    })

@app.route('/metrics')
def get_metrics():
    """Get transformation metrics"""
    metrics = performance_tracker.get_metrics()
    recent_transformations = []
    
    for result_id, result in list(reversed(list(transformation_results.items())))[:10]:
        if result['status'] == 'completed':
            recent_transformations.append({
                'filename': result['filename'],
                'processing_time': result['processing_time'] if 'processing_time' in result else 0
            })
    
    metrics['recent_transformations'] = recent_transformations
    return jsonify(metrics)

@app.route('/documentation')
def documentation():
    """
    Documentation page
    """
    return render_template('documentation.html')

@app.route('/schemas')
def schemas():
    """Schemas management page"""
    return render_template('schemas.html')

@app.route('/schemas/view/<schema_id>')
def view_schema(schema_id):
    """
    Return the content of a schema for viewing in the UI
    """
    schema_content = ""
    schema_title = ""
    
    if schema_id == 'iso_claim':
        try:
            with open('examples/iso_claim.xsd', 'r') as f:
                schema_content = f.read()
            schema_title = "ISO Standard Claim Schema"
        except:
            schema_content = "Schema file not found"
            
    elif schema_id == 'safelite_batch':
        try:
            with open('examples/sample_safelite_batch.xml', 'r') as f:
                schema_content = f.read()
            schema_title = "Safelite Claims Batch Schema"
        except:
            schema_content = "Schema file not found"
            
    elif schema_id == 'legacy_claim':
        try:
            with open('examples/sample_iso_claim.xml', 'r') as f:
                schema_content = f.read()
            schema_title = "Legacy XML Claim Schema"
        except:
            schema_content = "Schema file not found"
    
    return jsonify({
        'title': schema_title,
        'content': schema_content
    })

@app.route('/schemas/download/<schema_id>')
def download_schema(schema_id):
    """
    Allow downloading a schema file
    """
    if schema_id == 'iso_claim':
        try:
            return send_file('examples/iso_claim.xsd', as_attachment=True)
        except:
            return "Schema file not found", 404
            
    elif schema_id == 'safelite_batch':
        try:
            return send_file('examples/sample_safelite_batch.xml', as_attachment=True)
        except:
            return "Schema file not found", 404
            
    elif schema_id == 'legacy_claim':
        try:
            return send_file('examples/sample_iso_claim.xml', as_attachment=True)
        except:
            return "Schema file not found", 404
    
    return "Invalid schema ID", 400

@app.route('/schemas/upload', methods=['POST'])
def upload_schema_file():
    """
    Handle schema file uploads.
    Validates that the file is present and is a valid XML/XSD file.
    Returns a JSON response with the schema ID.
    """
    logger.info("Processing schema upload request")
    
    # Check if a file was included in the request
    if 'schema_file' not in request.files:
        logger.warning("No schema file in request")
        return jsonify({'error': 'No schema file included in the request'}), 400
    
    file = request.files['schema_file']
    
    # Check if a filename was selected
    if file.filename == '':
        logger.warning("Empty filename submitted")
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if it's a valid file type
    if not allowed_file(file.filename, allowed_extensions={'xml', 'xsd'}):
        logger.warning(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'File type not allowed. Only XML and XSD files are permitted.'}), 400
    
    # Generate a unique identifier for this schema
    schema_id = str(uuid.uuid4())
    
    # Create a secure filename based on original name
    filename = secure_filename(file.filename)
    schema_filename = f"{schema_id}_{filename}"
    schema_path = os.path.join(app.config['SCHEMAS_FOLDER'], schema_filename)
    
    # Save the file
    file.save(schema_path)
    logger.info(f"Schema saved as {schema_path}")
    
    # Return the schema ID and filename
    return jsonify({
        'schema_id': schema_id,
        'filename': filename,
        'path': schema_path
    }), 200

if __name__ == '__main__':
    # Verify OpenAI API Key
    if 'OPENAI_API_KEY' not in os.environ or not os.environ['OPENAI_API_KEY'] or os.environ['OPENAI_API_KEY'] == 'your_openai_api_key_here':
        print("WARNING: OPENAI_API_KEY environment variable not set or using default value.")
        print("Please set your OpenAI API key in the .env file or environment variables.")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 
