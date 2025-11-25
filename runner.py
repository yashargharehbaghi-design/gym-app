import os
import subprocess

# ست کردن مسیرهای موقت تا لیارا بتونه فایل بنویسه
os.environ["HOME"] = "/tmp"
os.environ["MPLCONFIGDIR"] = "/tmp"

# اجرای استریم‌لیت روی پورت لیارا
subprocess.run(
    [
        "streamlit",
        "run",
        "app.py",
        "--server.port=8000",
        "--server.address=0.0.0.0",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
)
