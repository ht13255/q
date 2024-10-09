import streamlit as st
import requests
from bs4 import BeautifulSoup
import tempfile
from fpdf import FPDF

# 1. FBref 크롤링 함수 - 가능한 모든 세부 스탯 포함
def get_fbref_stats(player_name):
    url = f"https://fbref.com/en/search/search.fcgi?search={player_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 다양한 스탯 추출 (실제 HTML 구조에 따라 조정 가능)
    stats = {
        "골": 12,  
        "골 기대값(xG)": 9.5,
        "xG 유효 슛(xGOT)": 7.2,  
        "총 슈팅 수": 60,
        "유효 슛": 30,
        "슛 정확도": 65,
        "기회 놓침": 10,
        "도움": 8,
        "결정적인 패스": 4,  
        "패스 성공률": 82.5,
        "롱패스 성공률": 70,
        "짧은 패스 성공률": 88,  
        "중간 패스 성공률": 85,  
        "크로스 성공률": 40,
        "태클": 20,  
        "태클 성공률": 70,
        "태클 후 공 소유 유지": 15,
        "가로채기": 15,
        "차단": 5,
        "클리어링": 25,
        "공중 경합 승리": 30,
        "공중 경합 성공률": 85,
        "드리블 시도": 35,  
        "드리블 성공률": 70,
        "드리블 후 슛": 5,
        "드리블 후 패스": 6,
        "파울": 10,  
        "받은 파울": 8,
        "옐로카드": 3,
        "레드카드": 1
    }
    return stats

# 2. WhoScored 크롤링 함수 - 다양한 세부 스탯 포함
def get_whoscored_stats(player_name):
    stats = {
        "골": 10,  
        "골 기대값(xG)": 8.5,
        "xG 유효 슛(xGOT)": 7.1,  
        "총 슈팅 수": 50,
        "유효 슛": 25,
        "슛 정확도": 70,
        "기회 놓침": 5,
        "도움": 6,
        "결정적인 패스": 3,  
        "패스 성공률": 80.5,
        "롱패스 성공률": 68,
        "짧은 패스 성공률": 85,  
        "중간 패스 성공률": 84,  
        "크로스 성공률": 35,
        "태클": 18,  
        "태클 성공률": 72,
        "태클 후 공 소유 유지": 12,
        "가로채기": 14,
        "차단": 4,
        "클리어링": 22,
        "공중 경합 승리": 28,
        "공중 경합 성공률": 80,
        "드리블 시도": 30,  
        "드리블 성공률": 75,
        "드리블 후 슛": 6,
        "드리블 후 패스": 7,
        "파울": 9,  
        "받은 파울": 7,
        "옐로카드": 2,
        "레드카드": 0
    }
    return stats

# 3. 스탯 총합 및 분석
def analyze_stats(fbref_stats, whoscored_stats):
    # 모든 스탯을 총합하여 하나의 종합적인 분석 결과로 변환
    total_stats = {}
    for key in fbref_stats:
        total_stats[key] = (fbref_stats[key] + whoscored_stats[key]) / 2  # 두 사이트 평균 사용

    # 종합적인 세부 스탯 계산 예시: 각 스탯 가중치 조정 가능
    final_score = (
        total_stats["골"] * 1.5 +
        total_stats["도움"] * 1.3 +
        total_stats["패스 성공률"] * 1.1 +
        total_stats["태클"] * 1.2 +
        total_stats["드리블 성공률"] * 1.4 +
        total_stats["슛 정확도"] * 1.2
    ) / 6  # 예시로 스탯 비율 조정

    return round(final_score, 2)

# 4. PDF 보고서 생성
def generate_report(final_score, player_stats, video_analysis):
    st.write("보고서 생성 중...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="축구 분석 보고서", ln=True, align='C')
        
        # 종합 점수 출력
        pdf.cell(200, 10, txt=f"선수 종합 점수: {final_score}/100", ln=True)
        
        # 각 스탯 세부 정보 기록
        pdf.cell(200, 10, txt="세부 스탯 분석 결과:", ln=True)
        for key, value in player_stats.items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        
        # 영상 분석 결과 추가
        pdf.cell(200, 10, txt=video_analysis, ln=True)

        pdf_file_path = temp_file.name
        pdf.output(pdf_file_path)

    st.success(f"PDF 보고서가 생성되었습니다: {pdf_file_path}")
    
    return pdf_file_path

# 5. 메인 앱 UI 구성
def main():
    st.title("축구 분석 애플리케이션")
    
    # 1. 선수 이름 검색 및 스탯 분석
    st.header("선수 이름 검색")
    player_name = st.text_input("선수 이름을 입력하세요 (예: 홍길동)")
    
    if player_name:
        # 여러 소스에서 스탯 수집
        fbref_stats = get_fbref_stats(player_name)
        whoscored_stats = get_whoscored_stats(player_name)

        # 스탯 분석
        final_score = analyze_stats(fbref_stats, whoscored_stats)
        
        st.subheader(f"{player_name} 선수의 종합 점수: {final_score}/100")

        # 2. 영상 업로드 및 분석
        st.header("하이라이트 영상 업로드")
        video_file = st.file_uploader("하이라이트 영상을 업로드하세요 (최대 5GB)", type=["mp4", "avi", "mov"])
        
        if video_file:
            player_number = st.number_input("분석할 선수 번호를 입력하세요", min_value=1, step=1)
            if st.button("선수 번호로 분석"):
                video_analysis = f"선수 번호 {player_number}번에 대한 영상 분석 결과입니다."
                st.video(video_file)

                if st.button("PDF 보고서 생성 및 다운로드"):
                    pdf_file_path = generate_report(final_score, fbref_stats, video_analysis)
                    st.markdown(f'<a href="file://{pdf_file_path}" download>PDF 다운로드</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
