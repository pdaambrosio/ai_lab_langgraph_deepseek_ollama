# LangGraph DeepSeek Ollama Agent

A lightweight, local AI agent built with LangGraph and LangChain, enabling tool-calling and ReAct patterns using DeepSeek-R1 (1.5B) via Ollama.

## Setup Instructions

1. Ensure Ollama is running locally with the model downloaded:
   ```bash
   ollama run deepseek-r1:1.5b
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```