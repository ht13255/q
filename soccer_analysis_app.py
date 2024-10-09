import cv2
import streamlit as st
import numpy as np
import tempfile
from fpdf import FPDF

# MediaPipe 포즈 추정 모델 불러오기
import mediapipe as mp
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 포즈 각도 계산 함수 (팔, 다리 각도 계산에 사용)
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# 공의 궤적 및 구질 분석 함수
def track_ball_trajectory(video_file_path):
    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        st.error("비디오 파일을 열 수 없습니다.")
        return None, "비디오 파일을 열 수 없습니다."

    ball_trajectory = []
    previous_position = None
    speeds = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_frame, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                (x, y, w, h) = cv2.boundingRect(contour)
                ball_position = (int(x + w / 2), int(y + h / 2))
                ball_trajectory.append(ball_position)

                if previous_position is not None:
                    distance = np.linalg.norm(np.array(ball_position) - np.array(previous_position))
                    speed = distance
                    speeds.append(speed)
                previous_position = ball_position

    cap.release()
    average_speed = np.mean(speeds) if speeds else 0
    ball_curve = "직선" if average_speed > 10 else "느린 곡선"

    return ball_trajectory, average_speed, ball_curve, None

# 선수 움직임, 자세 및 밸런스 분석 함수
def analyze_player_movements(video_file_path):
    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        st.error("비디오 파일을 열 수 없습니다.")
        return None, "비디오 파일을 열 수 없습니다."

    frame_count = 0
    posture_data = []
    off_the_ball_movements = []
    on_the_ball_movements = []
    balance_data = []

    previous_player_pos = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

            player_pos = np.array(left_shoulder)

            shoulder_angle = calculate_angle(left_hip, left_shoulder, right_shoulder)
            knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

            balance = abs(shoulder_angle - knee_angle)
            balance_data.append({
                'frame': frame_count,
                'balance': balance
            })

            if previous_player_pos is not None:
                player_movement = np.linalg.norm(player_pos - previous_player_pos)
                if player_movement > 0.05:
                    off_the_ball_movements.append({
                        'frame': frame_count,
                        'event': 'Off-the-ball Movement'
                    })
            else:
                on_the_ball_movements.append({
                    'frame': frame_count,
                    'event': 'On-the-ball Movement'
                })

            posture_data.append({
                'frame': frame_count,
                'shoulder_angle': shoulder_angle,
                'knee_angle': knee_angle
            })

            previous_player_pos = player_pos
        frame_count += 1

    cap.release()
    return {
        'posture_data': posture_data,
        'off_the_ball_movements': off_the_ball_movements,
        'on_the_ball_movements': on_the_ball_movements,
        'balance_data': balance_data
    }, None

# PDF 보고서 생성 함수
def generate_analysis_report(profile_info, analysis_results, ball_analysis):
    posture_data = analysis_results['posture_data']
    balance_data = analysis_results['balance_data']
    off_the_ball_movements = analysis_results['off_the_ball_movements']
    on_the_ball_movements = analysis_results['on_the_ball_movements']
    ball_trajectory, average_speed, ball_curve, _ = ball_analysis

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="축구 분석 보고서", ln=True, align='C')

    # 선수 프로필 정보 추가
    pdf.cell(200, 10, txt="선수 프로필:", ln=True)
    pdf.cell(200, 10, txt=f"이름: {profile_info['name']}", ln=True)
    pdf.cell(200, 10, txt=f"포지션: {profile_info['position']}", ln=True)
    pdf.image(profile_info['image_path'], x=10, y=60, w=40)

    pdf.ln(50)

    # 포즈 분석 데이터 추가
    pdf.cell(200, 10, txt="포즈 분석:", ln=True)
    for data in posture_data:
        pdf.cell(200, 10, txt=f"Frame: {data['frame']}, Shoulder Angle: {data['shoulder_angle']}, Knee Angle: {data['knee_angle']}", ln=True)

    # 밸런스 및 코어 안정성 분석 추가
    pdf.cell(200, 10, txt="몸의 밸런스 및 코어 안정성 분석:", ln=True)
    for balance in balance_data:
        pdf.cell(200, 10, txt=f"Frame: {balance['frame']}, Balance Score: {balance['balance']}", ln=True)

    # 오프더볼/온더볼 움직임 분석 추가
    pdf.cell(200, 10, txt="오프더볼 움직임:", ln=True)
    for movement in off_the_ball_movements:
        pdf.cell(200, 10, txt=f"Frame: {movement['frame']}, Event: {movement['event']}", ln=True)

    pdf.cell(200, 10, txt="온더볼 움직임:", ln=True)
    for movement in on_the_ball_movements:
        pdf.cell(200, 10, txt=f"Frame: {movement['frame']}, Event: {movement['event']}", ln=True)

    # 공의 궤적 분석 결과 추가
    pdf.cell(200, 10, txt="공의 구질과 궤적 분석:", ln=True)
    pdf.cell(200, 10, txt=f"평균 속도: {average_speed:.2f}, 구질: {ball_curve}", ln=True)

    # PDF 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdf.output(temp_file.name)

    return temp_file.name

# Streamlit 애플리케이션 UI 구성
def main():
    st.title("축구 선수 분석 애플리케이션")

    st.header("선수 프로필 입력")
    player_name = st.text_input("선수 이름을 입력하세요")
    player_position = st.text_input("선수 포지션을 입력하세요")
    player_image = st.file_uploader("선수 사진을 업로드하세요", type=["png", "jpg", "jpeg"])

    st.header("선수 영상 업로드")
    video_file = st.file_uploader("하이라이트 영상을 업로드하세요 (최대 5GB)", type=["mp4", "avi", "mov"])

    if video_file and player_image:
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

        # 선수 움직임, 자세 및 밸런스 분석
        st.subheader("선수 움직임 분석")
        analysis_results, error = analyze_player_movements(video_file_path)
        if error:
            st.error(error)

        # 공의 궤적 및 구질 분석
        st.subheader("공의 궤적 분석")
        ball_analysis, error = track_ball_trajectory(video_file_path)
        if error:
            st.error(error)

        # 분석 보고서 생성
        if st.button("PDF 보고서 생성"):
            pdf_file_path = generate_analysis_report(profile_info, analysis_results, ball_analysis)
            st.markdown(f'<a href="file://{pdf_file_path}" download>PDF 다운로드</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
