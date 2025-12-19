#!/bin/bash
# Browser Automation Launcher

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate nova

# Run the application
cd "$DIR"
python run_desktop_ui.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo "Press any key to exit..."
    read -n 1
fi
