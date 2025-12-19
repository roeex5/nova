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
        self.lock = threading.RLock()  # Use RLock to allow re-entrant locking (prevent deadlocks)
        self.api_key = None
        self.starting_page = None
        self.headless = False
        self.verbose = os.getenv('VERBOSE', '').lower() in ('true', '1', 'yes')

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
            if self.verbose:
                print("[VERBOSE] Browser already initialized, skipping")
            return  # Already initialized

        if not self.is_configured:
            raise RuntimeError("Automation not configured. Call configure() first.")

        print(f"\n{'='*80}")
        print("🚀 Starting Browser (First Command)")
        print(f"{'='*80}")
        print(f"Initializing browser automation with starting page: {self.starting_page}")
        if self.verbose:
            print(f"[VERBOSE] API key (masked): {self.api_key[:8]}...{self.api_key[-8:] if self.api_key else 'None'}")
            print(f"[VERBOSE] Headless mode: {self.headless}")
        print(f"{'='*80}\n")

        try:
            if self.verbose:
                print("[VERBOSE] Importing BrowserUI from main module...")
            from .main import BrowserUI

            if self.verbose:
                print("[VERBOSE] Creating BrowserUI instance...")
            self.browser = BrowserUI(api_key=self.api_key, headless=self.headless)

            if self.verbose:
                print(f"[VERBOSE] Starting browser with page: {self.starting_page}")
            self.browser.start(starting_page=self.starting_page)
            self.is_ready = True

            print(f"\n{'='*80}")
            print("✅ Browser Automation: READY")
            if self.verbose:
                print(f"[VERBOSE] Browser session ID: {id(self.browser)}")
                print(f"[VERBOSE] Browser ready state: {self.is_ready}")
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"\n{'='*80}")
            print(f"❌ ERROR: Failed to initialize browser")
            print(f"{'='*80}")
            print(f"{e}\n")
            if self.verbose:
                print("[VERBOSE] Full traceback:")
            import traceback
            traceback.print_exc()

            # Clean up partially initialized browser to prevent resource leak
            if self.browser is not None:
                try:
                    if self.verbose:
                        print("[VERBOSE] Cleaning up partially initialized browser...")
                    self.browser.stop()
                except Exception as cleanup_error:
                    if self.verbose:
                        print(f"[VERBOSE] Cleanup error (non-fatal): {cleanup_error}")
                finally:
                    self.browser = None
                    self.is_ready = False

            raise

    def execute_prompt(self, prompt):
        """Execute automation prompt - thread-safe with lazy initialization"""
        with self.lock:
            if self.verbose:
                print(f"[VERBOSE] Lock acquired for prompt execution")
                print(f"[VERBOSE] Browser ready state: {self.is_ready}")

            # Initialize browser on first use (lazy)
            if not self.is_ready:
                if self.verbose:
                    print("[VERBOSE] Browser not ready, initializing...")
                self._initialize_if_needed()

            # Execute automation - this may take a while
            print(f"\n[AUTOMATION] Executing: {prompt}")
            if self.verbose:
                print(f"[VERBOSE] Calling browser.agent.act() with prompt length: {len(prompt)}")

            try:
                self.browser.agent.act(prompt)
                if self.verbose:
                    print(f"[VERBOSE] browser.agent.act() completed successfully")
                print(f"[AUTOMATION] Completed\n")
            except Exception as e:
                print(f"\n[AUTOMATION ERROR] Failed to execute: {e}")
                if self.verbose:
                    print("[VERBOSE] Full error traceback:")
                    import traceback
                    traceback.print_exc()
                raise

    def close_browser(self):
        """Close the browser and clean up resources (callable from API)"""
        with self.lock:
            if self.browser:
                if self.verbose:
                    print("[VERBOSE] Closing browser session...")
                print("\nClosing browser session...")
                try:
                    self.browser.stop()
                    if self.verbose:
                        print("[VERBOSE] Browser stopped successfully")
                except Exception as e:
                    print(f"Error during browser close: {e}")
                    if self.verbose:
                        import traceback
                        traceback.print_exc()
                finally:
                    self.browser = None
                    self.is_ready = False
                    print("Browser session closed.")
                return True
            else:
                if self.verbose:
                    print("[VERBOSE] No active browser to close")
                return False

    def shutdown(self):
        """Clean shutdown of browser session (alias for close_browser for backward compatibility)"""
        self.close_browser()

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
        <!-- Voice Conversational AI Widget -->
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

                                // Log what we're returning to voice agent
                                console.log('[VOICE] Returning to agent:', result.message);

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

                // Listen for call end event to close browser
                widget.addEventListener('elevenlabs-convai:status', async (event) => {
                    const status = event.detail?.status;
                    console.log('[WIDGET] Status update:', status);

                    // When call ends (widget goes back to idle), close the browser
                    if (status === 'idle' || status === 'disconnected') {
                        console.log('[WIDGET] Call ended, closing browser...');
                        {% if expanded_ui %}
                        log('Call Ended - Closing Browser', { status });
                        {% endif %}

                        try {
                            const response = await fetch('http://localhost:5000/api/close_browser', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                }
                            });

                            const result = await response.json();
                            console.log('[BROWSER] Close response:', result);
                            {% if expanded_ui %}
                            log('Browser Close Result', result);
                            {% endif %}
                        } catch (error) {
                            console.error('[BROWSER] Error closing browser:', error);
                            {% if expanded_ui %}
                            log('Browser Close Error', { message: error.message });
                            {% endif %}
                        }
                    }
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
    print(f"\n[DEBUG] / route hit, is_configured: {automation_server.is_configured}")

    # Check if automation is configured
    if not automation_server.is_configured:
        # Redirect to setup if not configured
        print("[DEBUG] Redirecting to /setup")
        from flask import redirect, url_for
        return redirect(url_for('setup'))

    print("[DEBUG] Serving main UI")

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
        if automation_server.verbose:
            print(f"[VERBOSE] /api/execute_automation called")
            print(f"[VERBOSE] Request data: {data}")
            print(f"[VERBOSE] Request headers: {dict(request.headers)}")

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
        if automation_server.verbose:
            print(f"[VERBOSE] Prompt length: {len(prompt)} characters")
            print(f"[VERBOSE] Automation server configured: {automation_server.is_configured}")
            print(f"[VERBOSE] Browser ready: {automation_server.is_ready}")
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


