import subprocess
import datetime

LOG_FILE = "logs/agent.log"


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")


def get_fstab_mounts():
    mounts = []
    with open("/etc/fstab") as f:
        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue
            parts = line.split()
            if len(parts) > 1:
                mounts.append((parts[1], line))
    return mounts


def get_current_mounts():
    output = subprocess.getoutput("cat /proc/mounts")
    current = []
    for line in output.split("\n"):
        parts = line.split()
        if len(parts) > 1:
            current.append(parts[1])
    return current


def get_mount_type(fstab_line):
    if "nfs" in fstab_line:
        return "nfs"
    if "cifs" in fstab_line:
        return "cifs"
    return "local"


def run():
    fstab_mounts = get_fstab_mounts()
    current_mounts = get_current_mounts()

    for mount_point, line in fstab_mounts:
        if mount_point not in current_mounts:
            log(f"{mount_point} in fstab but NOT mounted")

            # Try auto mount
            subprocess.run(["mount", mount_point])

            # Recheck
            current_mounts = get_current_mounts()
            if mount_point in current_mounts:
                log(f"{mount_point} mounted successfully")
                continue

            mtype = get_mount_type(line)
            log(f"{mount_point} still not mounted. Type: {mtype}")

            if mtype == "nfs":
                log(f"{mount_point} is NFS → escalate to L3")

            elif mtype == "cifs":
                log(f"{mount_point} is CIFS → needs customer validation")

            else:
                log(f"{mount_point} is local mount → needs manual check")

    # Check mounts present but not in fstab
    for mount in current_mounts:
        found = any(mount == f[0] for f in fstab_mounts)
        if not found:
            log(f"{mount} mounted but not in fstab → customer validation needed")
