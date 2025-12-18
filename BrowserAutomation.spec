# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Browser Automation Desktop App
Creates macOS .app bundle with all dependencies
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all data files and submodules for key packages
nova_act_datas, nova_act_binaries, nova_act_hiddenimports = collect_all('nova_act')
flask_datas, flask_binaries, flask_hiddenimports = collect_all('flask')
flask_cors_datas, flask_cors_binaries, flask_cors_hiddenimports = collect_all('flask_cors')

# Additional hidden imports for modules that PyInstaller might miss
hiddenimports = [
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'PyQt6.sip',
    # Flask/Werkzeug modules
    'werkzeug.serving',
    'flask.templating',
    # Auto browser modules (including new config modules)
    'auto_browser.main',
    'auto_browser.web_ui',
    'auto_browser.desktop_app',
    'auto_browser.config_manager',
    'auto_browser.setup_dialog',
] + nova_act_hiddenimports + flask_hiddenimports + flask_cors_hiddenimports

a = Analysis(
    ['run_desktop_ui.py'],
    pathex=['src'],  # Add src directory so PyInstaller can find auto_browser
    binaries=nova_act_binaries + flask_binaries + flask_cors_binaries,
    datas=nova_act_datas + flask_datas + flask_cors_datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/rthook_pyqt6.py'],
    excludes=[
        # Size optimization - exclude unnecessary packages
        'matplotlib',
        'pandas',
        'tkinter',
        'jupyter',
        'IPython',
        # Legacy voice support not used in desktop app
        'speech_recognition',
        'pyaudio',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BrowserAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Keep symbols for debugging
    upx=True,  # Enable compression
    console=False,  # No console window on macOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BrowserAutomation',
)

app = BUNDLE(
    coll,
    name='BrowserAutomation.app',
    icon='resources/BrowserAutomation.icns',
    bundle_identifier='com.browserautomation.desktop',
    version='0.1.1',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSMicrophoneUsageDescription': 'This app needs microphone access for voice control features.',
        'NSCameraUsageDescription': 'This app may need camera access for certain automation tasks.',
        'LSMinimumSystemVersion': '10.15.0',
        'CFBundleDisplayName': 'Browser Automation',
        'CFBundleName': 'BrowserAutomation',
        'CFBundleShortVersionString': '0.1.1',
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True  # Allow localhost connections
        }
    },
)
