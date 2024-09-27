import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, mean_squared_error
import plotly.express as px
import matplotlib.pyplot as plt

# 1. 사용자 입력 받기
st.title("축구 선수 스카우팅 시스템 - 포지션별 선택 및 예측")
position = st.selectbox("원하는 포지션을 선택하세요", 
                        ['공격수', '수비수', '미드필더', '골키퍼', '윙어', '풀백', '센터백', '공격형 미드필더', '수비형 미드필더'])
preferred_foot = st.text_input("원하는 주발을 입력하세요 (예: 왼발, 오른발):")
age_limit = 25
min_games = 150
max_games = 200

# 2. 데이터 수집 (예시 데이터 사용)
def fetch_player_data():
    data = {
        "name": ["선수 A", "선수 B", "선수 C", "선수 D", "선수 E"],
        "age": [23, 24, 22, 21, 25],
        "position": ["공격수", "수비수", "미드필더", "공격수", "수비수"],
        "games": [180, 160, 170, 140, 155],
        "foot": ["오른발", "왼발", "오른발", "왼발", "오른발"],
        "market_value": [50000000, 30000000, 45000000, 25000000, 32000000],
        "injury_record": [2, 5, 3, 1, 4],  # 부상 횟수
        "pass_success_rate": [85, 78, 82, 76, 80],
        "dribble_success_rate": [60, 50, 70, 65, 55],
        "shot_accuracy": [75, 60, 65, 70, 62],  # 슛 정확도
        "ball_possession_time": [45, 38, 50, 40, 42],  # 볼 소유 시간
        "pass_per_game": [60, 50, 55, 48, 52],  # 경기당 패스 횟수
    }
    return pd.DataFrame(data)

df = fetch_player_data()

# 3. 부상 확률 예측 - Gradient Boosting 및 XGBoost 모델 사용
def train_injury_risk_model(df):
    X = df[['age', 'games', 'injury_record']]  # 입력 데이터
    y = (df['injury_record'] > 3).astype(int)  # 부상 확률 높음 (1), 낮음 (0)으로 변환
    
    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 하이퍼파라미터 그리드 설정 (Gradient Boosting)
    gb_param_grid = {
        'n_estimators': [50, 100, 150],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7]
    }
    
    gb_grid = GridSearchCV(GradientBoostingClassifier(random_state=42), gb_param_grid, cv=5, scoring='accuracy')
    gb_grid.fit(X_train, y_train)
    
    # 하이퍼파라미터 그리드 설정 (XGBoost)
    xgb_param_grid = {
        'n_estimators': [50, 100, 150],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'gamma': [0, 0.1, 0.3]
    }
    
    xgb_grid = GridSearchCV(XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'), 
                            xgb_param_grid, cv=5, scoring='accuracy')
    xgb_grid.fit(X_train, y_train)
    
    # 최적의 파라미터 출력
    st.write(f"Gradient Boosting 최적의 파라미터: {gb_grid.best_params_}")
    st.write(f"XGBoost 최적의 파라미터: {xgb_grid.best_params_}")
    
    # 교차 검증 및 모델 성능 평가
    gb_score = gb_grid.best_score_
    xgb_score = xgb_grid.best_score_

    return gb_grid.best_estimator_, xgb_grid.best_estimator_, gb_score, xgb_score

gb_injury_model, xgb_injury_model, gb_injury_score, xgb_injury_score = train_injury_risk_model(df)

# 4. 판매 가치 예측 - Gradient Boosting 및 XGBoost 모델 사용
def train_market_value_model(df):
    X = df[['age', 'games', 'injury_record']]  # 입력 데이터
    y = df['market_value']  # 목표 데이터
    
    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 하이퍼파라미터 그리드 설정 (Gradient Boosting)
    gb_param_grid = {
        'n_estimators': [50, 100, 150],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7]
    }
    
    gb_grid = GridSearchCV(GradientBoostingRegressor(random_state=42), gb_param_grid, cv=5, scoring='neg_mean_squared_error')
    gb_grid.fit(X_train, y_train)
    
    # 하이퍼파라미터 그리드 설정 (XGBoost)
    xgb_param_grid = {
        'n_estimators': [50, 100, 150],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'gamma': [0, 0.1, 0.3]
    }
    
    xgb_grid = GridSearchCV(XGBRegressor(random_state=42), xgb_param_grid, cv=5, scoring='neg_mean_squared_error')
    xgb_grid.fit(X_train, y_train)
    
    # 최적의 파라미터 출력
    st.write(f"Gradient Boosting 최적의 파라미터: {gb_grid.best_params_}")
    st.write(f"XGBoost 최적의 파라미터: {xgb_grid.best_params_}")
    
    # 교차 검증 및 모델 성능 평가
    gb_mse = gb_grid.best_score_
    xgb_mse = xgb_grid.best_score_

    return gb_grid.best_estimator_, xgb_grid.best_estimator_, gb_mse, xgb_mse

