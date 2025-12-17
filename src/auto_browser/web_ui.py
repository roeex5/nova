"""
Web UI for browser automation with ElevenLabs voice interface.
Serves the widget and handles client tool calls.
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for client tool calls

# HTML template with ElevenLabs widget
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Browser Automation - Voice Interface</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        h1 {
            margin: 0 0 10px 0;
            color: #333;
        }

        .subtitle {
            color: #666;
            margin: 0;
        }

        .console {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .log-entry {
            margin: 5px 0;
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }

        .log-time {
            color: #858585;
            margin-right: 10px;
        }

        .log-event {
            color: #4ec9b0;
            font-weight: bold;
        }

        .log-data {
            color: #ce9178;
            margin-top: 5px;
            padding-left: 20px;
            white-space: pre-wrap;
        }

        .clear-btn {
            background: #007acc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }

        .clear-btn:hover {
            background: #005a9e;
        }

        .status {
            background: #2d2d30;
            color: #cccccc;
            padding: 10px 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4ec9b0;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Browser Automation</h1>
        <p class="subtitle">Voice-controlled automation interface</p>
    </div>

    <div class="status">
        <span class="status-indicator"></span>
        Connected to automation backend
    </div>

    <div class="console" id="console">
        <div class="log-entry">
            <span class="log-time">Ready</span>
            <span class="log-event">Waiting for voice commands...</span>
        </div>
    </div>

    <button class="clear-btn" onclick="clearConsole()">Clear Console</button>

    <!-- ElevenLabs Conversational AI Widget -->
    <elevenlabs-convai agent-id="{{ agent_id }}"></elevenlabs-convai>
    <script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>

    <script>
        const consoleEl = document.getElementById('console');

        function log(event, data) {
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = 'log-entry';

            let html = `<span class="log-time">[${time}]</span><span class="log-event">${event}</span>`;

            if (data) {
                const dataStr = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
                html += `<div class="log-data">${dataStr}</div>`;
            }

            entry.innerHTML = html;
            consoleEl.appendChild(entry);
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }

        function clearConsole() {
            consoleEl.innerHTML = '<div class="log-entry"><span class="log-time">Ready</span><span class="log-event">Waiting for voice commands...</span></div>';
        }

        // Register client tools when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            console.log('[WIDGET] DOM loaded, searching for widget element...');
            const widget = document.querySelector('elevenlabs-convai');

            if (widget) {
                console.log('[WIDGET] Widget element found:', widget);
                log('Widget Element Found', { agentId: '{{ agent_id }}' });

                // Listen to all widget events for debugging
                widget.addEventListener('elevenlabs-convai:status', (event) => {
                    console.log('[WIDGET STATUS]', event.detail);
                    log('Widget Status Change', event.detail);
                });

                widget.addEventListener('elevenlabs-convai:error', (event) => {
                    console.error('[WIDGET ERROR]', event.detail);
                    log('Widget Error', event.detail);
                });

                widget.addEventListener('elevenlabs-convai:message', (event) => {
                    console.log('[WIDGET MESSAGE]', event.detail);
                    log('Widget Message', { message: event.detail });
                });

                // Register client tools when the widget initiates a call
                widget.addEventListener('elevenlabs-convai:call', (event) => {
                    console.log('[WIDGET] Call initiated, registering client tools...');
                    log('Registering Client Tools', null);

                    // Register the send_prompt_to_automation tool
                    event.detail.config.clientTools = {
                        send_prompt_to_automation: async ({ prompt }) => {
                            log('Tool Called: send_prompt_to_automation', { prompt });

                            try {
                                // Send prompt to Python backend
                                const response = await fetch('/api/execute_automation', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({ prompt })
                                });

                                const result = await response.json();
                                log('Backend Response', result);

                                // Log what we're returning to ElevenLabs
                                console.log('[ELEVENLABS] Returning to agent:', result.message);

                                return result.message || 'Command received';
                            } catch (error) {
                                log('Error', { message: error.message });
                                return `Error: ${error.message}`;
                            }
                        }
                    };

                    log('Client Tools Registered', {
                        tools: ['send_prompt_to_automation']
                    });
                });
            } else {
                console.error('[WIDGET] Widget element NOT FOUND in DOM!');
                log('Widget Error', { error: 'Widget element not found' });
            }
        });

        // Check if widget script loaded
        window.addEventListener('load', () => {
            console.log('[WIDGET] Page fully loaded');
            const scripts = document.querySelectorAll('script');
            const widgetScript = Array.from(scripts).find(s => s.src.includes('convai-widget-embed'));
            if (widgetScript) {
                console.log('[WIDGET] Widget script found:', widgetScript.src);
            } else {
                console.error('[WIDGET] Widget script NOT FOUND!');
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main UI with ElevenLabs widget."""
    agent_id = os.getenv('ELEVENLABS_AGENT_ID', 'agent_0901kckpgzzgecfb8dsh31a3h45w')
    print(f"\n[UI] Serving page with ElevenLabs Agent ID: {agent_id}\n")

    response = app.make_response(render_template_string(HTML_TEMPLATE, agent_id=agent_id))

    # Add permissive CSP to allow WebSocket connections, AudioWorklets, and external scripts
    # AudioWorklets require blob: URLs and worker-src directive
    response.headers['Content-Security-Policy'] = (
        "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; "
        "connect-src * wss: ws: blob:; "
        "script-src * 'unsafe-inline' 'unsafe-eval' blob:; "
        "worker-src * blob:; "
        "child-src * blob:; "
        "img-src * data: blob:; "
        "media-src * data: blob:; "
        "font-src * data: blob:;"
    )

    return response


@app.route('/api/execute_automation', methods=['POST'])
def execute_automation():
    """
    Endpoint called by the ElevenLabs client tool.
    Receives the automation prompt and processes it.
    """
    data = request.get_json()
    prompt = data.get('prompt', '')

    # Print to terminal
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*80}")
    print(f"[{timestamp}] AUTOMATION PROMPT RECEIVED:")
    print(f"{'-'*80}")
    print(prompt)
    print(f"{'='*80}\n")

    # Phase 0: Return detailed test response (Nova Act integration comes in Phase 1)
    response_message = (
        f"Done! I've received your automation request: {prompt}. "
        f"The integration is working correctly and I can hear you clearly. "
        f"In the next phase, this will execute real browser automation."
    )

    print(f"\n{'='*80}")
    print(f"[{timestamp}] SENDING RESPONSE TO ELEVENLABS:")
    print(f"{'-'*80}")
    print(response_message)
    print(f"{'='*80}\n")

    return jsonify({
        'status': 'success',
        'message': response_message,
        'timestamp': timestamp,
        'prompt': prompt
    })


def run_ui(host='127.0.0.1', port=5000):
    """
    Start the web UI server.

    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to listen on (default: 5000)
    """
    print(f"\n{'='*80}")
    print("Browser Automation - Voice Interface")
    print(f"{'='*80}")
    print(f"\nServer starting on http://{host}:{port}")
    print("\nOpen your browser and navigate to the URL above.")
    print("Speak to the widget to send automation commands.\n")

    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_ui()
