# claude_chat

A Flask-based chatbot powered by the Anthropic Claude API. The bot is tuned to feel sharp, practical, and a little dryly funny — more like a competent technical generalist than a generic assistant.

## Features

- Conversational chat interface with full message history
- Powered by Claude Sonnet via the Anthropic API
- Optional web search mode backed by Brave Search
- Server-side session management (no bloated cookies)
- Clean, minimal web UI
- Easy to customize — swap the personality by editing the system prompt

## Requirements

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com)

## Local Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/bhorvic/claude_chat.git
   cd claude_chat
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** with your Anthropic API key
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ```

   Optional: add a Brave Search API key to enable web search in the UI
   ```
   BRAVE_API_KEY=your-brave-key-here
   ```

5. **Run the app**
   ```bash
   python3 claude_app.py
   ```

   Then open your browser to `http://localhost:5000`.

## Customization

To change the bot's personality or behavior, edit the system prompt and `temperature` in the `get_bot_response()` function in `claude_app.py`. The current prompt aims for a sharp, practical assistant voice with a dry sense of humor, but you can tailor it however you want.

The chat UI also includes an **Enable web search** toggle. When turned on, the app can use Brave Search for current information. This may increase both response time and API cost.

## Production Deployment (Raspberry Pi + Cloudflare Tunnel)

This app is deployed on a Raspberry Pi 5 and made publicly accessible using a Cloudflare Tunnel — no port forwarding or static IP required.

### 1. Set up Cloudflare Tunnel

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

cloudflared tunnel login
cloudflared tunnel create <tunnel-name>
```

Create `/etc/cloudflared/config.yml`:
```yaml
tunnel: <your-tunnel-id>
credentials-file: /etc/cloudflared/<your-tunnel-id>.json

ingress:
  - hostname: yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

Route your domain and enable the service:
```bash
cloudflared tunnel route dns <tunnel-name> yourdomain.com
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### 2. Run Flask as a system service

Create `/etc/systemd/system/claude-chat.service`:
```ini
[Unit]
Description=Claude Chat Flask App
After=network.target

[Service]
User=<your-user>
WorkingDirectory=/path/to/claude_chat
EnvironmentFile=/path/to/claude_chat/.env
ExecStart=/path/to/claude_chat/.venv/bin/python3 claude_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable claude-chat
sudo systemctl start claude-chat
```

## Notes

- Never commit your `.env` file — it's listed in `.gitignore`
- The Flask dev server is fine for personal/low-traffic use; consider `gunicorn` for higher traffic