gb_market_model, xgb_market_model, gb_market_mse, xgb_market_mse = train_market_value_model(df)

# 5. 시각화 - 히트맵 생성
def generate_heatmap(player_name):
    heatmap_data = [[0, 1, 0], [0.5, 0.8, 0.2], [0.3, 0.6, 0.1]]
    fig = px.imshow(heatmap_data, labels=dict(x="필드 X", y="필드 Y", color="활동 빈도"))
    st.plotly_chart(fig)

# 6. 시각화 - 다양한 스탯 시각화
def visualize_player_stats(player):
    st.write(f"선수 이름: {player['name']}")
    
    # 패스 성공률 시각화
    fig, ax = plt.subplots()
    ax.bar(['Pass Success'], [player['pass_success_rate']], color='blue')
    ax.set_ylim([0, 100])
    st.pyplot(fig)

    # 드리블 성공률 시각화
    fig, ax = plt.subplots()
    ax.bar(['Dribble Success'], [player['dribble_success_rate']], color='green')
    ax.set_ylim([0, 100])
    st.pyplot(fig)

    # 슛 정확도 시각화
    fig, ax = plt.subplots()
    ax.bar(['Shot Accuracy'], [player['shot_accuracy']], color='red')
    ax.set_ylim([0, 100])
    st.pyplot(fig)

    # 볼 소유 시간 시각화
    fig, ax = plt.subplots()
    ax.bar(['Ball Possession'], [player['ball_possession_time']], color='purple')
    ax.set_ylim([0, 100])
    st.pyplot(fig)

    # 경기당 패스 횟수 시각화
    fig, ax = plt.subplots()
    ax.bar(['Pass per Game'], [player['pass_per_game']], color='orange')
    ax.set_ylim([0, 100])
    st.pyplot(fig)

# 7. Streamlit 결과 출력
if st.button("선수 검색"):
    filtered_players = df[
        (df['age'] <= age_limit) &
        (df['games'] >= min_games) &
        (df['games'] <= max_games) &
        (df['position'] == position) &
        (df['foot'] == preferred_foot)
    ]
    
    if not filtered_players.empty:
        st.dataframe(filtered_players)

        # 부상 확률 예측
        X_injury = filtered_players[['age', 'games', 'injury_record']].values
        gb_injury_prob = gb_injury_model.predict(X_injury)
        xgb_injury_prob = xgb_injury_model.predict(X_injury)
        filtered_players['gb_injury_prob'] = gb_injury_prob
        filtered_players['xgb_injury_prob'] = xgb_injury_prob
        
        st.write("부상 확률 예측 (Gradient Boosting):", filtered_players[['name', 'gb_injury_prob']])
        st.write("부상 확률 예측 (XGBoost):", filtered_players[['name', 'xgb_injury_prob']])
        st.write(f"Gradient Boosting 정확도: {gb_injury_score}")
        st.write(f"XGBoost 정확도: {xgb_injury_score}")
        
        # 판매 가치 예측
        X_market = filtered_players[['age', 'games', 'injury_record']].values
        gb_market_value_pred = gb_market_model.predict(X_market)
        xgb_market_value_pred = xgb_market_model.predict(X_market)
        filtered_players['gb_predicted_market_value'] = gb_market_value_pred
        filtered_players['xgb_predicted_market_value'] = xgb_market_value_pred
        
        st.write("예측된 시장 가치 (Gradient Boosting):", filtered_players[['name', 'gb_predicted_market_value']])
        st.write("예측된 시장 가치 (XGBoost):", filtered_players[['name', 'xgb_predicted_market_value']])
        st.write(f"Gradient Boosting MSE: {gb_market_mse}")
        st.write(f"XGBoost MSE: {xgb_market_mse}")
        
        # 히트맵 생성
        generate_heatmap("선수 A")

        # 각 선수의 스탯 시각화
        for i, player in filtered_players.iterrows():
            visualize_player_stats(player)
    else:
        st.write("조건에 맞는 선수가 없습니다.")
