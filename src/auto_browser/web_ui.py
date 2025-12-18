"""
Web UI for browser automation with ElevenLabs voice interface.
Serves the widget and handles client tool calls.
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import os
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for client tool calls


class AutomationServer:
    """Thread-safe browser automation session manager with lazy initialization"""

    def __init__(self):
        self.browser = None
        self.is_ready = False
        self.is_configured = False
        self.lock = threading.Lock()
        self.api_key = None
        self.starting_page = None
        self.headless = False

    def configure(self, api_key, starting_page="https://google.com", headless=False):
        """Configure automation settings (doesn't start browser yet)"""
        with self.lock:
            if self.is_configured:
                print("\n⚠️  Automation already configured, skipping...")
                return

            self.api_key = api_key
            self.starting_page = starting_page
            self.headless = headless
            self.is_configured = True

            print(f"\n{'='*80}")
            print("Browser Automation: CONFIGURED")
            print(f"{'='*80}")
            print(f"Starting page: {starting_page}")
            print(f"Headless mode: {headless}")
            print(f"Browser will start on first command (lazy initialization)")
            print(f"{'='*80}\n")

    def _initialize_if_needed(self):
        """Initialize browser if not already initialized (lazy init)"""
        # This must be called while holding the lock
        if self.is_ready and self.browser is not None:
            return  # Already initialized

        if not self.is_configured:
            raise RuntimeError("Automation not configured. Call configure() first.")

        print(f"\n{'='*80}")
        print("🚀 Starting Browser (First Command)")
        print(f"{'='*80}")
        print(f"Initializing browser automation with starting page: {self.starting_page}")
        print(f"{'='*80}\n")

        try:
            from .main import BrowserUI
            self.browser = BrowserUI(api_key=self.api_key, headless=self.headless)
            self.browser.start(starting_page=self.starting_page)
            self.is_ready = True

            print(f"\n{'='*80}")
            print("✅ Browser Automation: READY")
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"\n{'='*80}")
            print(f"❌ ERROR: Failed to initialize browser")
            print(f"{'='*80}")
            print(f"{e}\n")
            import traceback
            traceback.print_exc()
            raise

    def execute_prompt(self, prompt):
        """Execute automation prompt - thread-safe with lazy initialization"""
        with self.lock:
            # Initialize browser on first use (lazy)
            if not self.is_ready:
                self._initialize_if_needed()

            # Execute automation - this may take a while
            print(f"\n[AUTOMATION] Executing: {prompt}")
            self.browser.agent.act(prompt)
            print(f"[AUTOMATION] Completed\n")

    def shutdown(self):
        """Clean shutdown of browser session"""
        with self.lock:
            if self.browser:
                print("\nShutting down browser session...")
                try:
                    self.browser.stop()
                except Exception as e:
                    print(f"Error during shutdown: {e}")
                finally:
                    self.browser = None
                    self.is_ready = False
                    print("Browser session stopped.")

    def is_busy(self):
        """Check if currently executing a command"""
        return self.lock.locked()


# Global automation server instance
automation_server = AutomationServer()

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
            max-width: {% if expanded_ui %}1200px{% else %}600px{% endif %};
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }

        /* Title header styling */
        .app-title {
            text-align: center;
            font-size: 24px;
            font-weight: 600;
            color: #333;
            margin: 15px 0 25px 0;
            padding: 0;
        }

        /* Hide ElevenLabs branding footer with gradient overlay */
        .branding-overlay {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 32px;
            background: linear-gradient(to bottom, rgba(245,245,245,0) 0%, rgba(245,245,245,0.9) 25%, rgba(245,245,245,1) 50%);
            z-index: 9999;
            pointer-events: none;
        }

        {% if expanded_ui %}
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
        {% endif %}
    </style>
