#!/usr/bin/env python
import subprocess
import sys
print("Starting AI Support Pro Dashboard...")
subprocess.run([sys.executable, "-m", "streamlit", "run", "app_pro_final.py", "--server.port", "8501"])

