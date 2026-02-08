from modules import (
    service_monitor,
    disk_var,
    stale_mount,
    host_monitor,
    fstab_check
)

import datetime

def log(message):
    with open("logs/agent.log", "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")

if __name__ == "__main__":
    log("===== Agent Started =====")

    service_monitor.run()
    disk_var.run()
    stale_mount.run()
    host_monitor.run()
    fstab_check.run()
    
    log("===== Agent Finished =====\n")


