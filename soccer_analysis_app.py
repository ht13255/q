import streamlit as st
import requests
from bs4 import BeautifulSoup
import tempfile
from fpdf import FPDF

# 1. FBref 크롤링 함수
def get_fbref_stats(player_name):
    url = f"https://fbref.com/en/search/search.fcgi?search={player_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 예시로 특정 스탯 추출 (HTML 구조에 따라 조정 필요)
    stats = {
        "경기 수": "25",  # 예시 데이터
        "득점": "12",
        "어시스트": "8",
        "패스 성공률": "82.5"
    }
    return stats

# 2. WhoScored 크롤링 함수
def get_whoscored_stats(player_name):
    url = f"https://www.whoscored.com/Search/?t={player_name.replace(' ', '%20')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 예시로 특정 스탯 추출 (HTML 구조에 따라 조정 필요)
    stats = {
        "키패스": "50",  # 예시 데이터
        "태클": "25",
        "드리블 성공률": "60"
    }
    return stats

# 3. Understat 크롤링 함수
def get_understat_stats(player_name):
    url = f"https://understat.com/player/{player_name.replace(' ', '%20')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 예시로 특정 스탯 추출 (HTML 구조에 따라 조정 필요)
    stats = {
        "xG": "9.5",  # 예시 데이터
        "xA": "7.3",
        "슛 정확도": "65"
    }
    return stats

# 4. SofaScore 크롤링 함수
def get_sofascore_stats(player_name):
    url = f"https://www.sofascore.com/search?q={player_name.replace(' ', '%20')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 예시로 특정 스탯 추출 (HTML 구조에 따라 조정 필요)
    stats = {
        "경기 평점": "7.8",  # 예시 데이터
        "파울": "15",
        "경고": "2"
    }
    return stats

# 5. 선수 종합 스탯 수집 함수
def get_player_stats(player_name):
    fbref_stats = get_fbref_stats(player_name)
    whoscored_stats = get_whoscored_stats(player_name)
    understat_stats = get_understat_stats(player_name)
    sofascore_stats = get_sofascore_stats(player_name)
    
    player_stats = {
        "FBref": fbref_stats,
        "WhoScored": whoscored_stats,
        "Understat": understat_stats,
        "SofaScore": sofascore_stats,
        "신체 정보": {"키": "180 cm", "몸무게": "75 kg", "주 발": "오른발"}  # 신체 정보 예시
    }
    
    return player_stats

# 6. PDF 보고서 생성 함수
def generate_report(player_stats, video_analysis):
    st.write("보고서 생성 중...")
    
    # 임시 디렉터리에서 PDF 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="축구 분석 보고서", ln=True, align='C')
        
        # 선수 신체 정보 기록
        if "신체 정보" in player_stats:
            pdf.cell(200, 10, txt="신체 정보:", ln=True)
            for key, value in player_stats["신체 정보"].items():
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        
        # 여러 소스에서 가져온 스탯 기록
        for source, stats in player_stats.items():
            if source != "신체 정보":
                pdf.cell(200, 10, txt=f"{source} 분석 결과:", ln=True)
                for key, value in stats.items():
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        
        # 영상 분석 결과 추가
        pdf.cell(200, 10, txt=video_analysis, ln=True)

        # PDF 파일 저장
        pdf_file_path = temp_file.name
        pdf.output(pdf_file_path)

    st.success(f"PDF 보고서가 생성되었습니다: {pdf_file_path}")
    
    # PDF 파일 다운로드 링크 생성
    return pdf_file_path

# 7. 공유 기능 구현
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

# 8. 메인 앱 UI 구성
def main():
    st.title("축구 분석 애플리케이션")
    
    # 1. 선수 이름 검색 및 스탯 분석
    st.header("선수 이름 검색")
    player_name = st.text_input("선수 이름을 입력하세요 (예: 홍길동)")
    player_stats = None
    
    if player_name:
        player_stats = get_player_stats(player_name)
        if player_stats:
            st.subheader(f"{player_name} 선수의 스탯")
            
            # 신체 정보 표시
            if "신체 정보" in player_stats:
                st.write("신체 정보:")
                for key, value in player_stats["신체 정보"].items():
                    st.write(f"{key}: {value}")
            
            # 각 소스별 스탯 표시
            for source, stats in player_stats.items():
                if source != "신체 정보":
                    st.write(f"{source} 분석 결과:")
                    for key, value in stats.items():
                        st.write(f"{key}: {value}")
        else:
            st.warning("해당 선수에 대한 데이터가 없습니다.")
    
    # 2. 영상 업로드 및 분석
    st.header("하이라이트 영상 업로드")
    video_file = st.file_uploader("하이라이트 영상을 업로드하세요 (최대 5GB)", type=["mp4", "avi", "mov"])
    
    if video_file:
        # 선수 번호 선택
        player_number = st.number_input("분석할 선수 번호를 입력하세요", min_value=1, step=1)
        
        if st.button("선수 번호로 분석"):
            st.write(f"선수 번호 {player_number}번에 대한 분석을 진행합니다.")
            st.video(video_file)

        # 3. 보고서 생성 및 다운로드
        if st.button("보고서 생성 및 다운로드"):
            video_analysis = f"선수 번호 {player_number}번에 대한 분석 결과입니다."
            pdf_file_path = generate_report(player_stats, video_analysis)
            st.markdown(create_shareable_download_link(pdf_file_path, "pdf"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()