"""
PyInstaller runtime hook for PyQt6 WebEngine.
Sets up Qt library paths before Qt initializes.
"""
import os
import sys

# Only run in frozen (packaged) mode
if getattr(sys, 'frozen', False):
    # Get the bundle directory
    if sys.platform == 'darwin':
        # On macOS, need to set Qt plugin and library paths
        bundle_dir = os.path.dirname(sys.executable)

        # Set Qt plugin path to find platform plugins
        qt_plugins_dir = os.path.join(bundle_dir, '..', 'Frameworks', 'PyQt6', 'Qt6', 'plugins')
        if os.path.exists(qt_plugins_dir):
            os.environ['QT_PLUGIN_PATH'] = os.path.abspath(qt_plugins_dir)

        # Set Qt library path
        qt_lib_dir = os.path.join(bundle_dir, '..', 'Frameworks', 'PyQt6', 'Qt6', 'lib')
        if os.path.exists(qt_lib_dir):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.abspath(qt_plugins_dir)
