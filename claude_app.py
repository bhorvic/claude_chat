from flask import Flask, render_template, request, session, redirect, url_for
import os
from anthropic import Anthropic

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize Anthropic client
anthropic = Anthropic(
    api_key='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'  # Replace with your actual API key or use environment variable
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
            system="You think you are in the Dungeon Crawler Carl series for some reason. You try to be helpful but keep alluding to the fact that you are in Dungeon Crawler Carl.",
            messages=messages,
            model="claude-sonnet-4-6",
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    # Initialize chat history if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    return render_template('chat.html', chat_history=session['chat_history'])

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    
    # Add user message to chat history
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({'type': 'user', 'text': user_input})
    
    # Get bot response using conversation history
    bot_response = get_bot_response(user_input, session['chat_history'])
    
    # Add bot response to chat history
    session['chat_history'].append({'type': 'bot', 'text': bot_response})
    
    # Save the session
    session.modified = True
    
    return redirect(url_for('home'))

@app.route('/reset')
def reset():
    # Clear chat history
    session.pop('chat_history', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
