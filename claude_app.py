from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize Anthropic client
anthropic = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Function to get response from Claude with conversation history
def get_bot_response(user_input, conversation_history=None):
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
        response = anthropic.messages.create(
            max_tokens=1024,
            temperature=0.9,
            system="You are a sharp, practical assistant with a dry sense of humor. You help users solve problems, understand technical concepts, and make steady progress on real projects. You value clarity, competence, and useful advice over performative enthusiasm. Keep responses direct and informative. You can be funny in a subtle way, but never let personality get in the way of usefulness.",
            messages=messages,
            model="claude-sonnet-4-6",
        )
        return response.content[0].text
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
    chat_history = get_or_create_history(session['session_id'])
    return render_template('chat.html', chat_history=chat_history)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    
    chat_history = get_or_create_history(session['session_id'])
    bot_response = get_bot_response(user_input, chat_history)
    chat_history.append({'type': 'user', 'text': user_input})
    chat_history.append({'type': 'bot', 'text': bot_response})

    return redirect(url_for('home'))

@app.route('/reset')
def reset():
    if 'session_id' in session:
        chat_histories.pop(session['session_id'], None)
        session.pop('session_id', None)
    return redirect(url_for('home'))

@app.route('/chat_ajax', methods=['POST'])
def chat_ajax():
    user_input = request.form['user_input']
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    
    chat_history = get_or_create_history(session['session_id'])
    bot_response = get_bot_response(user_input, chat_history)
    chat_history.append({'type': 'user', 'text': user_input})
    chat_history.append({'type': 'bot', 'text': bot_response})

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
