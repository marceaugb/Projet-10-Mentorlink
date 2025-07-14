import subprocess
import time

SERVICE_NAME = "web"
MIN_REPLICAS = 1
MAX_REPLICAS = 5
SCALE_UP_THRESHOLD = 40.0  # % CPU
SCALE_DOWN_THRESHOLD = 10.0  # % CPU
CHECK_INTERVAL = 20  # seconds

def get_web_containers():
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={SERVICE_NAME}", "--format", "{{.Names}}"],
        stdout=subprocess.PIPE, text=True
    )
    return result.stdout.strip().splitlines()

def get_cpu_usage(container):
    result = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{.CPUPerc}}", container],
        stdout=subprocess.PIPE, text=True
    )
    try:
        value = result.stdout.strip().replace('%','')
        return float(value)
    except Exception:
        return 0.0

def get_current_replicas():
    containers = get_web_containers()
    return len(containers)

def scale_to(n):
    print(f"Scaling {SERVICE_NAME} to {n} replicas...")
    subprocess.run(
        ["docker", "compose", "up", "-d", "--scale", f"{SERVICE_NAME}={n}"]
    )
    print("Restarting nginx to update backend list...")
    subprocess.run(
        ["docker", "compose", "restart", "nginx"]
    )


def main():
    while True:
        containers = get_web_containers()
        if not containers:
            print("No web containers found. Waiting...")
            time.sleep(CHECK_INTERVAL)
            continue

        cpu_usages = [get_cpu_usage(c) for c in containers]
        avg_cpu = sum(cpu_usages) / len(cpu_usages)
        replicas = len(containers)
        print(f"Current replicas: {replicas}, Average CPU: {avg_cpu:.2f}%")

        if avg_cpu > SCALE_UP_THRESHOLD and replicas < MAX_REPLICAS:
            scale_to(replicas + 1)
        elif avg_cpu < SCALE_DOWN_THRESHOLD and replicas > MIN_REPLICAS:
            scale_to(replicas - 1)
        else:
            print("No scaling action needed.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
