# ESB LLM Orchestrator

An AI-powered orchestrator for transforming claim files, replacing traditional BizTalk ESB transformation processes. This application uses the OpenAI Agents SDK to intelligently transform data formats.

## Features

- Drag and drop file upload interface
- AI-powered transformation of claim data 
- XSLT fallback capability
- Example-based learning for better transformations
- Real-time performance monitoring
- Detailed transformation history

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd esb-llm-orchestrator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set the OpenAI API key:
   ```
   export OPENAI_API_KEY=your-api-key-here
   ```
   On Windows:
   ```
   set OPENAI_API_KEY=your-api-key-here
   ```

5. Prepare examples and XSLT (optional):
   - Place example transformations in the `examples` directory (JSON format)
   - Place XSLT files in the `xslt` directory for fallback transformations

## Directory Structure

- `main.py`: Main application entry point
- `templates/`: Frontend HTML templates
- `uploads/`: Directory for uploaded files
- `traces/`: Directory for agent execution traces
- `examples/`: Example transformations for few-shot learning
- `xslt/`: XSLT files for fallback transformations

## Running the Application

Start the server:
```
python main.py
```

The application will be available at http://localhost:5000

## Usage

1. Open the web interface at http://localhost:5000
2. (Optional) Enter the path to example transformations
3. (Optional) Enter the path to an XSLT file for fallback
4. Drag and drop a claim file, or click to browse and select one
5. Click "Transform File" to process the transformation
6. View the transformation results and performance metrics

## How It Works

The application uses the OpenAI Agents SDK to create an intelligent agent specialized in claim data transformation. The agent:

1. Receives the source file content
2. Analyzes the structure
3. References examples if provided
4. Transforms the data to the target format
5. Falls back to XSLT if needed and available

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 