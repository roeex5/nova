"""
First-run setup dialog for Browser Automation Desktop App.
Collects API keys and credentials from user on initial launch.

Created: 2025-12-17
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCursor

from .config_manager import ConfigManager


class SetupDialog(QDialog):
    """First-run setup dialog for collecting API credentials"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nova_api_key = None
        self.elevenlabs_agent_id = None
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Browser Automation - Initial Setup")
        self.setMinimumWidth(600)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title and description
        title = QLabel("Welcome to Browser Automation")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        description = QLabel(
            "This app provides voice-controlled browser automation.\n"
            "To get started, please provide your API credentials below."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Main API Key section
        nova_label = QLabel("Main API Key")
        nova_label_font = QFont()
        nova_label_font.setBold(True)
        nova_label.setFont(nova_label_font)
        layout.addWidget(nova_label)

        nova_help = QLabel(
            "Required for browser automation functionality.\n"
            "Contact your administrator for the API key."
        )
        nova_help.setStyleSheet("color: #666; font-size: 11px;")
        nova_help.setWordWrap(True)
        layout.addWidget(nova_help)

        self.nova_input = QLineEdit()
        self.nova_input.setPlaceholderText("Enter your API key...")
        self.nova_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.nova_input)

        self.nova_show_checkbox = QCheckBox("Show API key")
        self.nova_show_checkbox.stateChanged.connect(self.toggle_nova_visibility)
        layout.addWidget(self.nova_show_checkbox)

        # Voice Agent ID section
        elevenlabs_label = QLabel("Voice Agent ID")
        elevenlabs_label.setFont(nova_label_font)
        layout.addWidget(elevenlabs_label)

        elevenlabs_help = QLabel(
            "Optional - for voice interface customization.\n"
            "Leave blank to use the default voice agent."
        )
        elevenlabs_help.setStyleSheet("color: #666; font-size: 11px;")
        elevenlabs_help.setWordWrap(True)
        layout.addWidget(elevenlabs_help)

        self.elevenlabs_input = QLineEdit()
        self.elevenlabs_input.setPlaceholderText("Enter your Voice Agent ID (optional)...")
        layout.addWidget(self.elevenlabs_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Skip for Now")
        self.cancel_button.clicked.connect(self.handle_skip)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save and Continue")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.handle_save)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        # Warning label
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #D32F2F; font-weight: bold;")
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()
        layout.addWidget(self.warning_label)

        self.setLayout(layout)

    def toggle_nova_visibility(self, state):
        """Toggle visibility of Main API key field"""
        if state == Qt.CheckState.Checked.value:
            self.nova_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.nova_input.setEchoMode(QLineEdit.EchoMode.Password)

    def validate_inputs(self) -> bool:
        """Validate user inputs"""
        nova_key = self.nova_input.text().strip()

        if not nova_key:
            self.show_warning("Main API Key is required for browser automation.")
            return False

        # Basic validation: check if it looks like an API key
        if len(nova_key) < 10:
            self.show_warning("Main API Key appears to be invalid (too short).")
            return False

        return True

    def show_warning(self, message: str):
        """Show warning message in dialog"""
        self.warning_label.setText(message)
        self.warning_label.show()

    def handle_skip(self):
        """Handle skip button click"""
        reply = QMessageBox.question(
            self,
            "Skip Setup?",
            "Without API credentials, browser automation will not work.\n\n"
            "You can configure credentials later by deleting:\n"
            f"{ConfigManager.CONFIG_FILE}\n\n"
            "Are you sure you want to skip?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.reject()

    def handle_save(self):
        """Handle save button click"""
        if not self.validate_inputs():
            return

        nova_key = self.nova_input.text().strip()
        elevenlabs_id = self.elevenlabs_input.text().strip()

        # Validate API key with server
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.show_warning("Validating API key...")

        # Use QTimer to validate after UI updates
        QTimer.singleShot(100, lambda: self._perform_validation(nova_key, elevenlabs_id))

    def _perform_validation(self, nova_key: str, elevenlabs_id: str):
        """Perform API key validation"""
        try:
            is_valid, error_msg = ConfigManager.validate_api_key(nova_key)

            # Restore cursor and buttons
            self.unsetCursor()
            self.save_button.setEnabled(True)
            self.cancel_button.setEnabled(True)

            if not is_valid:
                self.show_warning(f"API key validation failed: {error_msg}")
                return

            # Validation successful - save config
            self.warning_label.hide()
            config = {
                'nova_act_api_key': nova_key
            }

            if elevenlabs_id:
                config['elevenlabs_agent_id'] = elevenlabs_id

            if ConfigManager.save_config(config):
                self.nova_api_key = nova_key
                self.elevenlabs_agent_id = elevenlabs_id if elevenlabs_id else None
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to save configuration. Please check permissions and try again."
                )
        except Exception as e:
            self.unsetCursor()
            self.save_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
            self.show_warning(f"Validation error: {str(e)}")

    @staticmethod
    def run_if_needed(parent=None) -> tuple[str | None, str | None]:
        """
        Show setup dialog if config doesn't exist.
        Returns (nova_api_key, elevenlabs_agent_id) tuple.
        """
        # Check if we already have configuration
        if ConfigManager.config_exists():
            return ConfigManager.get_api_key(), ConfigManager.get_agent_id()

        # Show setup dialog
        dialog = SetupDialog(parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return dialog.nova_api_key, dialog.elevenlabs_agent_id
        else:
            # User skipped - return None values
            return None, None
