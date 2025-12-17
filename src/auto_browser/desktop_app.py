"""
Desktop application wrapper for browser automation web UI.
Embeds Flask server and displays UI in PyQt6 window.

Phase 0 version: Tests ElevenLabs integration without Nova Act backend.
"""

import sys
import os
import threading

# Enable web inspector BEFORE importing Qt
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9223'

from PyQt6.QtCore import QUrl, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage, QWebEngineProfile


class WebPage(QWebEnginePage):
    """Custom web page that logs console messages and handles permissions"""

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """Log JavaScript console messages to terminal"""
        level_names = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }
        level_name = level_names.get(level, "LOG")

        print(f"\n[JS {level_name}] {message}")
        if sourceID:
            print(f"  Source: {sourceID}:{lineNumber}")

    def featurePermissionRequested(self, securityOrigin, feature):
        """Handle permission requests (microphone, camera, etc.)"""
        from PyQt6.QtWebEngineCore import QWebEnginePage

        feature_names = {
            QWebEnginePage.Feature.MediaAudioCapture: "Microphone",
            QWebEnginePage.Feature.MediaVideoCapture: "Camera",
            QWebEnginePage.Feature.MediaAudioVideoCapture: "Microphone and Camera",
            QWebEnginePage.Feature.Geolocation: "Location",
            QWebEnginePage.Feature.Notifications: "Notifications"
        }

        feature_name = feature_names.get(feature, f"Feature {feature}")
        print(f"\n[PERMISSION] {feature_name} access requested by {securityOrigin.toString()}")
        print(f"[PERMISSION] Granting {feature_name} access...")

        # Grant the permission
        self.setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def certificateError(self, error):
        """Handle SSL certificate errors"""
        print(f"\n[SSL ERROR] {error.errorDescription()}")
        print(f"[SSL ERROR] URL: {error.url().toString()}")
        # Ignore SSL errors for localhost and unpkg.com (for development)
        return True


class FlaskServerThread(QObject):
    """Flask server running in background thread"""

    server_started = pyqtSignal(str)  # Emits URL when ready
    server_error = pyqtSignal(str)    # Emits error message

    def __init__(self, host='127.0.0.1', port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        """Start Flask server in background thread"""
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def _run_server(self):
        """Run Flask server - executes in background thread"""
        try:
            # Ensure src is in path
            import sys
            src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            # Import Flask app
            from auto_browser import web_ui

            # Get server object for manual control
            from werkzeug.serving import make_server
            self.server = make_server(self.host, self.port, web_ui.app)

            # Signal that server is ready
            url = f"http://{self.host}:{self.port}"
            self.server_started.emit(url)

            print(f"\n{'='*80}")
            print("Flask Server Starting")
            print(f"{'='*80}")
            print(f"Server URL: {url}")
            print(f"{'='*80}\n")

            # Start serving
            self.server.serve_forever()

        except Exception as e:
            error_msg = f"Flask server failed: {str(e)}"
            print(f"\nERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            self.server_error.emit(error_msg)

    def stop(self):
        """Stop Flask server"""
        if self.server:
            print("\nStopping Flask server...")
            self.server.shutdown()

            # Wait for thread to finish
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
            print("Flask server stopped.")


class DesktopBrowserAutomationApp(QMainWindow):
    """Main desktop application window"""

    def __init__(self, host='127.0.0.1', port=5000):
        super().__init__()

        self.host = host
        self.port = port
        self.flask_server = None

        # Setup UI
        self.init_ui()

        # Start Flask server
        self.start_server()

    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowTitle("Browser Automation - Voice Interface")
        self.setGeometry(100, 100, 1200, 800)

        # Center window on screen
        self.center_on_screen()

        # Create web view with custom page for console logging
        self.web_view = QWebEngineView()

        # Configure profile with permissive settings
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.web_page = WebPage(self.web_view)
        self.web_view.setPage(self.web_page)
        self.setCentralWidget(self.web_view)

        # Configure web engine settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowGeolocationOnInsecureOrigins, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)

        # Enable developer tools for debugging
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        print("\nWeb Inspector enabled at: http://localhost:9223")
        print("Open this URL in Chrome/Edge to see console logs and network requests")
        print("\nWebEngine settings configured for ElevenLabs widget:")
        print("  - Insecure content allowed")
        print("  - WebSockets enabled")
        print("  - Autoplay enabled\n")

        # Show loading message
        self.web_view.setHtml("""
            <html>
            <body style="display: flex; align-items: center; justify-content: center;
                         height: 100vh; font-family: sans-serif; background: #f5f5f5;">
                <div style="text-align: center;">
                    <h1>Browser Automation</h1>
                    <p>Initializing server...</p>
                    <p style="color: #666; font-size: 14px;">Please wait while the application starts up.</p>
                </div>
            </body>
            </html>
        """)

    def center_on_screen(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def start_server(self):
        """Start Flask server in background"""
        self.flask_server = FlaskServerThread(
            host=self.host,
            port=self.port
        )

        # Connect signals
        self.flask_server.server_started.connect(self.on_server_started)
        self.flask_server.server_error.connect(self.on_server_error)

        # Start server thread
        self.flask_server.start()

    def on_server_started(self, url):
        """Called when Flask server is ready"""
        print(f"\nFlask server ready at {url}")
        print("Loading UI in desktop window...\n")
        self.web_view.load(QUrl(url))

    def on_server_error(self, error):
        """Called when Flask server encounters error"""
        print(f"\nERROR: Flask server failed: {error}")
        self.web_view.setHtml(f"""
            <html>
            <body style="display: flex; align-items: center; justify-content: center;
                         height: 100vh; font-family: sans-serif; background: #f5f5f5;">
                <div style="text-align: center; color: #d32f2f;">
                    <h1>Error</h1>
                    <p>Failed to start server</p>
                    <p style="color: #666; font-size: 14px;">{error}</p>
                    <p style="color: #666; font-size: 14px;">Check console for details.</p>
                </div>
            </body>
            </html>
        """)

    def closeEvent(self, event):
        """Handle window close event"""
        print("\n{'='*80}")
        print("Closing application...")
        print("{'='*80}\n")

        # Stop Flask server
        if self.flask_server:
            self.flask_server.stop()

        print("Application closed.\n")
        event.accept()


def run_desktop_app(host='127.0.0.1', port=5000):
    """
    Launch desktop application (Phase 0 version for testing ElevenLabs integration)

    Args:
        host: Flask server host (default: 127.0.0.1)
        port: Flask server port (default: 5000)
    """
    print(f"\n{'='*80}")
    print("Browser Automation Desktop UI")
    print("Phase 0: ElevenLabs Integration Test")
    print(f"{'='*80}")
    print("\nStarting desktop application...")
    print("Speak to the ElevenLabs widget to test the voice interface.\n")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Browser Automation")

    # Create main window
    window = DesktopBrowserAutomationApp(
        host=host,
        port=port
    )

    # Show window
    window.show()

    # Run Qt event loop
    sys.exit(app.exec())
