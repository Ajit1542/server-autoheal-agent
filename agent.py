from modules import (
    service_monitor,
    disk_var,
    stale_mount,
    host_monitor,
    fstab_check
)
import datetime
METRICS_FILE = "metrics.prom"
metrics = {
    "autoheal_service_failed": 0,
    "autoheal_disk_var_failed": 0,
    "autoheal_stale_failed": 0,
    "autoheal_fstab_failed": 0
}
def write_metrics():
    with open(METRICS_FILE, "w") as f:
        for k, v in metrics.items():
            f.write(f"{k} {v}\n")
def log(message):
    with open("logs/agent.log", "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")

if __name__ == "__main__":
    log("===== Agent Started =====")

    service_monitor.run()
    disk_var.run()
    stale_mount.run()
    # host_monitor.run()
    fstab_check.run()
    
    if not disk_var.run():
        metrics["autoheal_disk_var_failed"]=1
    if not service_monitor.run():
        metrics["autoheal_service_failed"]=1
    if not fstab_check.run():
        metrics["autoheal_fstab_failed"]=1
    if not stale_mount.run():
        metrics["autoheal_stale_failed"]=1
    
    log("===== Agent Finished =====\n")

    write_metrics()