@app.route('/api/close_browser', methods=['POST'])
def close_browser_endpoint():
    """
    Endpoint to close the browser session.
    Called when the voice widget call ends or user explicitly requests browser close.
    """
    try:
        if automation_server.verbose:
            print(f"[VERBOSE] /api/close_browser called")
            print(f"[VERBOSE] Request headers: {dict(request.headers)}")

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not automation_server.is_configured:
            return jsonify({
                'status': 'error',
                'message': 'Automation not configured',
                'timestamp': timestamp
            }), 400

        # Attempt to close browser
        was_open = automation_server.close_browser()

        if was_open:
            message = 'Browser session closed successfully'
            print(f"\n{'='*80}")
            print(f"[{timestamp}] {message}")
            print(f"{'='*80}\n")
        else:
            message = 'No active browser session to close'
            if automation_server.verbose:
                print(f"[VERBOSE] {message}")

        return jsonify({
            'status': 'success',
            'message': message,
            'was_open': was_open,
            'timestamp': timestamp
        })

    except Exception as e:
        error_msg = f"Error closing browser: {str(e)}"
        print(f"\n{'='*80}")
        print(f"ERROR: {error_msg}")
        print(f"{'='*80}\n")

        if automation_server.verbose:
            import traceback
            traceback.print_exc()

        return jsonify({
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


@app.route('/setup')
def setup():
    """Show API key setup page"""
    SETUP_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Setup - Browser Automation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .setup-card {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 24px;
        }
        .subtitle {
            color: #666;
            margin: 0 0 30px 0;
            font-size: 14px;
        }
        label {
            display: block;
            margin: 20px 0 8px 0;
            color: #333;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #007acc;
        }
        .help-text {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #007acc;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            margin-top: 30px;
        }
        button:hover {
            background: #005a9e;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .error {
            color: #d32f2f;
            font-size: 14px;
            margin-top: 10px;
            display: none;
        }
        .success {
            color: #388e3c;
            font-size: 14px;
            margin-top: 10px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="setup-card">
        <h1>Welcome to Browser Automation</h1>
        <p class="subtitle">Configure your API keys to get started</p>

        <form id="setupForm">
            <label for="apiKey">Main API Key *</label>
            <input type="password" id="apiKey" name="apiKey" required placeholder="Enter your main API key">
            <div class="help-text">Required for browser automation</div>

            <label for="agentId">Voice Agent ID (Optional)</label>
            <input type="text" id="agentId" name="agentId" placeholder="agent_xxxxxxxxxxxxxxxxx">
            <div class="help-text">Optional: For voice control features</div>

            <button type="submit" id="submitBtn">Save and Continue</button>

            <div class="error" id="error"></div>
            <div class="success" id="success"></div>
        </form>
    </div>

    <script>
        document.getElementById('setupForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitBtn');
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');

            submitBtn.disabled = true;
            submitBtn.textContent = 'Saving...';
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';

            try {
                const response = await fetch('/api/save_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        api_key: document.getElementById('apiKey').value,
                        agent_id: document.getElementById('agentId').value
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    successDiv.textContent = 'Configuration saved! Redirecting...';
                    successDiv.style.display = 'block';
                    setTimeout(() => window.location.href = '/', 1000);
                } else {
                    errorDiv.textContent = result.message || 'Failed to save configuration';
                    errorDiv.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Save and Continue';
                }
            } catch (error) {
                errorDiv.textContent = 'Error: ' + error.message;
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Save and Continue';
            }
        });
    </script>
</body>
</html>
    """
    return render_template_string(SETUP_TEMPLATE)


@app.route('/api/save_config', methods=['POST'])
def save_config():
    """Save API configuration"""
    try:
        from .config_manager import ConfigManager

        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        agent_id = data.get('agent_id', '').strip()

        if not api_key:
            return jsonify({'status': 'error', 'message': 'API key is required'}), 400

        # Save config
        config = {'nova_act_api_key': api_key}
        if agent_id:
            config['elevenlabs_agent_id'] = agent_id
            os.environ['ELEVENLABS_AGENT_ID'] = agent_id

        ConfigManager.save_config(config)

        # Configure automation
        automation_server.configure(
            api_key=api_key,
            starting_page="https://google.com",
            headless=False
        )

        print(f"\n✓ Configuration saved and automation enabled")

        return jsonify({'status': 'success', 'message': 'Configuration saved'})

    except Exception as e:
        print(f"\n✗ Error saving config: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


def run_ui(host='127.0.0.1', port=5000, api_key=None,
           starting_page="https://google.com", headless=False, threaded=False, expanded_ui=False):
    """
    Start the web UI server with browser automation.

    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to listen on (default: 5000)
        api_key: Main API key (required for automation)
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
        print("Set API key via configuration or pass --api-key\n")

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
