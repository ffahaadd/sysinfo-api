import psutil
import socket
import platform
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


def get_uptime() -> str:
    """Calculate system uptime from boot time."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_delta = datetime.now() - boot_time
    hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


@router.get("/info")
def system_info():
    """
    Returns basic system information.
    Try: curl http://localhost:8000/system/info
    """
    return {
        "hostname":         socket.gethostname(),
        "platform":         platform.system(),
        "platform_version": platform.version(),
        "architecture":     platform.machine(),
        "uptime":           get_uptime(),
        "timestamp":        datetime.now().isoformat(),
    }


@router.get("/cpu")
def cpu_info():
    """
    Returns CPU usage statistics.
    Try: curl http://localhost:8000/system/cpu
    """
    return {
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_count_logical":  psutil.cpu_count(logical=True),
        "cpu_percent":        psutil.cpu_percent(interval=1),
        "cpu_freq_mhz":       psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
    }


@router.get("/memory")
def memory_info():
    """
    Returns RAM usage.
    Try: curl http://localhost:8000/system/memory
    """
    mem = psutil.virtual_memory()
    return {
        "total_gb":     round(mem.total / (1024 ** 3), 2),
        "used_gb":      round(mem.used  / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "percent_used": mem.percent,
    }


@router.get("/disk")
def disk_info():
    """
    Returns disk usage for the root partition.
    Try: curl http://localhost:8000/system/disk
    """
    disk = psutil.disk_usage("/")
    return {
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb":  round(disk.used  / (1024 ** 3), 2),
        "free_gb":  round(disk.free  / (1024 ** 3), 2),
        "percent_used": disk.percent,
    }


@router.get("/network")
def network_info():
    """
    Returns network interface statistics.
    Try: curl http://localhost:8000/system/network
    """
    net_io = psutil.net_io_counters()
    interfaces = []

    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == 2:  # AF_INET = IPv4
                interfaces.append({
                    "interface": iface,
                    "ip": addr.address
                })

    return {
        "interfaces":       interfaces,
        "bytes_sent_mb":    round(net_io.bytes_sent / (1024 ** 2), 2),
        "bytes_recv_mb":    round(net_io.bytes_recv / (1024 ** 2), 2),
        "packets_sent":     net_io.packets_sent,
        "packets_recv":     net_io.packets_recv,
    }


@router.get("/processes")
def top_processes():
    """
    Returns the top 5 CPU-consuming processes.
    Try: curl http://localhost:8000/system/processes
    """
    procs = []

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent"]
    ):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    top5 = sorted(
        procs,
        key=lambda x: x["cpu_percent"] or 0,
        reverse=True
    )[:5]

    return {"top_processes_by_cpu": top5}
