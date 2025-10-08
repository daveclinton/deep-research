# 🔎 Local Deep Research Agent

An AI-powered research assistant that combines Bright Data's data collection with local Ollama models for private, comprehensive research.

## Features

- 🤖 **Local AI Processing**: Uses Ollama for private, local model inference
- 🌐 **Bright Data Integration**: Reliable web data collection
- 📚 **Vector Knowledge Base**: ChromaDB for storing and retrieving research
- 🎨 **Streamlit UI**: User-friendly web interface
- 🔍 **Multi-source Research**: Aggregates and summarizes multiple sources
- 💾 **Research History**: Maintains history of all research sessions

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Studio1HQ/deep-research-agent
cd deep-research-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

### 2. Setup Ollama

```bash
# Install Ollama (https://ollama.ai/)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
```

### 3. Configure Enviroment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API key
BRIGHT_DATA_API_KEY=your_actual_api_key_here
```


### 4. Run the Application

```bash
streamlit run app.py
```

### Usage
Configure API: Enter your Bright Data API key in the sidebar

Set Parameters: Choose model and number of sources

Enter Topic: Type your research question

Start Research: Click "Start Research" to begin automated analysis

### Architecture
Bright Data Client: Fetches structured web data

Ollama Processor: Local AI summarization and analysis

Research Knowledge Base: Vector storage with ChromaDB

Streamlit UI: Web interface for interaction

### Requirements
Python 3.8+

Bright Data API account

Ollama installed with desired models

4GB+ RAM for local models

### License
MIT License - see LICENSE file for details

```bash

## Running the Application

### Installation & Setup
```bash
# 1. Create and activate virtual environment
python -m venv research_env
source research_env/bin/activate  # Windows: research_env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Ollama (if not already installed)
# Visit https://ollama.ai/ or use:
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2

# 4. Create .env file with your API key
echo "BRIGHT_DATA_API_KEY=your_actual_key_here" > .env

# 5. Run the application
streamlit run app.py
```

### Usage Example
1. Open http://localhost:8501 in your browser

2. Enter your Bright Data API key in the sidebar

3. Type a research topic like "Latest AI developments in 2024"

4. Click "Start Research" and watch the agent collect and analyze data

5. Browse the AI-generated summaries and insights

This complete implementation provides a fully functional research agent that runs locally while leveraging Bright Data's powerful data collection capabilities. The system is modular, extensible, and ready for production use.