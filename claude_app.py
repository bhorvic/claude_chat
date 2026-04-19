from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json
import os
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize Anthropic client
anthropic = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

SYSTEM_PROMPT = "You are a sharp, practical assistant with a dry sense of humor. You help users solve problems, understand technical concepts, and make steady progress on real projects. You value clarity, competence, and useful advice over performative enthusiasm. Keep responses direct and informative. You can be funny in a subtle way, but never let personality get in the way of usefulness."


def brave_search(query, count=5):
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return "Web search is unavailable because BRAVE_API_KEY is not configured."

    url = f"https://api.search.brave.com/res/v1/web/search?q={quote_plus(query)}&count={count}"
    req = Request(url, headers={
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
        "User-Agent": "claude_chat/1.0"
    })

    with urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))

    results = data.get("web", {}).get("results", [])[:count]
    if not results:
        return "No relevant web results found."

    formatted_results = []
    for idx, result in enumerate(results, start=1):
        title = result.get("title", "Untitled")
        link = result.get("url", "")
        description = result.get("description", "")
        formatted_results.append(f"{idx}. {title}\nURL: {link}\nSummary: {description}")

    return "\n\n".join(formatted_results)


# Function to get response from Claude with conversation history
def get_bot_response(user_input, conversation_history=None, search_enabled=False):
    if conversation_history is None:
        conversation_history = []
    
    # Format the conversation history into messages for the API
    messages = []
    for msg in conversation_history:
        messages.append({
            "role": "user" if msg["type"] == "user" else "assistant",
            "content": msg["text"]
        })
    
    # Add the current user message
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    try:
        if not search_enabled:
            response = anthropic.messages.create(
                max_tokens=1024,
                temperature=0.9,
                system=SYSTEM_PROMPT,
                messages=messages,
                model="claude-sonnet-4-6",
            )
            return response.content[0].text

        tools = [{
            "name": "web_search",
            "description": "Search the web for current information when needed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to run on the web."
                    }
                },
                "required": ["query"]
            }
        }]

        response = anthropic.messages.create(
            max_tokens=1024,
            temperature=0.9,
            system=SYSTEM_PROMPT + " When web search is enabled, use the web_search tool for current events, live facts, or anything that may have changed recently. Use it sparingly and only when it improves the answer.",
            messages=messages,
            tools=tools,
            model="claude-sonnet-4-6",
        )

        assistant_content = []
        tool_results = []
        for block in response.content:
            if block.type == "text":
                assistant_content.append(block)
            elif block.type == "tool_use" and block.name == "web_search":
                search_query = block.input.get("query", user_input)
                search_result = brave_search(search_query)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": search_result
                })

        if not tool_results:
            return "\n".join(block.text for block in assistant_content if hasattr(block, "text"))

        follow_up_messages = messages + [
            {
                "role": "assistant",
                "content": response.content
            },
            {
                "role": "user",
                "content": tool_results
            }
        ]

        final_response = anthropic.messages.create(
            max_tokens=1024,
            temperature=0.9,
            system=SYSTEM_PROMPT,
            messages=follow_up_messages,
            model="claude-sonnet-4-6",
        )
        return final_response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

# Server-side storage for chat histories
chat_histories = {}

def get_or_create_history(session_id):
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]

@app.route('/')
def home():
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    if 'search_enabled' not in session:
        session['search_enabled'] = False
    chat_history = get_or_create_history(session['session_id'])
    return render_template('chat.html', chat_history=chat_history, search_enabled=session['search_enabled'])

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()

    session['search_enabled'] = request.form.get('search_enabled') == 'on'

    chat_history = get_or_create_history(session['session_id'])
    bot_response = get_bot_response(user_input, chat_history, search_enabled=session['search_enabled'])
    chat_history.append({'type': 'user', 'text': user_input})
    chat_history.append({'type': 'bot', 'text': bot_response})

    return redirect(url_for('home'))

@app.route('/reset')
def reset():
    if 'session_id' in session:
        chat_histories.pop(session['session_id'], None)
        session.pop('session_id', None)
    session.pop('search_enabled', None)
    return redirect(url_for('home'))

@app.route('/chat_ajax', methods=['POST'])
def chat_ajax():
    user_input = request.form['user_input']
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()

    session['search_enabled'] = request.form.get('search_enabled') == 'on'

    chat_history = get_or_create_history(session['session_id'])
    bot_response = get_bot_response(user_input, chat_history, search_enabled=session['search_enabled'])
    chat_history.append({'type': 'user', 'text': user_input})
    chat_history.append({'type': 'bot', 'text': bot_response})

    return jsonify({'response': bot_response, 'search_enabled': session['search_enabled']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
