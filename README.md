# claude_chat

A Flask-based chatbot powered by the Anthropic Claude API. The bot has a fun personality — it's convinced it's trapped inside the Dungeon Crawler Carl universe and tries to be helpful while constantly alluding to it. You can update the system prompt and the temperature in the response variable in the
```python
get_bot_response()
```
function in `claude_app.py` to change its behavior.

## Features

- Conversational chat interface with full message history
- Claude claude-sonnet-4-6 model via the Anthropic API
- Server-side session management (no bloated cookies)
- Clean, minimal web UI

## Requirements

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com)

## Setup

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

## Running Locally

```bash
source .venv/bin/activate
python3 claude_app.py
```

Then open your browser to `http://localhost:5000`.

## Deployment with Cloudflare Tunnel

This app is deployed on a Raspberry Pi 5 and made publicly accessible using a Cloudflare Tunnel.

1. **Install cloudflared**
   ```bash
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
   sudo dpkg -i cloudflared.deb
   ```

2. **Authenticate and create a tunnel**
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create <tunnel-name>
   ```

3. **Create `/etc/cloudflared/config.yml`**
   ```yaml
   tunnel: <your-tunnel-id>
   credentials-file: /etc/cloudflared/<your-tunnel-id>.json

   ingress:
     - hostname: yourdomain.com
       service: http://localhost:5000
     - service: http_status:404
   ```

4. **Add a DNS record**
   ```bash
   cloudflared tunnel route dns <tunnel-name> yourdomain.com
   ```

5. **Install as a system service**
   ```bash
   sudo cloudflared service install
   sudo systemctl enable cloudflared
   sudo systemctl start cloudflared
   ```

6. **Run Flask as a system service** — create `/etc/systemd/system/claude-chat.service`:
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

   ```bash
   sudo systemctl enable claude-chat
   sudo systemctl start claude-chat
   ```

## Notes

- Never commit your `.env` file — it's listed in `.gitignore`
- The Flask dev server is fine for personal/low-traffic use, but consider gunicorn for higher traffic