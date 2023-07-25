# Author: labs-dwcts
# Version: 0.9.9
# Python : 3.8.10
# Date: 2023-07-17
# Description: HPC NVIDIA GPU Monitoring Setup

import os
import subprocess
import logging
import argparse
import fileinput

def check_if_root():
    if not os.geteuid() == 0:
        raise PermissionError('This script must be run as root!')

def setup_logging():
    log_dir = "/var/log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_filename = 'hpc-monitor-install.log'
    log_filepath = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_filepath, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logging.getLogger().addHandler(console_handler)

def run_command(command):
    try:
        logging.info(f'Running: {command}')
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        logging.info(output.decode())
        return output.decode().strip()
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode().strip()
        logging.error(f'Error while running command "{command}": {error_message}')
        raise Exception(f'Failed to run command: {command}')

def check_nvidia_smi():
    try:
        return run_command('which nvidia-smi')
    except Exception as e:
        logging.warning(f'nvidia-smi not found: {e}')
        return False

def check_nvidia_gpu():
    try:
        output = run_command('lspci')
        if 'NVIDIA' in output:
            return True
        else:
            return False
    except Exception as e:
        logging.warning(f'Could not run lspci: {e}')
        return False

def install_packages(*packages):
    print("Installing packages...")
    run_command('sudo apt-get update')
    for package in packages:
        run_command(f'sudo apt-get install -y {package}')
    print("Packages installed.")

def download_nvidia_driver(version):
    print("Downloading NVIDIA driver...")
    run_command(f'wget https://us.download.nvidia.com/XFree86/Linux-x86_64/{version}/NVIDIA-Linux-x86_64-{version}.run')

