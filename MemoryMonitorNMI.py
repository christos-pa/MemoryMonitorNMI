import psutil
import json
import socket
import time
import traceback
import logging
from PIL import Image
import pystray
from threading import Thread
import sys
import os

from logging.handlers import RotatingFileHandler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import ssl
from smtplib import SMTP, SMTP_SSL


# ------------------------------------------------------------
# Load config.json reliably (works for EXE or script)
# ------------------------------------------------------------
def load_config():
    try:
        # Always load config.json from the EXE/script directory
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        config_path = os.path.join(exe_dir, "config.json")

        with open(config_path, "r") as f:
            return json.load(f)

    except Exception as e:
        print("ERROR: Could not load config.json:", e)
        raise e


config = load_config()
monitor_cfg = config["monitor_settings"]
alert_cfg = config["alert_settings"]
email_cfg = config["email_settings"]
log_cfg = config["logging"]

THRESHOLD = monitor_cfg["threshold_percent"]
INTERVAL = monitor_cfg["check_interval_seconds"]
REQUIRED_MINUTES = monitor_cfg["required_duration_minutes"]

# Converts minutes to seconds for timer logic
REQUIRED_SECONDS = REQUIRED_MINUTES * 60


# ------------------------------------------------------------
# Logging Setup with Rotation
# ------------------------------------------------------------
log_folder = log_cfg["log_directory"]
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "MemoryMonitorNMI.log")

handler = RotatingFileHandler(
    log_file,
    maxBytes=log_cfg["max_log_size_mb"] * 1024 * 1024,
    backupCount=log_cfg["backup_log_files"]
)

logging.basicConfig(
    level=getattr(logging, log_cfg.get("log_level", "INFO")),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[handler]
)

logging.info("MemoryMonitorNMI started.")
logging.info(f"Threshold: {THRESHOLD}%, Duration: {REQUIRED_MINUTES} mins, Interval: {INTERVAL}s")


# ------------------------------------------------------------
# Email Sending Function (smart TLS/SSL with fallback)
# ------------------------------------------------------------
def send_email_alert(usage_percent, duration_minutes, top_processes):
    try:
        hostname = socket.gethostname()

        subject = email_cfg["email_subject"].replace("[HOSTNAME]", hostname)
        subject = subject.replace("[THRESHOLD]", str(THRESHOLD))

        body = email_cfg["email_prefix_text"] + "\n\n"
        body += f"Hostname: {hostname}\n"
        body += f"Virtual Memory Usage: {usage_percent}%\n"
        body += f"Threshold: {THRESHOLD}%\n"
        body += f"Duration Above Threshold: {duration_minutes} minutes\n"
        body += f"Timestamp: {datetime.now()}\n\n"

        if alert_cfg["include_top_processes"]:
            body += "Top Memory Processes:\n"
            for proc in top_processes:
                body += f" - {proc}\n"

        # Build email
        msg = MIMEMultipart()
        msg["From"] = email_cfg["email_from"]
        msg["To"] = ", ".join(email_cfg["email_to"])
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = email_cfg["smtp_server"]
        port = email_cfg["smtp_port"]
        username = email_cfg["smtp_username"]
        password = email_cfg["smtp_password"]

        # TLS/SSL context (secure)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # ------------------------------
        # 1) Try STARTTLS first (587)
        # ------------------------------
        try:
            smtp = SMTP(server, port, timeout=10)
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(username, password)
            smtp.sendmail(email_cfg["email_from"], email_cfg["email_to"], msg.as_string())
            smtp.quit()
            logging.info("ALERT SENT via STARTTLS.")
            return True

        except Exception as e1:
            logging.warning("STARTTLS failed, trying SSL...")
            logging.warning(str(e1))

        # ------------------------------
        # 2) Try SSL (465)
        # ------------------------------
        try:
            smtp = SMTP_SSL(server, 465, context=context, timeout=10)
            smtp.login(username, password)
            smtp.sendmail(email_cfg["email_from"], email_cfg["email_to"], msg.as_string())
            smtp.quit()
            logging.info("ALERT SENT via SSL.")
            return True

        except Exception as e2:
            logging.warning("SSL send failed:")
            logging.warning(str(e2))

        # ------------------------------
        # 3) Plain SMTP fallback (rare)
        # ------------------------------
        try:
            smtp = SMTP(server, 25, timeout=10)
            smtp.login(username, password)
            smtp.sendmail(email_cfg["email_from"], email_cfg["email_to"], msg.as_string())
            smtp.quit()
            logging.info("ALERT SENT via plain SMTP.")
            return True

        except Exception as e3:
            logging.error("Plain SMTP failed:")
            logging.error(str(e3))

        return False

    except Exception:
        logging.error("ERROR sending email alert:")
        logging.error(traceback.format_exc())
        return False


# ------------------------------------------------------------
# Get Top Memory Processes
# ------------------------------------------------------------
def get_top_processes(limit):
    processes = []
    for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            mem = round(proc.info["memory_percent"], 2)
            processes.append((mem, proc.info["pid"], proc.info["name"]))
        except Exception:
            pass

    processes.sort(reverse=True, key=lambda x: x[0])
    return [f"{name} (PID {pid}) - {mem}%" for mem, pid, name in processes[:limit]]


# ------------------------------------------------------------
# Main Monitoring Loop
# ------------------------------------------------------------
def monitor_memory():
    above_timer = 0       # Seconds above threshold
    alert_sent = False

    while True:
        try:
            mem = psutil.virtual_memory()
            usage = mem.percent

            logging.info(f"Memory usage: {usage}% (Threshold: {THRESHOLD}%)")

            if usage >= THRESHOLD:
                above_timer += INTERVAL
                logging.info(f"Above threshold for {above_timer}/{REQUIRED_SECONDS} seconds")

                if above_timer >= REQUIRED_SECONDS and not alert_sent:
                    top_procs = get_top_processes(alert_cfg["max_processes"])
                    duration_mins = above_timer // 60

                    if alert_cfg["enable_email_alerts"]:
                        if send_email_alert(usage, duration_mins, top_procs):
                            alert_sent = True
            else:
                if above_timer > 0:
                    logging.info("Memory below threshold. Timer reset.")
                above_timer = 0

                if alert_sent:
                    logging.info("Memory normal again. Alert state reset.")
                alert_sent = False

            time.sleep(INTERVAL)

        except Exception:
            logging.error("Unexpected error:")
            logging.error(traceback.format_exc())
            time.sleep(INTERVAL)


# ------------------------------------------------------------
# System Tray Icon
# ------------------------------------------------------------
def create_tray_icon():
    try:
        image = Image.open("memorymonitor_icon.ico")

        def on_exit(icon, item):
            logging.info("Tray icon exit clicked. Shutting down...")
            icon.stop()
            sys.exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("Exit MemoryMonitorNMI", on_exit)
        )

        icon = pystray.Icon("MemoryMonitorNMI", image, "MemoryMonitorNMI", menu)
        icon.run()

    except Exception:
        logging.error("Tray icon error:")
        logging.error(traceback.format_exc())


# ------------------------------------------------------------
# Start Monitoring
# ------------------------------------------------------------
if __name__ == "__main__":
    monitor_thread = Thread(target=monitor_memory, daemon=True)
    monitor_thread.start()

    create_tray_icon()
