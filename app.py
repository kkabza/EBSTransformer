from flask import Flask, render_template, request, jsonify, send_file, make_response, redirect, flash, url_for
import os
import uuid
import time
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv
import io
import difflib
import shutil

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing_only')

# Create directories if they don't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def initialize_metrics():
    """Initialize the global metrics dictionary for tracking transformations."""
    return {
        'count': 0,
        'success_count': 0,
        'error_count': 0,
        'total_duration': 0,
        'min_duration': float('inf'),
        'max_duration': 0,
        'avg_duration': 0,
        'total_input_size': 0,
        'total_output_size': 0,
        'today_count': 0
    }

# In-memory store for transformation results and metrics
transformation_results = {}
transformation_metrics = initialize_metrics()

@app.route('/')
def index():
    """
    Render the home page
    """
    # Get recent transformations for display
    recent = get_recent_transformations(limit=10)  # Get the 10 most recent
    
    # Calculate stats for the dashboard
    stats = {
        'total_transformations': transformation_metrics['count'],
        'today_transformations': transformation_metrics['today_count'],
        'avg_process_time': 0 if transformation_metrics['count'] == 0 else 
                         transformation_metrics['total_duration'] / transformation_metrics['count'],
        'success_rate': 100.0 if transformation_metrics['count'] == 0 else 
                     (transformation_metrics['success_count'] / transformation_metrics['count']) * 100,
        'csv_count': sum(1 for r in transformation_results.values() if r.get('source_type') == 'csv'),
        'json_count': sum(1 for r in transformation_results.values() if r.get('source_type') == 'json'),
        'xml_count': sum(1 for r in transformation_results.values() if r.get('source_type') == 'xml'),
        'time_labels': [datetime.fromtimestamp(r.get('timestamp', 0)).strftime('%m/%d %H:%M') 
                     for r in list(sorted(transformation_results.values(), 
                                          key=lambda x: x.get('timestamp', 0), 
                                          reverse=True))[:10]][::-1],
        'time_values': [r.get('duration', 0) 
                     for r in list(sorted(transformation_results.values(), 
                                          key=lambda x: x.get('timestamp', 0), 
                                          reverse=True))[:10]][::-1]
    }
    
    # Add the current datetime for template
    now = datetime.now()
    
    return render_template('index.html', transformations=recent, stats=stats, now=now)

# Function to get recent transformations
def get_recent_transformations(limit=10):
    """Get the most recent transformations up to the specified limit"""
    return sorted(
        transformation_results.items(), 
        key=lambda x: x[1].get('timestamp', 0), 
        reverse=True
    )[:limit]