def check_x_window():
    try:
        subprocess.check_output('xset -q', shell=True, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        return False

def install_nvidia_driver(version):
    print("Installing NVIDIA driver...")
    if check_x_window():
        run_command(f'sudo sh NVIDIA-Linux-x86_64-{version}.run --silent')
    else:
        run_command(f'sudo sh NVIDIA-Linux-x86_64-{version}.run --silent --no-x-check')
    print("NVIDIA driver installed.")

def configure_docker_repository():
    print("Configuring Docker repository...")
    commands = [
        'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
        'sudo apt-key fingerprint 0EBFCD88',
        'sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"',
        'sudo apt-get update'
    ]
    for command in commands:
        run_command(command)
    print("Docker repository configured.")

def configure_nvidia_repository():
    print("Configuring NVIDIA repository...")
    command = 'distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list'
    run_command(command)
    run_command('sudo apt-get update')
    print("NVIDIA repository configured.")

def restart_docker():
    print("Restarting Docker...")
    run_command('sudo systemctl restart docker')
    print("Docker restarted.")

def configure_nvidia_runtime():
    print("Configuring NVIDIA runtime...")
    commands = [
        'sudo mkdir -p /etc/systemd/system/docker.service.d',
        'sudo tee /etc/systemd/system/docker.service.d/override.conf <<EOF\n[Service]\nExecStart=\nExecStart=/usr/bin/dockerd --host=fd:// --add-runtime=nvidia=/usr/bin/nvidia-container-runtime\nEOF',
        'sudo systemctl daemon-reload',
        'sudo nvidia-ctk runtime configure --runtime=docker',
    ]
    for command in commands:
        run_command(command)
    print("NVIDIA runtime configured.")

def test_docker_nvidia_runtime():
    print("Testing Docker NVIDIA runtime...")
    run_command('sudo docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi')
    print("Docker NVIDIA runtime tested.")

def run_docker_compose():
    print("Running Docker Compose...")
    run_command('docker compose -f ./compose/docker-compose.yml up -d')
    print("Docker Compose run.")

def uninstall_containers():
    print("Uninstalling containers...")
    run_command('docker compose -f ./compose/docker-compose.yml down')
    print("Containers uninstalled.")

def complete_message():    
    print("\n----------------------------------------------------------------------\n")
    nvidia_smi_output = run_command('nvidia-smi')
    print(nvidia_smi_output)
    print("\n----------------------------------------------------------------------\n")
    print("Listing all Docker processes...")
    print("\n----------------------------------------------------------------------\n")
    docker_ps_output = run_command('docker ps -a')
    print(docker_ps_output)
    print("\n----------------------------------------------------------------------\n"
          "Add your user to the docker group.\n"
          "Run 'sudo usermod -aG docker $USER'\n"
          "Log out and log back in so that your group membership is re-evaluated.\n"
          "Run 'newgrp docker'\n"
          "----------------------------------------------------------------------\n\n"
          "----------------------------------------------------------------------\n"
          "Stress Test\n"
          "----------------------------------------------------------------------\n"
          "Multi-GPU CUDA stress test\n"
          "$ docker run --gpus all --rm oguzpastirmaci/gpu-burn 60\n"
          "----------------------------------------------------------------------\n"
          "CPU stress test\n"
          "$ stress --cpu `nproc` --vm `nproc` --vm-bytes 1GB --io `nproc` --hdd `nproc` --hdd-bytes 1GB --timeout 60s\n"
          "----------------------------------------------------------------------\n")

def check_tools(*tools):
    for tool in tools:
        try:
            run_command(f'which {tool}')
        except Exception as e:
            raise Exception(f"Required tool {tool} is not installed.")

def replace_ip_in_file(file_path, ip):
    with fileinput.FileInput(file_path, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace('localhost', ip), end='')

def replace_endpoint_in_env(file_path, ip):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if line.startswith('WA_PROMETHEUS_ENDPOINT'):
                file.write(f'WA_PROMETHEUS_ENDPOINT=http://{ip}:9090\n')
            elif line.startswith('GF_SERVER_ROOT_URL'):
                file.write(f'GF_SERVER_ROOT_URL=http://{ip}:3000\n')
            else:
                file.write(line)

def modify_grafana_container():
    print("Modifying Grafana container...")
    
    replacements = [
        ('AppTitle="Grafana"', 'AppTitle="DACOMSYSTEM"'),
        ('LoginTitle="Welcome to Grafana"', 'LoginTitle="Welcome to DACOMSYSTEM"'),
        ('[{target:"_blank",id:"documentation".*grafana_footer"}]', '[]'),
        ('({target:"_blank",id:"license",.*licenseUrl})', '()'),
        ('({target:"_blank",id:"version",.*CHANGELOG.md":void 0})', '()'),
        ('({target:"_blank",id:"updateVersion",.*grafana_footer"})', '()'),
        ('..createElement(....,{className:.,onClick:.,iconOnly:!0,icon:"rss","aria-label":"News"})', 'null'),
    ]
    
    for old, new in replacements:
        command = f'docker exec -it -u 0 grafana find /usr/share/grafana/public/build/ -name "*.js" -exec sed -i \'s|{old}|{new}|g\' {{}} \\;'
        run_command(command)
    
    print("Container modified.")

def main(server_ip, client_ip, driver_version, uninstall):
    try:
        check_if_root()
        setup_logging()
        check_tools('curl', 'wget', 'lspci')

        if uninstall:
            uninstall_containers()
            exit(0)

        if not check_nvidia_gpu():
            logging.error("No NVIDIA GPU detected. Exiting.")
            print("No NVIDIA GPU detected. Exiting.")
            exit(1)

        if server_ip:
            replace_ip_in_file('./compose/prometheus/prometheus.yml', server_ip)
            replace_ip_in_file('./compose/grafana/provisioning/datasources/prometheus.yml', server_ip)
            replace_endpoint_in_env('./compose/.env', server_ip)

        print("Starting setup...")
        install_packages('build-essential','stress')

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

        modify_grafana_container()
        print("Setup completed.")
        
        complete_message()

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print("An unexpected error occurred.")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to setup NVIDIA GPU for HPC')
    parser.add_argument('--driver-version', type=str, default='535.54.03', help='NVIDIA driver version (default: 535.54.03)')
    parser.add_argument('--server-ip', type=str, help='Server IP')
    parser.add_argument('--client-ip', type=str, help='Client IP')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall the containers')
    args = parser.parse_args()
    main(args.server_ip, args.client_ip, args.driver_version, args.uninstall)
