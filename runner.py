import os
import subprocess
import sys

# 1. تغییر مسیر خانه به پوشه موقت (که اجازه نوشتن دارد)
os.environ["HOME"] = "/tmp"
os.environ["MPLCONFIGDIR"] = "/tmp"

# 2. دستور اجرای استریم‌لیت
command = [
    sys.executable, "-m", "streamlit", "run", "app.py",
    "--server.port=8000",
    "--server.address=0.0.0.0",
    "--server.enableCORS=false",
    "--server.enableXsrfProtection=false",
]

# 3. اجرای برنامه
subprocess.run(command)
