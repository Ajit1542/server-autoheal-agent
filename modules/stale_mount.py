import subprocess
import datetime

LOG_FILE = "logs/agent.log"


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")


def get_stale_mounts():
    # This command tries to detect hung mounts
    output = subprocess.getoutput("timeout 5 df -h 2>&1")

    stale = []
    for line in output.split("\n"):
        if "Stale file handle" in line or "cannot access" in line:
            parts = line.split()
            if len(parts) > 0:
                stale.append(parts[-1])
    return stale


def get_mount_type(mount_point):
    fstab = subprocess.getoutput("cat /etc/fstab")
    for line in fstab.split("\n"):
        if mount_point in line:
            if "nfs" in line:
                return "nfs"
            if "cifs" in line:
                return "cifs"
    return "unknown"


def get_server_from_mount(mount_point):
    fstab = subprocess.getoutput("cat /etc/fstab")
    for line in fstab.split("\n"):
        if mount_point in line:
            return line.split()[0]
    return None


def ping_server(server):
    result = subprocess.getoutput(f"ping -c 2 {server}")
    return "0% packet loss" in result


def remount(mount_point):
    subprocess.run(["umount", "-l", mount_point])
    subprocess.run(["mount", mount_point])


def run():
    stale_mounts = get_stale_mounts()

    if not stale_mounts:
        log("No stale mounts found")
        return

    for mount in stale_mounts:
        log(f"Stale mount detected: {mount}")

        mtype = get_mount_type(mount)
        log(f"Mount type: {mtype}")

        if mtype == "nfs":
            log(f"{mount} is NFS → escalate to L3")
            continue

        if mtype == "cifs":
            server = get_server_from_mount(mount)
            if not server:
                log(f"Server not found for {mount}")
                continue

            server_host = server.split(":")[0].replace("//", "")
            log(f"Pinging CIFS server: {server_host}")

            if ping_server(server_host):
                log("Server reachable. Attempting remount...")
                remount(mount)
                log(f"Remount attempted for {mount}")
            else:
                log(f"Server unreachable → escalate ticket for {mount}")

        else:
            log(f"Unknown mount type for {mount}")
