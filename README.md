# RealSense Python Test

Raspberry Pi에서 Intel RealSense를 Python으로 테스트하기 위한 기본 환경입니다.

## 1. Clone

```bash
git clone <YOUR_REPOSITORY_URL>
cd realsense_docker
```

## 2. Install

```bash
chmod +x setup.sh run.sh
./setup.sh
```

설치되는 시스템 패키지:

- python3-pip
- python3-venv
- libusb-1.0-0
- libgl1

설치되는 Python 패키지:

- pyrealsense2
- opencv-python
- numpy

## 3. Run

```bash
./run.sh
```

또는:

```bash
source ~/realsense_venv/bin/activate
python3 realsense_test.py
```

`q` 키를 누르면 종료합니다.

## 4. Raspberry Pi USB 확인

RealSense가 연결된 상태에서:

```bash
lsusb
```

Intel RealSense 장치가 표시되는지 확인합니다.

## 5. 주의

`opencv-python`의 GUI 창을 사용하므로 Raspberry Pi에서 데스크톱 GUI 환경으로 실행하는 것을 기준으로 합니다.
