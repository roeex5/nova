"""
PyInstaller hook for auto_browser package
Ensures all auto_browser submodules are included
"""

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('auto_browser')