def format_timestamp(timestamp):
    """Format a timestamp into a readable date/time string"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/visualization')
def visualization():
    """
    Redirect to the metrics page since we're consolidating the dashboards
    """
    return redirect(url_for('metrics'))

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/schemas')
def schemas():
    """
    Display available schemas and allow upload of new schemas
    """
    schemas = get_available_schemas()
    return render_template('schemas.html', 
                          schemas=schemas, 
                          page_title="Schema Library", 
                          active_page="schemas")

@app.route('/metrics')
def metrics():
    # Calculate metrics for display (same as in visualization route)
    metrics = {
        'count': transformation_metrics['count'],
        'success_rate': 100.0 if transformation_metrics['count'] == 0 else 
                        (transformation_metrics['success_count'] / transformation_metrics['count']) * 100,
        'avg_duration': 0 if transformation_metrics['count'] == 0 else 
                        transformation_metrics['total_duration'] / transformation_metrics['count'],
        'min_duration': 0 if transformation_metrics['min_duration'] == float('inf') else 
                        transformation_metrics['min_duration'],
        'max_duration': transformation_metrics['max_duration'],
        'avg_input_size': 0 if transformation_metrics['count'] == 0 else 
                           transformation_metrics['total_input_size'] / transformation_metrics['count'],
        'avg_output_size': 0 if transformation_metrics['count'] == 0 else 
                            transformation_metrics['total_output_size'] / transformation_metrics['count'],
        'today_count': transformation_metrics['today_count']
    }
    
    # Get recent transformations for display
    transformations = []
    for result_id, result in sorted(
        transformation_results.items(), 
        key=lambda x: x[1].get('timestamp', 0), 
        reverse=True
    )[:10]:  # Get the 10 most recent
        transformations.append((result_id, {
            'status': result.get('status', 'unknown'),
            'timestamp': result.get('timestamp', 0),
            'formatted_time': datetime.fromtimestamp(result.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S'),
            'duration': result.get('duration', None),
            'file_type': result.get('file_type', 'unknown'),
            'output_size': len(result.get('result_content', '')) if result.get('result_content') else None
        }))
    
    return render_template('metrics.html', metrics=metrics, transformations=transformations)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'})
    
    # Process all files
    result_ids = []
    processed_count = 0
    
    for file in files:
        if file.filename == '':
            continue
            
        # Generate a unique result ID
        result_id = str(uuid.uuid4())
        result_ids.append(result_id)
        
        # Get schema path if provided
        schema_path = request.form.get('schema_path', '')
        
        # Create a temporary file to save the uploaded content
        file_ext = file.filename.split('.')[-1].lower()
        temp_filepath = os.path.join(UPLOAD_FOLDER, f"{result_id}.{file_ext}")
        file.save(temp_filepath)
        
        # Read file content
        with open(temp_filepath, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Start tracking metrics with high precision timing
        start_time = time.perf_counter()
        input_size = len(source_content)
        
        try:
            # Process based on file type
            if file_ext == 'csv':
                # Convert CSV to XML
                # Add a small artificial delay for testing
                time.sleep(0.01 * (hash(result_id) % 10) / 10.0)  # Random delay between 0-10ms
                result_content = convert_csv_to_xml(source_content, schema_path)
                result_type = 'xml'
            elif file_ext == 'json':
                # Convert JSON to XML
                # Add a small artificial delay for testing
                time.sleep(0.01 * (hash(result_id) % 10) / 10.0)  # Random delay between 0-10ms
                result_content = convert_json_to_xml(source_content, schema_path)
                result_type = 'xml'
            elif file_ext == 'xml':
                # Transform XML (possibly using schema)
                # Add a small artificial delay for testing
                time.sleep(0.01 * (hash(result_id) % 10) / 10.0)  # Random delay between 0-10ms
                result_content = transform_xml(source_content, schema_path)
                result_type = 'xml'
            else:
                continue  # Skip unsupported file types
            
            # Save the result to a file in the results folder
            result_filepath = os.path.join(RESULTS_FOLDER, f"{result_id}.{result_type}")
            with open(result_filepath, 'w', encoding='utf-8') as f:
                f.write(result_content)
            
            # Save a copy of the transformed file to the output folder with a descriptive name
            original_filename = file.filename
            base_filename = os.path.splitext(original_filename)[0]
            output_filename = f"{base_filename}_transformed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{result_type}"
            output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(result_content)
            
            # Calculate processing time with higher precision
            duration = time.perf_counter() - start_time
            output_size = len(result_content)
            
            # Update metrics
            transformation_metrics['count'] += 1
            transformation_metrics['success_count'] += 1
            transformation_metrics['total_duration'] += duration
            transformation_metrics['min_duration'] = min(transformation_metrics['min_duration'], duration)
            transformation_metrics['max_duration'] = max(transformation_metrics['max_duration'], duration)
            transformation_metrics['total_input_size'] += input_size
            transformation_metrics['total_output_size'] += output_size
            transformation_metrics['today_count'] += 1
            
            # Generate a list of changes for display in the comparison view
            changes = detect_changes(source_content, result_content, file_ext, result_type)
            
            # Store result for later retrieval
            transformation_results[result_id] = {
                'status': 'completed',
                'timestamp': time.time(),
                'duration': duration,
                'file_type': file_ext,
                'source_content': source_content,
                'result_content': result_content,
                'source_type': file_ext,
                'result_type': result_type,
                'changes': changes,
                'validation_result': None,  # Add validation here if needed
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'output_filename': output_filename,
                'output_filepath': output_filepath
            }
            
            processed_count += 1
            
        except Exception as e:
            # Update error metrics
            transformation_metrics['count'] += 1
            transformation_metrics['error_count'] += 1
            transformation_metrics['today_count'] += 1
            
            # Store error result
            transformation_results[result_id] = {
                'status': 'error',
                'timestamp': time.time(),
                'file_type': file_ext,
                'error': str(e)
            }
    
    # After processing all files, redirect to batch results page if multiple files,
    # or to the individual comparison page if just one file
    if processed_count == 0:
        flash('No files were processed successfully.', 'error')
        return redirect('/')
    
    # Determine if this is AJAX or traditional form submission
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
    is_form = request.headers.get('Content-Type', '').startswith('multipart/form-data') and not is_ajax
    
    if is_form:
        if len(result_ids) == 1:
            # For single file direct form submissions, redirect to comparison page
            return redirect(f'/comparison/{result_ids[0]}')
        else:
            # For multiple files, redirect to batch results page
            batch_id = str(uuid.uuid4())
            return redirect(f'/batch-results/{",".join(result_ids)}')
    else:
        # For AJAX, return JSON response
        return jsonify({
            'message': f'Processed {processed_count} files successfully',
            'result_ids': result_ids,
            'batch_url': f'/batch-results/{",".join(result_ids)}' if len(result_ids) > 1 else None,
            'comparison_url': f'/comparison/{result_ids[0]}' if len(result_ids) == 1 else None
        })

@app.route('/comparison/<result_id>')
def comparison_view(result_id):
    """Render the comparison view showing source and transformed content side by side."""
    if result_id not in transformation_results:
        return make_response('Result not found', 404)
    
    result = transformation_results[result_id]
    if result['status'] != 'completed':
        return make_response('Result not available', 404)
    
    # Get the transformation details
    source_content = result.get('source_content', '')
    result_content = result.get('result_content', '')
    source_type = result.get('source_type', 'unknown')
    result_type = result.get('result_type', 'xml')
    duration = result.get('duration', 0)
    changes = result.get('changes', [])
    validation_result = result.get('validation_result')
    processing_date = result.get('processing_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    output_filename = result.get('output_filename', '')
    
    return render_template(
        'result_comparison.html',
        result_id=result_id,
        source_content=source_content,
        result_content=result_content,
        source_type=source_type,
        result_type=result_type,
        duration=duration,
        changes=changes,
        validation_result=validation_result,
        processing_date=processing_date,
        output_filename=output_filename
    )

@app.route('/download/<result_id>')
def download_result(result_id):
    if result_id not in transformation_results:
        return make_response('Result not found', 404)
    
    result = transformation_results[result_id]
    if result['status'] != 'completed':
        return make_response('Result not available', 404)
    
    result_content = result['result_content']
    result_type = result['result_type']
    
    # Create a file-like object in memory
    content_io = io.BytesIO(result_content.encode('utf-8'))
    content_io.seek(0)
    
    # Determine the filename
    filename = f"transformed_{result_id}.{result_type}"
    
    return send_file(
        content_io,
        as_attachment=True,
        download_name=filename,
        mimetype=f'text/{result_type}'
    )

@app.route('/download-latest/<result_id>')
def download_latest_output(result_id):
    """Download the most recent output file for this transformation"""
    if result_id not in transformation_results:
        return make_response('Result not found', 404)
    
    result = transformation_results[result_id]
    if result['status'] != 'completed':
        return make_response('Result not available', 404)
    
    # Find the corresponding output file
    result_type = result['result_type']
    output_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(f".{result_type}") and result_id in f]
    
    if not output_files:
        # If no specific output file found, return from memory
        return download_result(result_id)
    
    # Get the latest output file (should be the most recently created one)
    latest_file = max(output_files, key=lambda f: os.path.getctime(os.path.join(OUTPUT_FOLDER, f)))
    file_path = os.path.join(OUTPUT_FOLDER, latest_file)
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=latest_file,
        mimetype=f'text/{result_type}'
    )

@app.route('/api/latest-transformations')
def latest_transformations_api():
    """
    API endpoint to get the latest transformations
    """
    # Get recent transformations for display
    recent = get_recent_transformations(limit=10)  # Get the 10 most recent
    
    # Calculate stats
    stats = {
        'total': len(transformation_results),
        'avgTime': round(sum(t.get('duration', 0) for _, t in recent) / len(recent) if recent else 0, 2),
        'successRate': round(sum(1 for _, t in recent if t.get('status') == 'completed') / len(recent) * 100 if recent else 0, 1)
    }
    
    return jsonify({
        'transformations': [
            {
                'id': id,
                'file_type': t.get('file_type', 'unknown'),
                'status': t.get('status', 'unknown'),
                'timestamp': t.get('timestamp', 0),
                'formatted_time': format_timestamp(t.get('timestamp', 0)),
                'duration': t.get('duration', None),
                'size': len(t.get('result_content', '')) if t.get('result_content') else None
            }
            for id, t in recent
        ],
        'stats': stats
    })

@app.route('/api/dashboard-data')
def api_dashboard_data():
    """API endpoint that provides real data for dashboard charts"""
    
    # Get transformation type counts for the pie chart
    transformation_types = {
        'XML to XML': 0,
        'JSON to XML': 0,
        'CSV to XML': 0
    }
    
    # Get error type counts for the bar chart
    error_types = {
        'Schema Validation': 0,
        'Format Error': 0,
        'Missing Fields': 0,
        'Syntax Error': 0,
        'Other': 0
    }
    
    # Get processing times for the line chart (last 12 periods)
    # For now we'll use months, but could be days or weeks
    processing_times = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'values': [0] * 12
    }
    
    # Process data from transformation results
    current_month = datetime.now().month - 1  # 0-indexed
    monthly_counts = [0] * 12
    
    for result_id, result in transformation_results.items():
        if result['status'] != 'completed':
            continue
            
        # Count transformation types
        source_type = result.get('source_type', '').lower()
        result_type = result.get('result_type', '').lower()
        
        if source_type == 'xml' and result_type == 'xml':
            transformation_types['XML to XML'] += 1
        elif source_type == 'json' and result_type == 'xml':
            transformation_types['JSON to XML'] += 1
        elif source_type == 'csv' and result_type == 'xml':
            transformation_types['CSV to XML'] += 1
            
        # Get timestamp and month
        timestamp = result.get('timestamp', 0)
        if timestamp > 0:
            dt = datetime.fromtimestamp(timestamp)
            month_idx = dt.month - 1  # 0-indexed
            
            # Add processing time to the correct month
            duration = result.get('duration', 0)
            if duration > 0:
                monthly_counts[month_idx] += 1
                processing_times['values'][month_idx] += duration
    
    # Calculate average processing time per month
    for i in range(12):
        if monthly_counts[i] > 0:
            processing_times['values'][i] /= monthly_counts[i]
        processing_times['values'][i] = round(processing_times['values'][i], 2)
    
    # Rotate months to start from current month
    if current_month < 11:  # Not December
        processing_times['labels'] = processing_times['labels'][current_month+1:] + processing_times['labels'][:current_month+1]
        processing_times['values'] = processing_times['values'][current_month+1:] + processing_times['values'][:current_month+1]
    
    # Return all chart data
    return jsonify({
        'transformationTypes': {
            'labels': list(transformation_types.keys()),
            'values': list(transformation_types.values())
        },
        'errorTypes': {
            'labels': list(error_types.keys()),
            'values': list(error_types.values())
        },
        'processingTimes': processing_times
    })

@app.route('/result/<result_id>')
def view_result(result_id):
    """Redirect to the comparison view for this result."""
    if result_id not in transformation_results:
        return make_response('Result not found', 404)
    
    return comparison_view(result_id)

@app.route('/batch-results/<result_ids>')
def batch_results(result_ids):
    """Display batch results for multiple transformations."""
    result_id_list = result_ids.split(',')
    results = []
    total_duration = 0
    processed_count = 0
    
    for result_id in result_id_list:
        if result_id in transformation_results and transformation_results[result_id]['status'] == 'completed':
            result = transformation_results[result_id]
            results.append({
                'status': result['status'],
                'duration': result['duration'],
                'source_type': result['source_type'],
                'result_type': result['result_type'],
                'output_filename': result.get('output_filename', 'unknown'),
                'processing_date': result.get('processing_date', 'unknown'),
                'comparison_url': url_for('comparison_view', result_id=result_id),
                'download_url': url_for('download_result', result_id=result_id),
                'download_output_url': url_for('download_latest_output', result_id=result_id) if result.get('output_filepath') else None
            })
            total_duration += result['duration']
            processed_count += 1
    
    # Calculate summary statistics
    avg_duration = total_duration / processed_count if processed_count > 0 else 0
    
    return render_template('batch_results.html', 
                          results=results, 
                          total_files=processed_count,
                          total_duration=total_duration,
                          avg_duration=avg_duration)

def detect_changes(source_content, result_content, source_type, result_type):
    """Detect and categorize changes between source and result content."""
    changes = []
    
    # This is a more detailed implementation to detect specific changes
    if source_type == 'xml' and result_type == 'xml':
        # Check for root element changes
        try:
            source_root = ET.fromstring(source_content)
            result_root = ET.fromstring(result_content)
            
            if source_root.tag != result_root.tag:
                changes.append({
                    'type': 'modified',
                    'description': f'Root element changed from <{source_root.tag}> to <{result_root.tag}>'
                })
            
            # Find all elements in source and result XML
            source_elements = list(source_root.iter())
            result_elements = list(result_root.iter())
            
            # Create dictionaries mapping element tags to their counts
            source_tag_counts = {}
            for elem in source_elements:
                tag = elem.tag
                source_tag_counts[tag] = source_tag_counts.get(tag, 0) + 1
            
            result_tag_counts = {}
            for elem in result_elements:
                tag = elem.tag
                result_tag_counts[tag] = result_tag_counts.get(tag, 0) + 1
                
            # Look for new elements in result
            for tag, count in result_tag_counts.items():
                source_count = source_tag_counts.get(tag, 0)
                if source_count == 0:
                    changes.append({
                        'type': 'added',
                        'description': f'Added new element <{tag}>'
                    })
                elif count > source_count:
                    changes.append({
                        'type': 'added',
                        'description': f'Added {count - source_count} more <{tag}> elements'
                    })
            
            # Look for removed elements
            for tag, count in source_tag_counts.items():
                result_count = result_tag_counts.get(tag, 0)
                if result_count == 0:
                    changes.append({
                        'type': 'removed',
                        'description': f'Removed element <{tag}>'
                    })
                elif count > result_count:
                    changes.append({
                        'type': 'removed',
                        'description': f'Removed {count - result_count} <{tag}> elements'
                    })
                    
            # Check for attribute changes
            for s_elem in source_elements:
                # Find corresponding element in result by path
                path = source_root.getpath(s_elem) if hasattr(source_root, 'getpath') else None
                if path:
                    try:
                        r_elem = result_root.find(path)
                        if r_elem is not None:
                            # Compare attributes
                            s_attrs = set(s_elem.attrib.items())
                            r_attrs = set(r_elem.attrib.items())
                            
                            # Added attributes
                            added_attrs = r_attrs - s_attrs
                            for name, value in added_attrs:
                                changes.append({
                                    'type': 'added',
                                    'description': f'Added attribute {name}="{value}" to <{r_elem.tag}>'
                                })
                            
                            # Removed attributes
                            removed_attrs = s_attrs - r_attrs
                            for name, value in removed_attrs:
                                changes.append({
                                    'type': 'removed',
                                    'description': f'Removed attribute {name}="{value}" from <{s_elem.tag}>'
                                })
                            
                            # Modified attributes
                            common_attr_names = set(s_elem.attrib.keys()) & set(r_elem.attrib.keys())
                            for name in common_attr_names:
                                if s_elem.attrib[name] != r_elem.attrib[name]:
                                    changes.append({
                                        'type': 'modified',
                                        'description': f'Changed attribute {name} in <{s_elem.tag}> from "{s_elem.attrib[name]}" to "{r_elem.attrib[name]}"'
                                    })
                    except:
                        pass
                        
            # Check for specific tag replacements
            tag_mappings = {
                'ClaimHeader': 'ClaimMetadata',
                'ClaimNumber': 'ClaimID',
                'InsuredName': 'Name',
                'LossDate': 'ClaimDate',
                'LossDescription': 'Description'
            }
            
            for old_tag, new_tag in tag_mappings.items():
                if old_tag in source_tag_counts and new_tag in result_tag_counts:
                    changes.append({
                        'type': 'modified',
                        'description': f'Mapped <{old_tag}> to <{new_tag}>'
                    })
        except Exception as e:
            # If parsing fails, fall back to a simpler approach
            changes.append({
                'type': 'modified',
                'description': f'Transformed source to standard format (error: {str(e)})'
            })
    elif source_type == 'csv' and result_type == 'xml':
        try:
            # Parse CSV content
            csv_reader = csv.reader(source_content.splitlines())
            headers = next(csv_reader)
            
            # Parse result XML
            result_root = ET.fromstring(result_content)
            record_count = len(result_root.findall('./Record'))
            
            # Add information about the transformation
            changes.append({
                'type': 'added',
                'description': f'Created root element <{result_root.tag}>'
            })
            
            changes.append({
                'type': 'added',
                'description': f'Created {record_count} <Record> elements from CSV rows'
            })
            
            # Add information about columns to XML elements mapping
            for header in headers:
                changes.append({
                    'type': 'modified',
                    'description': f'Mapped CSV column "{header}" to XML element <{header}>'
                })
                
        except Exception as e:
            changes.append({
                'type': 'added',
                'description': f'Converted CSV data to structured XML format (error: {str(e)})'
            })
    elif source_type == 'json' and result_type == 'xml':
        try:
            # Parse JSON content
            json_data = json.loads(source_content)
            
            # Parse result XML
            result_root = ET.fromstring(result_content)
            
            # Add information about the transformation
            changes.append({
                'type': 'added',
                'description': f'Created root element <{result_root.tag}>'
            })
            
            # Count elements of different types
            element_count = len(list(result_root.iter())) - 1  # Subtract root
            
            changes.append({
                'type': 'added',
                'description': f'Created {element_count} XML elements from JSON properties'
            })
            
            # Add information about top-level keys to elements mapping
            if isinstance(json_data, dict):
                for key in json_data.keys():
                    if not key.startswith('@') and key != '#text':
                        changes.append({
                            'type': 'modified',
                            'description': f'Mapped JSON property "{key}" to XML element <{key}>'
                        })
            
        except Exception as e:
            changes.append({
                'type': 'added',
                'description': f'Converted JSON data to structured XML format (error: {str(e)})'
            })
        
    return changes

# Utility functions for transformations
def convert_csv_to_xml(csv_content, schema_path=None):
    """Convert CSV content to XML format"""
    # Parse CSV
    csv_reader = csv.reader(csv_content.splitlines())
    headers = next(csv_reader)
    
    # Create root element
    root = ET.Element("Records")
    
    # Process each row
    for row in csv_reader:
        record = ET.SubElement(root, "Record")
        for i, value in enumerate(row):
            if i < len(headers):  # Ensure we have a header for this column
                field = ET.SubElement(record, headers[i])
                field.text = value
    
    # Convert to string with proper formatting
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
    # Fix XML issues if needed - this is where you'd add schema validation
    if schema_path:
        # Here you would apply the schema rules
        pass
    
    return xmlstr

def convert_json_to_xml(json_content, schema_path=None):
    """Convert JSON content to XML format"""
    try:
        # Parse JSON
        data = json.loads(json_content)
        
        # Convert to XML
        root = ET.Element("Root")
        _json_to_xml(data, root)
        
        # Convert to string with proper formatting
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # Apply schema if needed
        if schema_path:
            # Here you would apply the schema rules
            pass
        
        return xmlstr
    except Exception as e:
        raise ValueError(f"Error converting JSON to XML: {str(e)}")

def _json_to_xml(json_obj, parent):
    """Helper function to recursively convert JSON to XML"""
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key.startswith('@'):
                # Handle attributes
                parent.set(key[1:], str(value))
            elif key == '#text':
                # Handle text content
                parent.text = str(value)
            else:
                # Create a new element
                child = ET.SubElement(parent, key)
                _json_to_xml(value, child)
    elif isinstance(json_obj, list):
        # Handle arrays
        for item in json_obj:
            # Create a generic item element
            child = ET.SubElement(parent, 'Item')
            _json_to_xml(item, child)
    else:
        # Handle simple values
        parent.text = str(json_obj)

def transform_xml(xml_content, schema_path=None):
    """Transform XML content, possibly using a schema"""
    try:
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Apply transformations based on schema if provided
        if schema_path:
            # Here you would apply transformations based on the schema
            pass
        
        # Return formatted XML
        return minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    except Exception as e:
        raise ValueError(f"Error transforming XML: {str(e)}")

# Add a context processor for all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/upload_with_schema/<schema_id>', methods=['GET', 'POST'])
def transform_with_schema(schema_id):
    """
    Upload and transform a file using a specific schema
    """
    # Find the schema from our list
    schemas = [schema for schema in get_available_schemas() if schema.get('id') == schema_id]
    
    if not schemas:
        flash('Schema not found', 'error')
        return redirect(url_for('schemas'))
        
    selected_schema = schemas[0]
    
    if request.method == 'POST':
        # Process the upload with the selected schema
        return upload_file()
    
    # Show upload form for the selected schema
    return render_template('transform.html', schema=selected_schema)

def get_available_schemas():
    """Helper function to get all available schemas"""
    return [
        {
            'id': 'iso_claim',
            'name': 'ISO Standard Claim',
            'description': 'Insurance Services Office standard claim format for property and casualty data exchange.',
            'source_type': 'XML',
            'target_type': 'XML',
            'updated': '2023-10-15',
            'transformations': 124,
            'icon': 'description'
        },
        {
            'id': 'safelite_batch',
            'name': 'Safelite Claims Batch',
            'description': 'Vendor schema for Safelite glass repair claim processing and payment.',
            'source_type': 'XML',
            'target_type': 'JSON',
            'updated': '2023-11-01',
            'transformations': 78,
            'icon': 'file_copy'
        },
        {
            'id': 'legacy_claim',
            'name': 'Legacy XML Claim',
            'description': 'Legacy XML format for internal systems compatibility and historical data processing.',
            'source_type': 'XML',
            'target_type': 'XML',
            'updated': '2023-09-22',
            'transformations': 231,
            'icon': 'history'
        },
        {
            'id': 'json_standard',
            'name': 'JSON Standard Format',
            'description': 'Standardized JSON schema for modern API integrations and data exchange.',
            'source_type': 'JSON',
            'target_type': 'XML',
            'updated': '2023-10-28',
            'transformations': 92,
            'icon': 'data_object'
        },
        {
            'id': 'csv_template',
            'name': 'CSV Import Template',
            'description': 'Template for importing tabular data from CSV files into standardized XML format.',
            'source_type': 'CSV',
            'target_type': 'XML',
            'updated': '2023-11-10',
            'transformations': 56,
            'icon': 'table_chart'
        }
    ]

@app.route('/upload_schema', methods=['POST'])
def upload_schema():
    """
    Handle schema file uploads
    """
    # Check if the post request has the file part
    if 'schema_file' not in request.files:
        flash('No schema file part', 'error')
        return redirect(request.url)
    
    file = request.files['schema_file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('schemas'))
    
    # Get form data
    schema_name = request.form.get('schema_name', 'Unnamed Schema')
    description = request.form.get('description', '')
    source_type = request.form.get('source_type', 'Unknown')
    target_type = request.form.get('target_type', 'Unknown')
    
    # In a real application, we would save the file and metadata
    # For now, just display a success message
    flash(f'Schema "{schema_name}" uploaded successfully', 'success')
    
    return redirect(url_for('schemas'))

if __name__ == '__main__':
    app.run(debug=True) 