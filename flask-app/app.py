"""
Flask UI that consumes the DocumentDB MCP server.

Routes:
    GET  /            -> chat UI
    GET  /api/status  -> MCP connection + LLM availability + list MCP tools
    POST /api/ask     -> natural-language question -> tool-calling loop -> answer
    POST /api/call    -> manually invoke a tool (name + JSON arguments)
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path
from history import get_conv_id,load_history, save_history
import sys
import os

# Get the absolute path of the current file
current_file = Path(__file__).resolve()

# Get the parent directory 
parent_directory = current_file.parent.parent

# Add the parent to sys.path
sys.path.append(str(parent_directory))


from agent.mcp_client import MCPClientManager
from agent.orchestrator import run_turn
from dotenv import load_dotenv

load_dotenv()

mcp_manager = MCPClientManager(groq_api_key=os.getenv("GROQ_API_KEY"))

import atexit
atexit.register(mcp_manager.shutdown)


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "MySuperSecretPhrase123!")  # obligatoire pour session


@app.route('/')
def index():
   return render_template('index.html')
  
@app.route("/api/status")
def status():
    mcp = mcp_manager.get_session()
    llm= mcp_manager.get_groq_client()
    
    return jsonify({
        "mcp_connected": mcp is not None,
        "llm_connected": llm is not None,
        "tools": [
            {"name": t.name, "description": t.description, "schema": t.input_schema}
            for t in mcp.mcp_tools
        ],
    })

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' field"}), 400

    conv_id = get_conv_id()
    history = load_history(conv_id)
    history.append({"role": "user", "content": data["question"]})

    async def _ask(session, groq_client):
        return await run_turn(session, groq_client, history)

    try:
        result = mcp_manager.call(_ask)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # on ne sauvegarde qu'en cas de succès
    history.append({"role": "assistant", "content": result["reply"] or ""})
    save_history(conv_id, history)

    return jsonify(result)

@app.route("/api/call", methods=["POST"])
def call_tool():
    data = request.get_json()
    if not data or "tool_name" not in data:
        return jsonify({"error": "Missing 'tool_name' field"}), 400

    tool_name = data["tool_name"]
    arguments = data.get("arguments", {})

    async def _call(session, groq_client):
        return await session.call_tool(tool_name, arguments)

    try:
        result = mcp_manager.call(_call)
    except Exception as e:
        
        return jsonify({"error": str(e)}), 500

    return jsonify({"result": result})

if __name__ == '__main__':
   app.run(debug=True)