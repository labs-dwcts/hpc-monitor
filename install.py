# Author: labs-dwcts
# Version: 0.9.8
# Date: 2023-07-17
# Description: HPC NVIDIA GPU single node monitor

import os
import subprocess
import logging
import datetime


def check_if_root():
    if not os.geteuid() == 0:
        raise PermissionError('This script must be run as root!')


def setup_logging():
    # Set up log directory
    log_dir = "/var/log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set log file name
    log_filename = 'hpc-monitor-install.log'
    log_filepath = os.path.join(log_dir, log_filename)

    # Set up logging
    logging.basicConfig(filename=log_filepath, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logging.getLogger().addHandler(console_handler)


def run_command(command):
    """Run shell command and log output."""
    try:
        logging.info(f'Running: {command}')
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        logging.info(output.decode())
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        logging.error(f'Error: {e.output.decode()}')
        raise Exception(f'Failed to run command: {command}')


def check_nvidia_smi():
    """Check if the 'nvidia-smi' command is available."""
    try:
        return run_command('which nvidia-smi')
    except Exception as e:
        logging.warning(f'nvidia-smi not found: {e}')
        return False


def install_packages(*packages):
    run_command('sudo apt-get update')
    for package in packages:
        run_command(f'sudo apt-get install -y {package}')


def download_nvidia_driver(version):
    run_command(f'wget https://us.download.nvidia.com/XFree86/Linux-x86_64/{version}/NVIDIA-Linux-x86_64-{version}.run')


def check_x_window():
    """Check if the X Window System is running."""
    try:
        subprocess.check_output('xset -q', shell=True, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        return False


def install_nvidia_driver(version):
    """Install the NVIDIA driver."""
    if check_x_window():
        run_command(f'sudo sh NVIDIA-Linux-x86_64-{version}.run --silent')
    else:
        run_command(f'sudo sh NVIDIA-Linux-x86_64-{version}.run --silent --no-x-check')



def configure_docker_repository():
    commands = [
        'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
        'sudo apt-key fingerprint 0EBFCD88',
        'sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"',
        'sudo apt-get update'
    ]
    for command in commands:
        run_command(command)


def configure_nvidia_repository():
    command = 'distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list'
    run_command(command)
    run_command('sudo apt-get update')


def restart_docker():
    run_command('sudo systemctl restart docker')


def configure_nvidia_runtime():
    commands = [
        'sudo mkdir -p /etc/systemd/system/docker.service.d',
        'sudo tee /etc/systemd/system/docker.service.d/override.conf <<EOF\n[Service]\nExecStart=\nExecStart=/usr/bin/dockerd --host=fd:// --add-runtime=nvidia=/usr/bin/nvidia-container-runtime\nEOF',
        'sudo systemctl daemon-reload',
        'sudo nvidia-ctk runtime configure --runtime=docker',
    ]
    for command in commands:
        run_command(command)


def test_docker_nvidia_runtime():
    run_command('sudo docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu20.04 nvidia-smi')


def run_docker_compose():
    os.chdir("./compose")
    run_command('docker compose up -d')


def complete_message():
    run_command('docker ps -a')
    print("\n------------------------------------\n"
          "Add your user to the docker group.\n"
          "Run 'sudo usermod -aG docker $USER'\n"
          "Log out and log back in so that your group membership is re-evaluated.\n"
          "Run 'newgrp docker'\n"
          "------------------------------------\n")


def main():
    try:
        check_if_root()
        setup_logging()

        install_packages('build-essential')

        driver_version = '535.54.03'
        if not check_nvidia_smi():
            download_nvidia_driver(driver_version)
            install_nvidia_driver(driver_version)

        install_packages('apt-transport-https', 'ca-certificates', 'curl', 'gnupg-agent', 'software-properties-common')
        configure_docker_repository()
        install_packages('docker-ce', 'docker-ce-cli', 'containerd.io')

        configure_nvidia_repository()
        install_packages('nvidia-container-toolkit')
        restart_docker()

        configure_nvidia_runtime()
        restart_docker()

        test_docker_nvidia_runtime()
        run_docker_compose()

        complete_message()

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print("An unexpected error occurred.")
        exit(1)


if __name__ == "__main__":
    main()
