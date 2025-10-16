import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def open_output_folder(subfolder_name=None):
    """'output' 또는 'output/[subfolder_name]' 폴더를 엽니다."""
    if subfolder_name:
        target_dir = os.path.join(BASE_DIR, 'output', subfolder_name)
    else:
        target_dir = os.path.join(BASE_DIR, 'output')

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if sys.platform == "win32":
        os.startfile(os.path.realpath(target_dir))
    elif sys.platform == "darwin": # macOS
        subprocess.Popen(["open", target_dir])
    else: # Linux
        subprocess.Popen(["xdg-open", target_dir])