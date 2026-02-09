import subprocess
import datetime

LOG_FILE = "logs/agent.log"

#store the logs into log file
def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")

#service status function
def get_status(service):
    return subprocess.getoutput(f"systemctl is-active {service}")

#service restart fuction
def restart(service):
    subprocess.run(["systemctl", "restart", service])


# ---------- SSSD CHECK ----------
def check_sssd():
    status = get_status("sssd")

    if status == "active":
        log("sssd service is active and running fine")
        return

    log("sssd service is DOWN. Restarting...")
    restart("sssd")

    if get_status("sssd") == "active":
        log("sssd restarted successfully")
        return True
    else:
        log("sssd restart FAILED. Needs escalation")
        return False


# ---------- NTP CHECK ----------
def check_time_sync():
    # ntp_status = get_status("ntpd")
    chrony_status = get_status("chronyd")

    # if ntp_status == "active":
    #     log("ntpd service is active and running fine")
    #     return 

    if chrony_status == "active":
        log("chronyd service is active and running fine")
        return

    log("chronyd service is DOWN. Attempting recovery...")

    # Try chronyd first
    restart("chronyd")

    if get_status("chronyd") == "active":
        log("chronyd service restarted successfully")
        return True
    else:
        log("Time sync recovery FAILED. Needs escalation")
        return False
    # # Try ntpd
    # restart("ntpd")

    # if get_status("ntpd") == "active":
    #     log("ntpd restarted successfully")
    #     return True
    


def run():

    sssd_service=check_sssd()
    time_sync_Service=check_time_sync()
    if (sssd_service and time_sync_Service) == True:
        return True
    else:
        return False
    
