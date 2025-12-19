"""
PyInstaller hook for nova_act package
Ensures all submodules and dependencies are included in the bundle
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_dynamic_libs

datas, binaries, hiddenimports = collect_all('nova_act')

# Ensure all submodules are included
hiddenimports += collect_submodules('nova_act')

# Include any browser-related binaries
binaries += collect_dynamic_libs('nova_act')
