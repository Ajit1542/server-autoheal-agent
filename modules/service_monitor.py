import subprocess
import datetime
import os
import json

LOG_FILE = "logs/agent.log"
STATE_FILE = "logs/service_state.json"
MAX_RETRIES = 2


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")


def get_status(service):
    return subprocess.getoutput(f"systemctl is-active {service}").strip()


def restart(service):
    subprocess.run(["systemctl", "restart", service])


def get_rca(service):
    return subprocess.getoutput(f"journalctl -u {service} -n 20 --no-pager")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def reset_retry(state, service):
    state[service] = {"retries": 0}
    save_state(state)


def increment_retry(state, service):
    if service not in state:
        state[service] = {"retries": 0}
    state[service]["retries"] += 1
    save_state(state)
    return state[service]["retries"]


def create_alert(service, rca):
    alert_file = f"logs/{service}_ALERT.flag"
    with open(alert_file, "w") as f:
        f.write(f"{datetime.datetime.now()}\n")
        f.write("Service failed after retries\n\n")
        f.write(rca)
    log(f"ALERT CREATED for {service}")


def check_service(service):
    state = load_state()
    status = get_status(service)

    if status == "active":
        log(f"{service} active and running fine")
        reset_retry(state, service)
        return

    retries = state.get(service, {}).get("retries", 0)

    if retries >= MAX_RETRIES:
        log(f"{service} already retried {MAX_RETRIES} times. Skipping auto-fix.")
        return

    log(f"{service} DOWN. Attempting restart {retries+1}/{MAX_RETRIES}")
    restart(service)

    # Recheck status
    new_status = get_status(service)

    if new_status == "active":
        log(f"{service} restarted successfully")
        reset_retry(state, service)
    else:
        retries = increment_retry(state, service)
        log(f"{service} restart failed. Retry count: {retries}")

        if retries >= MAX_RETRIES:
            log(f"{service} failed after {MAX_RETRIES} retries → ESCALATE")
            rca = get_rca(service)
            log(f"RCA for {service}:\n{rca}")
            create_alert(service, rca)
def run():
    check_service("sssd")
    check_service("ntpd")
    check_service("chronyd")
