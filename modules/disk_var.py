import subprocess
import datetime

LOG_FILE = "logs/agent.log"
THRESHOLD = 85


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")


def get_var_usage():
    output = subprocess.getoutput("df -h /var | tail -1 | awk '{print $5}' | sed 's/%//'")
    return int(output)


def run():
    usage = get_var_usage()
    log(f"/var usage: {usage}%")

    if usage < THRESHOLD:
        log("/var usage normal")
        return

    log("/var usage HIGH. Starting cleanup...")

    # Check size of messages file
    size = subprocess.getoutput("du -h /var/log/messages | awk '{print $1}'")
    log(f"/var/log/messages size: {size}")

    # Run cleanup script
    subprocess.run(["bash", "fixes/clean_var.sh"])

    # Recheck usage
    new_usage = get_var_usage()
    log(f"/var usage after cleanup: {new_usage}%")

    if new_usage < THRESHOLD:
        log("/var cleanup successful")
        return True
    else:
        log("/var still high. Needs manual investigation")
        return False
