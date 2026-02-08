import subprocess
import datetime

LOG_FILE = "logs/agent.log"


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")


def get_status(service):
    return subprocess.getoutput(f"systemctl is-active {service}")


def restart(service):
    subprocess.run(["systemctl", "restart", service])


# ---------- SSSD CHECK ----------
def check_sssd():
    status = get_status("sssd")

    if status == "active":
        log("sssd is running нормально")
        return

    log("sssd is DOWN. Restarting...")
    restart("sssd")

    if get_status("sssd") == "active":
        log("sssd restarted successfully")
    else:
        log("sssd restart FAILED. Needs escalation")


# ---------- NTP CHECK ----------
def check_time_sync():
    ntp_status = get_status("ntpd")
    chrony_status = get_status("chronyd")

    if ntp_status == "active":
        log("ntpd is running нормально")
        return

    if chrony_status == "active":
        log("chronyd is running нормально")
        return

    log("Both ntpd & chronyd are DOWN. Attempting recovery...")

    # Try chronyd first
    restart("chronyd")

    if get_status("chronyd") == "active":
        log("chronyd restarted successfully")
        return

    # Try ntpd
    restart("ntpd")

    if get_status("ntpd") == "active":
        log("ntpd restarted successfully")
    else:
        log("Time sync recovery FAILED. Needs escalation")


def run():
    check_sssd()
    check_time_sync()
