# **HPC NVIDIA GPU Monitoring Setup**

고성능 컴퓨팅(High-Performance Computing, HPC) 환경에서 NVIDIA GPU를 사용하고 모니터링하기 위한 도구 입니다.

## **설치 요구사항**

- NVIDIA GPU가 설치된 Ubuntu 시스템
- **`curl`**, **`wget`** 등의 필수 도구가 설치된 Ubuntu 20.04 시스템
- 관리자 권한

## **사용 방법**

1. 이 저장소를 복제 합니다.

```
git clone https://github.com/your_username/hpc-monitor.git
```

2. **`install.py`** 스크립트를 실행합니다.
아래 옵션을 제공 합니다.
```
install.py [-h]
           [--driver-version DRIVER_VERSION]
           [--server-ip SERVER_IP]
           [--client-ip CLIENT_IP]
           [--uninstall]
```

```
cd hpc-monitor
```

설치 예제)

```
sudo python install.py --driver-version 535.54.03 --server-ip YOUR_SERVER_IP
```

- `YOUR_SERVER_IP`에는 실제 서버의 IP 주소를 입력 합니다.

웹브라우저에서 **`http://your_server_ip:3000`** 열어서 대시보드를 확인할 수 있습니다.

- 초기 ID와 비밀번호는 *`admin`*/*`admin`* 입니다.