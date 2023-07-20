# **HPC NVIDIA GPU Monitoring Setup**

고성능 컴퓨팅(High-Performance Computing, HPC) 환경에서 NVIDIA GPU를 사용하고 모니터링하기 위한 도구 입니다.

## **설치 요구사항**

- NVIDIA GPU가 설치된 Ubuntu 시스템
- **`curl`**, **`wget`** 등의 필수 도구가 설치된 시스템
- 관리자 권한

## **사용 방법**

1. 이 저장소를 복제 합니다.

```bash
git clone https://github.com/your_username/hpc-monitor.git
```

설치전 이메일 알림이 필요하다면 /compose/.env 환경 설정을 열고 SMTP 서버, 이메일 주소, 비밀번호를 설정해야 합니다.

```yaml
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
GF_USERS_ALLOW_SIGN_UP=false

WA_PROMETHEUS_ENDPOINT=http://localhost:9090
GF_SERVER_ROOT_URL=http://localhost:3000
GF_SMTP_ENABLED=1
GF_SMTP_HOST=host:port # SMTP 서버
GF_SMTP_USER=yout@email # 이메일 주소
GF_SMTP_PASSWORD=yourpassword # 비밀번호
GF_SMTP_SKIP_VERIFY=1
```

**`install.py`** 스크립트는 다음과 같은 옵션을 제공 합니다.

```bash
install.py [-h]
           [--driver-version DRIVER_VERSION]
           [--server-ip SERVER_IP]
           [--client-ip CLIENT_IP]
           [--uninstall]
```

2. 설치를 시작 합니다.

```bash
cd hpc-monitor
```

설치 (예)

—driver-version을 지정하지 않으면 535.54.03 버전 (기본값) 으로 설치 됩니다.

`YOUR_SERVER_IP`에는 실제 서버의 IP 주소를 입력 합니다.

```bash
sudo python install.py --driver-version 535.54.03 --server-ip YOUR_SERVER_IP
```

3. 모니터 대시보드 접속

웹브라우저에서 **`http://your_server_ip:3000`** 열어서 대시보드를 확인할 수 있습니다.

- 초기 ID와 비밀번호는 **`admin`**/**`admin`** 입니다.
    - 초기 비밀번호를 사용할 경우 새 비밀번호를 입력해야 합니다.
    - 환경설정에서 비밀번호를 변경하였다면 변경된 비밀번호로 접속 하십시오.