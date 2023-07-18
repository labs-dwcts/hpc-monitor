# **HPC NVIDIA GPU Monitoring Setup**

이 프로젝트는 고성능 컴퓨팅(High-Performance Computing, HPC) 환경에서 NVIDIA GPU를 사용하고 모니터링하기 위한 도구를 설정하는 스크립트를 제공 합니다. 스크립트는 필요한 패키지를 설치하고, NVIDIA GPOU 드라이버가 없을시에만 드라이버를 설치 합니다.
그리고 Docker와 NVIDIA 리포지토리를 설정하며, NVIDIA 런타임을 구성하고, Docker Compose를 실행 합니다.

## **설치 요구사항**

- NVIDIA GPU가 설치된 Ubuntu 시스템
- **`curl`**, **`wget`**, **`lspci`** 등의 필수 도구가 설치된 시스템
- 관리자 권한

## **사용 방법**

1. 이 프로젝트를 복제 합니다.

```
git clone https://github.com/your_username/hpc-monitor.git
```

2. **`install.py`** 스크립트를 실행합니다.
아래 옵션을 제공 합니다.
usage: install.py [-h] [--driver-version DRIVER_VERSION] [--server-ip SERVER_IP] [--client-ip CLIENT_IP]

```
cd hpc-monitor
```

```
sudo python3 install.py --driver-version 535.54.03 --server-ip YOUR_SERVER_IP
```

**`your_server_ip`**에는 실제 서버의 IP 주소를 입력합니다. 이 옵션을 사용하면 설정 파일 내의 'localhost'가 해당 IP 주소로 변경 됩니다.

스크립트 실행이 완료되면, Docker 프로세스 목록과 추가로 수행해야 할 단계들을 안내하는 메시지가 출력됩니다.

웹브라우져에서 **`http://your_server_ip:3000`** 열어서 Grafana 대시보드를 확인할 수 있습니다.
초기 ID와 비밀번호는 **`admin`**/**`dwcts`** 입니다.