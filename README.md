# SysInfo API

## 1. Application Description

SysInfo API is a small FastAPI web application that exposes real information about the Linux server it runs on: hostname, uptime, CPU, memory, disk, network interfaces and the top processes. It reads data from the operating system using `psutil`, so it works as a learning tool for Linux and DevOps.

The app is deployed manually on CentOS 10 without Docker or Kubernetes:

    Client -> Nginx (port 80) -> Uvicorn (127.0.0.1:8000) -> FastAPI -> Linux
                                   ^ managed by systemd

## 2. API Endpoints

| Endpoint | Description |
|---|---|
| `/health` | Liveness check |
| `/system/info` | Hostname, platform, architecture, uptime |
| `/system/cpu` | CPU cores, usage, frequency |
| `/system/memory` | RAM usage |
| `/system/disk` | Root partition usage |
| `/system/network` | Interfaces, IPs, traffic counters |
| `/system/processes` | Top 5 processes by CPU |

Example commands:

    curl http://localhost/health
    curl http://localhost/system/info
    curl http://localhost/system/cpu
    curl http://localhost/system/memory
    curl http://localhost/system/disk
    curl http://localhost/system/network
    curl http://localhost/system/processes

Interactive Swagger UI: `http://<vm-ip>/docs`

## 3. Deployment Instructions

**Phase 1 - Git setup:** install git, set identity, create the project structure and make the first commit.

**Phase 2 - Python environment:** install python3 and pip, create a virtual environment (`python3 -m venv venv`), activate it, run `pip install -r requirements.txt`, and test with `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

**Phase 3 - systemd service:** create `/etc/systemd/system/sysinfo-api.service`, then run `daemon-reload`, `enable` and `start`. Test auto-restart by killing uvicorn. On CentOS the venv binaries must be labelled for SELinux:

    sudo semanage fcontext -a -t bin_t "/home/fahad/sysinfo-api/venv/bin(/.*)?"
    sudo restorecon -Rv /home/fahad/sysinfo-api/venv/bin

**Phase 4 - Nginx reverse proxy:** install nginx, create `/etc/nginx/conf.d/sysinfo-api.conf`, run `nginx -t`, enable and start it. Open the firewall and allow Nginx to reach Uvicorn through SELinux:

    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --reload
    sudo setsebool -P httpd_can_network_connect 1

If port 80 is already in use (for example by Apache `httpd`), stop and disable the other service first.

**Phase 5 - Bash script + cron:** `scripts/archive_logs.sh` compresses the Nginx access log, clears it, and deletes archives older than 30 days. It is scheduled in root's crontab:

    0 2 * * 0 /home/fahad/sysinfo-api/scripts/archive_logs.sh

This means every Sunday at 2:00 AM.

## 4. Configuration Files

- **sysinfo-api.service** (`/etc/systemd/system/`): tells systemd how to run Uvicorn as a background service as user `fahad`, bound to `127.0.0.1:8000`, with `Restart=on-failure` so it restarts after a crash and starts automatically on boot.
- **sysinfo-api.conf** (`/etc/nginx/conf.d/`): Nginx virtual host that listens on port 80 and proxies all requests to `http://127.0.0.1:8000`, with its own access and error logs.

## 5. Log Locations

Application logs (systemd journal):

    sudo journalctl -u sysinfo-api
    sudo journalctl -u sysinfo-api -f

Application log file: `logs/app.log`

Nginx logs:

    /var/log/nginx/sysinfo-api.access.log
    /var/log/nginx/sysinfo-api.error.log

Archive script:

    /var/log/nginx/archives/
    /var/log/archive_logs.log
