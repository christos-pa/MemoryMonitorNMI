# MemoryMonitorNMI

A lightweight Windows background memory-usage monitor that runs silently with a tray icon, checks system memory at configurable intervals, and sends automated email alerts when usage stays above a defined threshold.  
Designed for unattended systems, kiosks, and remote Windows environments.

---

## 🚀 Features

- ✔ **Real-time memory monitoring**  
- ✔ **Threshold alerts** (e.g., above 90% for 30 minutes)  
- ✔ **Email notifications** via SMTP  
- ✔ **System tray icon** (running silently in the background)  
- ✔ **Automatic startup** via `INSTALL.bat`  
- ✔ **Full configuration via `config.json`**  
- ✔ **Optional logging** with rotation  
- ✔ **Included EXE for easy deployment**  
- ✔ Suitable for **kiosks, terminals, remote PCs, and production environments**

---

## 📂 Project Structure

MemoryMonitorNMI/
│
├── MemoryMonitorNMI.exe # Compiled executable (ready to run)
├── MemoryMonitorNMI.py # Main source script
├── INSTALL.bat # Installs + autostarts the monitor
├── UNINSTALL.bat # Removes autostart + files
├── config.json # Editable configuration file
├── memorymonitor_icon.ico # Tray icon
├── readme.pdf # PDF usage documentation
├── LICENSE # MIT License
└── README.md # This file


---

## ⚙️ Configuration (`config.json`)

This tool is fully configurable using a simple JSON file.

> **IMPORTANT:**  
> For security, replace the template email/password with your own secure credentials.

Example configuration:

```json
{
  "monitor_settings": {
    "check_interval_seconds": 60,
    "threshold_percent": 90,
    "required_duration_minutes": 30
  },
  "alert_settings": {
    "enable_email_alerts": true,
    "send_once_per_episode": true,
    "include_top_processes": true,
    "max_processes": 5
  },
  "email_settings": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": true,
    "smtp_username": "your_email_here@gmail.com",
    "smtp_password": "YOUR_APP_PASSWORD_HERE",
    "email_from": "your_email_here@gmail.com",
    "email_to": ["recipient@example.com"],
    "email_subject": "NMI Memory Alert - [HOSTNAME] Above 90%",
    "email_prefix_text": "This is an automated memory alert from MemoryMonitorNMI."
  },
  "logging": {
    "log_enabled": true,
    "log_directory": "logs",
    "log_level": "INFO",
    "max_log_size_mb": 5,
    "backup_log_files": 3
  }
}

```

---


## 🛠 Installation

### 1️⃣ Copy the folder to the target PC
Place it anywhere, e.g.:

C:\MemoryMonitorNMI\

### 2️⃣ Run the installer
Right-click → Run as administrator:

INSTALL.bat

This will:

- copy files  
- configure auto-start on Windows boot  
- launch the monitor  

### 3️⃣ Done
The tool will now run automatically on every reboot.

---

## ❌ Uninstalling

Run:

UNINSTALL.bat

This removes the scheduled task and the program directory.

---

## 📧 Alerts

When memory stays above the configured threshold (e.g., 90%) for the configured duration (e.g., 30 minutes), the monitor sends an email containing:

- System name  
- Memory usage  
- Uptime  
- Optional top processes  
- Timestamp  

---

## 🖥 Use Cases

- Windows kiosk machines  
- Car park payment terminals  
- NMI / S&B industrial terminals  
- Remote Windows PCs  
- Monitoring systems with restricted GUI access  
- Automated IT alerting  

---

## 📝 License

This project is licensed under the MIT License.  
You are free to use, modify, and distribute it.

---

## 🤝 Contributing

Pull requests are welcome.  
For major changes, please open an issue first to discuss the proposal.

---

## ⭐ Support the Project

If you find this useful, please consider starring the repo! ⭐
