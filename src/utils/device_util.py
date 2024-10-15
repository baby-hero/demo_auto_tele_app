import re
import subprocess
import time

from src.configs.common_config import GENYMOTION_PATH
from src.utils.log_util import logger


def get_vms():
    """
    Get all virtual machines running on Genymotion.

    Returns:
        list: A list of tuples, each containing the VM name and its associated UUID.
        Sample: [('device_name', "uid")]
    """
    try:
        output = subprocess.check_output(["VBoxManage", "list", "vms", "-s"]).decode(
            "utf-8"
        )
        vms = re.findall(r'"([^"]+)"\s+\{([^\}]+)\}', output)
        return vms
    except subprocess.CalledProcessError as e:
        logger.error("Get vms", e)
        return []


def start_vm(vm_name, vn_id, wait_seconds=60):
    """
    player Options:
        -h, --help                       Displays help on commandline options.
        --help-all                       Displays help including Qt specific options.
        -v, --version                    Displays version information.
        -n, --vm-name <name_or_uuid>     Device to start.
        --no-update-check                Skip update checks.
        -p, --from-plugin <plugin_name>  Started from plugin.
        -i, --ide <ide_name>             Started from IDE.
        -r, --referer <referer_name>     Started from referer
        -s, --no-popup                   Do not show any popups.
        -x, --poweroff                   Stop a running device.
        -a, --startadb                   Connect ADB.
        -z, --stopadb                    Disconnect ADB.
        --log-filter-rules <rules>       Log filter rules.
        --resume                         Resume latest snapshot.
    """
    try:
        logger.info(f"Starting vm: {vm_name}")
        subprocess.Popen(
            [
                f"{GENYMOTION_PATH}/player",
                "--vm-name",
                vn_id,
                "--referer",
                "launchpad",
                "--resume",
            ],
        )
        logger.info(f"Successfully started the VM: {vm_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start the VM: {vm_name}", e)
    except Exception as e:
        logger.error(f"An error occurred when start vm: {vm_name}", e)


def stop_vm(vm_name, vn_id, wait_seconds=60):
    """
    player Options:
        -h, --help                       Displays help on commandline options.
        --help-all                       Displays help including Qt specific options.
        -v, --version                    Displays version information.
        -n, --vm-name <name_or_uuid>     Device to start.
        --no-update-check                Skip update checks.
        -p, --from-plugin <plugin_name>  Started from plugin.
        -i, --ide <ide_name>             Started from IDE.
        -r, --referer <referer_name>     Started from referer
        -s, --no-popup                   Do not show any popups.
        -x, --poweroff                   Stop a running device.
        -a, --startadb                   Connect ADB.
        -z, --stopadb                    Disconnect ADB.
        --log-filter-rules <rules>       Log filter rules.
        --resume                         Resume latest snapshot.
    """
    try:
        logger.info(f"Stopping vm: {vm_name}")
        subprocess.run(
            [
                f"{GENYMOTION_PATH}/player",
                "--vm-name",
                vn_id,
                "-x",
            ],
        )
        time.sleep(wait_seconds)  # wait for VM to fully stop
        logger.info(f"Successfully stopped the VM: {vm_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start the VM: {vm_name}", e)
    except Exception as e:
        logger.error(f"An error occurred when start vm: {vm_name}", e)


def main():
    vms = get_vms()

    if not vms:
        print("No VMs found.")
        return

    print("Available VMs:")
    for i, vm in enumerate(vms, start=1):
        print(f"{i}: {vm}")

    try:
        choice = int(input("Enter the number of the VM to manage: "))
        vm_name = vms[choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Exiting.")
        return

    action = input("Enter 'start' to start or 'stop' to stop the VM: ").strip().lower()

    if action == "start":
        start_vm(*vm_name)
    elif action == "stop":
        stop_vm(*vm_name)
    else:
        print("Invalid action. Please enter 'start' or 'stop'.")


if __name__ == "__main__":
    main()
