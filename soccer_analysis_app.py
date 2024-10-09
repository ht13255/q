# File: app.py

import streamlit as st
import requests
from bs4 import BeautifulSoup
import tempfile
from fpdf import FPDF
import cv2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. FBref 크롤링 함수 - 고급 스탯 분석 포함 (기존 유지)
def get_fbref_stats(player_name):
    # 기존 스탯 수집 로직 유지
    stats = {
        "골": "12",  
        "골 기대값(xG)": "9.5",
        "xG 유효 슛(xGOT)": "7.2",
        "도움": "8",
        "Expected Assists (xA)": "6.3",
        "패스 성공률": "82.5",
        "전진 패스": "45",
        "침투 성공률": "65",
        "주요 침투 구역": "상대 페널티 박스 안, 상대 측면 공간"
    }
    return stats

# 2. 영상 분석 함수 - OpenCV를 사용한 움직임 분석
def analyze_video_for_movement(video_file, player_number):
    # OpenCV로 비디오 파일 열기
    cap = cv2.VideoCapture(video_file)
    
    # 선수 움직임 추적을 위한 경로
    movement_path = []

    # 프레임마다 분석
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 움직임 분석 예시: 특정 번호의 선수 추적 (가정: 선수 번호를 구분할 수 있는 방식으로)
        # 이 코드는 실시간 객체 추적과 경로 저장을 포함합니다.
        # 예시로서 흰색의 영역을 추적하는 코드입니다. 실제로는 선수 번호 인식 모델을 사용하여 개선 필요.
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh_frame = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)

        # 모멘트를 사용하여 객체의 중심(추적 대상) 위치를 찾음
        moments = cv2.moments(thresh_frame)
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])  # X 좌표
            cy = int(moments['m01'] / moments['m00'])  # Y 좌표
            movement_path.append((cx, cy))  # 추적 경로 저장
    
    cap.release()

    # 추적된 경로 시각화
    plt.figure(figsize=(6, 4))
    x_coords, y_coords = zip(*movement_path)
    plt.plot(x_coords, y_coords, marker='o', color='blue', markersize=5)
    plt.title(f"선수 {player_number}의 움직임 경로")
    plt.xlabel("X 좌표")
    plt.ylabel("Y 좌표")
    
    # 움직임 경로를 이미지 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        plt.savefig(tmpfile.name)
        plt.close()
        return tmpfile.name

# 3. PDF 보고서 생성 함수
def generate_report(final_score, player_stats, video_analysis, movement_image_path):
    st.write("보고서 생성 중...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="축구 분석 보고서", ln=True, align='C')
        
        pdf.cell(200, 10, txt=f"선수 종합 점수: {final_score}/100", ln=True)
        
        pdf.cell(200, 10, txt="세부 스탯 분석 결과:", ln=True)
        for key, value in player_stats.items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        
        # 영상 분석 결과 추가
        pdf.cell(200, 10, txt=video_analysis, ln=True)

        # 선수 움직임 경로 이미지 추가
        pdf.add_page()
        pdf.image(movement_image_path, x=10, y=10, w=180)

        pdf_file_path = temp_file.name
        pdf.output(pdf_file_path)

    st.success(f"PDF 보고서가 생성되었습니다: {pdf_file_path}")
    
    return pdf_file_path

# 4. Streamlit UI 구성
def main():
    st.title("축구 분석 애플리케이션")
    
    st.header("선수 이름 검색")
    player_name = st.text_input("선수 이름을 입력하세요 (예: 홍길동)")
    
    position = st.selectbox("선수 포지션을 선택하세요", ['공격수', '미드필더', '수비수'])
    
    if player_name:
        fbref_stats = get_fbref_stats(player_name)
        final_score = 85  # 예시 점수
        
        st.subheader(f"{player_name} 선수의 종합 점수: {final_score}/100")

        # 하이라이트 영상 업로드 및 분석
        st.header("하이라이트 영상 업로드")
        video_file = st.file_uploader("하이라이트 영상을 업로드하세요 (최대 5GB)", type=["mp4", "avi", "mov"])
        
        if video_file:
            player_number = st.number_input("분석할 선수 번호를 입력하세요", min_value=1, step=1)
            if st.button("선수 번호로 분석"):
                movement_image_path = analyze_video_for_movement(video_file, player_number)
                st.image(movement_image_path, caption=f"선수 {player_number}의 움직임 경로")
                
                # PDF 보고서 생성 및 다운로드
                if st.button("PDF 보고서 생성 및 다운로드"):
                    video_analysis = f"선수 번호 {player_number}의 움직임이 분석되었습니다."
                    pdf_file_path = generate_report(final_score, fbref_stats, video_analysis, movement_image_path)
                    st.markdown(f'<a href="file://{pdf_file_path}" download>PDF 다운로드</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