</head>
<body>
    {% if expanded_ui %}
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
    {% endif %}

    {% if not expanded_ui %}
    <!-- Title for minimal UI mode -->
    <h1 class="app-title">Web Automation Agent</h1>
    {% endif %}

    <!-- Widget wrapper to enable branding hiding -->
    <div class="widget-wrapper">
        <!-- ElevenLabs Conversational AI Widget -->
        <elevenlabs-convai agent-id="{{ agent_id }}"></elevenlabs-convai>
    </div>

    <!-- Overlay to hide branding footer -->
    <div class="branding-overlay"></div>

    <script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>

    <script>
        {% if expanded_ui %}
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
        {% else %}
        // Minimal UI (default) - stub functions for widget compatibility
        function log(event, data) {
            console.log('[LOG]', event, data);
        }
        {% endif %}

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
                    {% if expanded_ui %}
                    log('Widget Status Change', event.detail);
                    {% endif %}
                });

                widget.addEventListener('elevenlabs-convai:error', (event) => {
                    console.error('[WIDGET ERROR]', event.detail);
                    {% if expanded_ui %}
                    log('Widget Error', event.detail);
                    {% endif %}
                });

                widget.addEventListener('elevenlabs-convai:message', (event) => {
                    console.log('[WIDGET MESSAGE]', event.detail);
                    {% if expanded_ui %}
                    log('Widget Message', { message: event.detail });
                    {% endif %}
                });

                // Register client tools when the widget initiates a call
                widget.addEventListener('elevenlabs-convai:call', (event) => {
                    console.log('[WIDGET] Call initiated, registering client tools...');
                    {% if expanded_ui %}
                    log('Registering Client Tools', null);
                    {% endif %}

                    // Register the send_prompt_to_automation tool
                    event.detail.config.clientTools = {
                        send_prompt_to_automation: async ({ prompt }) => {
                            {% if expanded_ui %}
                            log('Tool Called: send_prompt_to_automation', { prompt });
                            {% endif %}

                            try {
                                // Send prompt to Python backend (use absolute URL for Tauri compatibility)
                                const response = await fetch('http://localhost:5000/api/execute_automation', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({ prompt })
                                });

                                const result = await response.json();
                                {% if expanded_ui %}
                                log('Backend Response', result);
                                {% endif %}

                                // Log what we're returning to ElevenLabs
                                console.log('[ELEVENLABS] Returning to agent:', result.message);

                                return result.message || 'Command received';
                            } catch (error) {
                                {% if expanded_ui %}
                                log('Error', { message: error.message });
                                {% endif %}
                                return `Error: ${error.message}`;
                            }
                        }
                    };

                    {% if expanded_ui %}
                    log('Client Tools Registered', {
                        tools: ['send_prompt_to_automation']
                    });
                    {% endif %}
                });
            } else {
                console.error('[WIDGET] Widget element NOT FOUND in DOM!');
                {% if expanded_ui %}
                log('Widget Error', { error: 'Widget element not found' });
                {% endif %}
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
    expanded_ui = getattr(app, 'expanded_ui', False)
    print(f"\n[UI] Serving page with ElevenLabs Agent ID: {agent_id}")
    print(f"[UI] Expanded UI mode: {expanded_ui}\n")

    response = app.make_response(render_template_string(HTML_TEMPLATE, agent_id=agent_id, expanded_ui=expanded_ui))

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
    Receives the automation prompt and executes it via Nova Act.
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or missing JSON data'
            }), 400
        
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'No prompt provided'
            }), 400

        # Log receipt
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'='*80}")
        print(f"[{timestamp}] AUTOMATION PROMPT RECEIVED:")
        print(f"{'-'*80}")
        print(prompt)
        print(f"{'='*80}\n")

        # Execute automation via Nova Act
        print("Executing automation...")
        automation_server.execute_prompt(prompt)

        # Format detailed response
        response_message = (
            f"Done! I've completed the automation task: {prompt}. "
            f"The browser action has finished successfully."
        )

        print(f"\n{'='*80}")
        print(f"[{timestamp}] AUTOMATION COMPLETED")
        print(f"{'-'*80}")
        print(response_message)
        print(f"{'='*80}\n")

        return jsonify({
            'status': 'success',
            'message': response_message,
            'timestamp': timestamp,
            'prompt': prompt
        })

    except RuntimeError as e:
        # Browser not initialized
        error_msg = f"Browser not ready: {str(e)}"
        print(f"\n{'='*80}")
        print(f"ERROR: {error_msg}")
        print(f"{'='*80}\n")

        return jsonify({
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 503

    except Exception as e:
        # Automation error
        error_msg = f"Error executing automation: {str(e)}"
        print(f"\n{'='*80}")
        print(f"ERROR: {error_msg}")
        print(f"{'='*80}\n")

        import traceback
        traceback.print_exc()

        return jsonify({
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


def run_ui(host='127.0.0.1', port=5000, api_key=None,
           starting_page="https://google.com", headless=False, threaded=False, expanded_ui=False):
    """
    Start the web UI server with browser automation.

    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to listen on (default: 5000)
        api_key: Nova Act API key (required for automation)
        starting_page: Initial browser page (default: https://google.com)
        headless: Run browser in headless mode (default: False)
        threaded: If True, returns server object for manual control (for PyQt integration)
        expanded_ui: Show full UI with header, console, and status (default: False - minimal widget-only UI)
    """
    # Store expanded_ui flag in app for template access
    app.expanded_ui = expanded_ui
    
    # Configure automation backend if API key provided
    # Note: Browser will start lazily on first command (not immediately)
    if api_key:
        try:
            automation_server.configure(api_key, starting_page, headless)
        except Exception as e:
            print(f"\nFailed to configure browser automation: {e}")
            print("Server will start but automation will not be available.\n")
    else:
        print("\n⚠️  WARNING: No API key provided, automation will not be available")
        print("Set NOVA_ACT_API_KEY environment variable or pass --api-key\n")

    print(f"\n{'='*80}")
    print("Browser Automation - Voice Interface")
    print(f"{'='*80}")
    print(f"\nServer starting on http://{host}:{port}")
    print("\nOpen your browser and navigate to the URL above.")
    print("Speak to the widget to send automation commands.\n")

    if threaded:
        # Return server for manual control (PyQt integration)
        from werkzeug.serving import make_server
        server = make_server(host, port, app)
        return server
    else:
        # Run normally
        try:
            app.run(host=host, port=port, debug=False, use_reloader=False)
        finally:
            automation_server.shutdown()


if __name__ == '__main__':
    run_ui()
