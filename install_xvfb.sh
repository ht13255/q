#!/bin/bash

# 업데이트 및 Xvfb 설치
sudo apt-get update -y
sudo apt-get install -y xvfb

# Xvfb 실행
Xvfb :1 -screen 0 1024x768x16 &
export DISPLAY=:1

echo "Xvfb 설치 및 실행이 완료되었습니다."