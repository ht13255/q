import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import moviepy.editor as mpy
import boto3
import base64
import tempfile
from fpdf import FPDF

# 1. 선수 이름 검색 및 스탯 분석 (예시 데이터로 구현)
def get_player_stats(player_name):
    # 이 함수는 실제로는 FBref나 API를 호출해서 데이터를 가져와야 하지만,
    # 여기서는 예시 데이터를 사용합니다.
    sample_stats = {
        "홍길동": {"경기 수": 25, "득점": 12, "어시스트": 8, "패스 성공률": 82.5},
        "김철수": {"경기 수": 30, "득점": 15, "어시스트": 10, "패스 성공률": 85.0}
    }
    
    # 선수 스탯을 반환
    return sample_stats.get(player_name, None)

# 2. 선수 번호에 따라 영상 속 선수 분석 (영상 분석 관련 함수)
def analyze_player_in_video(video_file, player_number):
    # 여기서는 단순히 영상 속에서 플레이어 번호를 기반으로 분석하는 로직을 구현
    st.write(f"선수 번호 {player_number}번에 대한 분석을 진행합니다.")
    
    # 실제 영상 분석 로직을 구현해야 함 (예: OpenCV 사용)
    # 추후 YOLO 등 모델을 사용하여 선수 움직임 감지 가능
    st.video(video_file)

# PDF 보고서 생성 함수
def generate_report(player_stats, video_analysis):
    st.write("보고서 생성 중...")
    
    # 임시 디렉터리에서 PDF 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="축구 분석 보고서", ln=True, align='C')
        
        # 선수 스탯 기록 추가
        if player_stats:
            pdf.cell(200, 10, txt="선수 스탯 분석 결과:", ln=True)
            for key, value in player_stats.items():
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        
        # 영상 분석 결과 추가
        pdf.cell(200, 10, txt=video_analysis, ln=True)

        # PDF 파일 저장
        pdf_file_path = temp_file.name
        pdf.output(pdf_file_path)

    st.success(f"PDF 보고서가 생성되었습니다: {pdf_file_path}")
    
    # PDF 파일 다운로드 링크 생성
    return pdf_file_path

# 공유 기능 구현
def create_shareable_download_link(file_path, file_type):
    with open(file_path, "rb") as f:
        data = f.read()
        b64_data = base64.b64encode(data).decode()
    
    if file_type == "pdf":
        mime_type = "application/pdf"
        file_name = "soccer_analysis_report.pdf"
    elif file_type == "video":
        mime_type = "video/mp4"
        file_name = "highlight_clips.mp4"
    else:
        raise ValueError("지원되지 않는 파일 유형입니다.")

    href = f'<a href="data:{mime_type};base64,{b64_data}" download="{file_name}">다운로드 링크 생성</a>'
    return href

# 메인 앱 UI 구성
def main():
    st.title("축구 분석 애플리케이션")
    
    # 1. 선수 이름 검색 및 스탯 분석
    st.header("선수 이름 검색")
    player_name = st.text_input("선수 이름을 입력하세요 (예: 홍길동, 김철수)")
    player_stats = None
    
    if player_name:
        player_stats = get_player_stats(player_name)
        if player_stats:
            st.subheader(f"{player_name} 선수의 스탯")
            for key, value in player_stats.items():
                st.write(f"{key}: {value}")
        else:
            st.warning("해당 선수에 대한 데이터가 없습니다.")
    
    # 2. 영상 업로드 및 분석
    st.header("하이라이트 영상 업로드")
    video_file = st.file_uploader("하이라이트 영상을 업로드하세요", type=["mp4", "avi", "mov"])
    
    if video_file:
        # 선수 번호 선택
        player_number = st.number_input("분석할 선수 번호를 입력하세요", min_value=1, step=1)
        
        if st.button("선수 번호로 분석"):
            analyze_player_in_video(video_file, player_number)

        # 3. 보고서 생성 및 다운로드
        if st.button("보고서 생성 및 다운로드"):
            video_analysis = f"선수 번호 {player_number}번에 대한 분석 결과입니다."
            pdf_file_path = generate_report(player_stats, video_analysis)
            st.markdown(create_shareable_download_link(pdf_file_path, "pdf"), unsafe_allow_html=True)

    # 사용자 피드백 수집
    st.header("사용자 피드백")
    collect_user_feedback()

if __name__ == "__main__":
    main()