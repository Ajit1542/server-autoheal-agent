import subprocess
import datetime

LOG_FILE = "logs/agent.log"


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")


def ping_host(host):
    result = subprocess.getoutput(f"ping -c 2 {host}")
    return "0% packet loss" in result


def get_uptime(host):
    return subprocess.getoutput(f"ssh -o ConnectTimeout=5 {host} uptime")


def get_last_reboot(host):
    return subprocess.getoutput(f"ssh -o ConnectTimeout=5 {host} who -b")


def run():
    try:
        with open("servers.txt") as f:
            servers = f.read().splitlines()
    except:
        log("servers.txt not found")
        return

    for host in servers:
        log(f"Checking host: {host}")

        if not ping_host(host):
            log(f"{host} is NOT reachable → Host Down alert valid")
            continue

        log(f"{host} reachable")

        # Check SSH
        uptime = get_uptime(host)
        if "load average" in uptime:
            log(f"{host} SSH accessible")
            log(f"Uptime: {uptime}")

            reboot = get_last_reboot(host)
            log(f"Last reboot info: {reboot}")
        else:
            log(f"{host} ping OK but SSH failed → Needs investigation")
