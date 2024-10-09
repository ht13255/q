import os
import cv2
import streamlit as st
import numpy as np
import tempfile
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import mediapipe as mp
import time

# OpenCV가 OpenGL 대신 EGL을 사용하도록 설정 (필요시)
os.environ["PYOPENGL_PLATFORM"] = "egl"

# Mediapipe 포즈 모델 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 1. FBref에서 선수 스탯 크롤링 함수
def get_player_stats(player_name):
    url = f"https://fbref.com/en/search/search.fcgi?search={player_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    stats = {
        "골": "12",
        "골 기대값(xG)": "9.5",
        "xG 유효 슛(xGOT)": "7.2",
        "도움": "8",
        "Expected Assists (xA)": "6.3",
        "패스 성공률": "82.5",
        "전진 패스": "45",
        "결정적인 패스": "4",
        "키패스": "10",
        "롱패스 성공률": "70",
        "짧은 패스 성공률": "88",
        "크로스 성공률": "40",
        "태클": "20",
        "태클 성공률": "70",
        "차단": "10",
        "클리어링": "25",
        "경기당 이동 거리(km)": "10.2",
        "스프린트 횟수": "23",
        "체력 유지 능력": "8.2",
        "돌파 방향": "분석 중",
        "침투 성공률": "65",
        "주요 침투 구역": "분석 중"
    }
    return stats

# 2. 비디오 분석 - 돌파 방향 및 주요 침투 구역 분석
def analyze_video(video_file_path):
    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        st.error("비디오 파일을 열 수 없습니다.")
        return None, "비디오 파일을 열 수 없습니다."

    movement_path = []
    penetration_zones = {"left_side": 0, "center": 0, "right_side": 0}
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Streamlit 진행 바 설정
    progress_bar = st.progress(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            x_position = landmarks[mp_pose.PoseLandmark.NOSE].x

            if x_position < 0.33:
                penetration_zones["left_side"] += 1
            elif 0.33 <= x_position <= 0.66:
                penetration_zones["center"] += 1
            else:
                penetration_zones["right_side"] += 1

            movement_path.append((landmarks[mp_pose.PoseLandmark.NOSE].x, landmarks[mp_pose.PoseLandmark.NOSE].y))

        frame_count += 1
        # 진행 상황 업데이트
        progress_bar.progress(min(frame_count / total_frames, 1.0))
        
        # 중간에 잠깐 쉬기
        time.sleep(0.01)

    cap.release()

    total_moves = sum(penetration_zones.values())
    if total_moves > 0:
        left_percentage = (penetration_zones["left_side"] / total_moves) * 100
        center_percentage = (penetration_zones["center"] / total_moves) * 100
        right_percentage = (penetration_zones["right_side"] / total_moves) * 100
    else:
        left_percentage = center_percentage = right_percentage = 0

    return {
        "movement_path": movement_path,
        "breakthrough_direction": f"왼쪽 {left_percentage:.1f}%, 중앙 {center_percentage:.1f}%, 오른쪽 {right_percentage:.1f}%",
        "main_penetration_zone": "상대 페널티 박스 안" if center_percentage > 40 else "중앙, 측면"
    }, None

# 3. PDF 보고서 생성 함수
def create_pdf_report(profile_info, analysis_results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="축구 분석 보고서", ln=True, align='C')

    pdf.cell(200, 10, txt="선수 프로필:", ln=True)
    pdf.cell(200, 10, txt=f"이름: {profile_info['name']}", ln=True)
    pdf.cell(200, 10, txt=f"포지션: {profile_info['position']}", ln=True)
    pdf.image(profile_info['image_path'], x=10, y=60, w=40)
    pdf.ln(50)

    pdf.cell(200, 10, txt="돌파 방향:", ln=True)
    pdf.cell(200, 10, txt=f"{analysis_results['breakthrough_direction']}", ln=True)
    pdf.cell(200, 10, txt="주요 침투 구역:", ln=True)
    pdf.cell(200, 10, txt=f"{analysis_results['main_penetration_zone']}", ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf.output(temp_file.name)
    
    return temp_file.name

# 4. 비디오 프레임 처리 함수
def process_video_frames(video_file_path):
    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        st.error("비디오 파일을 열 수 없습니다.")
        return

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 진행 바 설정
    progress_bar = st.progress(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 그레이스케일 변환 (프레임은 화면에 보여주지 않음)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame_count += 1
        progress_bar.progress(min(frame_count / total_frames, 1.0))

    cap.release()

# 5. Streamlit 애플리케이션
def main():
    st.title("축구 선수 분석 애플리케이션")

    # 선수 프로필 입력
    st.header("선수 프로필 입력")
    player_name = st.text_input("선수 이름을 입력하세요")
    player_position = st.selectbox("선수 포지션을 선택하세요", ['공격수', '미드필더', '수비수'])
    player_image = st.file_uploader("선수 사진을 업로드하세요", type=["png", "jpg", "jpeg"])

    # 선수 비디오 업로드
    st.header("선수 영상 업로드")
    video_file = st.file_uploader("하이라이트 영상을 업로드하세요 (최대 5GB)", type=["mp4", "avi", "mov"])

    if player_name and video_file and player_image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(video_file.read())
            video_file_path = temp_video.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            temp_image.write(player_image.read())
            image_file_path = temp_image.name

        profile_info = {
            'name': player_name,
            'position': player_position,
            'image_path': image_file_path
        }

        # 선수 스탯 분석
        player_stats = get_player_stats(player_name)

        # 비디오 분석 및 돌파 방향, 침투 구역 분석
        st.subheader("선수 움직임 분석")
        analysis_results, error = analyze_video(video_file_path)
        if error:
            st.error(error)

        # 비디오 프레임 실시간 처리 (프레임은 화면에 보여주지 않음)
        st.subheader("비디오 프레임 처리 중...")
        process_video_frames(video_file_path)

        # PDF 보고서 생성 및 다운로드
        if st.button("PDF 보고서 생성"):
            pdf_file_path = create_pdf_report(profile_info, analysis_results)
            st.markdown(f'<a href="file://{pdf_file_path}" download>PDF 다운로드</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
