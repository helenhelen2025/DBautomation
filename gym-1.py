import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import hashlib

# 데이터베이스 초기화
def init_database():
    conn = sqlite3.connect('gym_management.db')
    cursor = conn.cursor()
    
    # 회원 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            membership_type TEXT,
            start_date DATE,
            end_date DATE,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # 트레이너 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            experience_years INTEGER,
            rating REAL DEFAULT 4.5,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # 운동 기록 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            exercise_name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            duration INTEGER,
            calories_burned INTEGER,
            date DATE,
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    ''')
    
    # 수업 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            trainer_id INTEGER,
            date DATE,
            time TEXT,
            duration INTEGER,
            max_capacity INTEGER,
            current_bookings INTEGER DEFAULT 0,
            FOREIGN KEY (trainer_id) REFERENCES trainers (id)
        )
    ''')
    
    # 예약 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            class_id INTEGER,
            booking_date DATE,
            status TEXT DEFAULT 'confirmed',
            FOREIGN KEY (member_id) REFERENCES members (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# 샘플 데이터 삽입
def insert_sample_data():
    conn = sqlite3.connect('gym_management.db')
    cursor = conn.cursor()
    
    # 기존 데이터 확인
    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # 샘플 회원 데이터
    members_data = [
        ('김철수', 'kim@email.com', '010-1234-5678', '프리미엄', '2024-01-15', '2024-12-15'),
        ('이영희', 'lee@email.com', '010-2345-6789', '일반', '2024-02-01', '2024-08-01'),
        ('박민수', 'park@email.com', '010-3456-7890', '프리미엄', '2024-03-10', '2025-03-10'),
        ('최지은', 'choi@email.com', '010-4567-8901', '일반', '2024-04-05', '2024-10-05'),
        ('정대호', 'jung@email.com', '010-5678-9012', '프리미엄', '2024-05-20', '2025-05-20'),
    ]
    
    for member in members_data:
        cursor.execute('''
            INSERT INTO members (name, email, phone, membership_type, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', member)
    
    # 샘플 트레이너 데이터
    trainers_data = [
        ('김트레이너', '웨이트 트레이닝', 5, 4.8),
        ('이코치', '요가/필라테스', 3, 4.7),
        ('박선생', '크로스핏', 7, 4.9),
        ('최강사', '수영', 4, 4.6),
    ]
    
    for trainer in trainers_data:
        cursor.execute('''
            INSERT INTO trainers (name, specialty, experience_years, rating)
            VALUES (?, ?, ?, ?)
        ''', trainer)
    
    # 샘플 운동 기록 데이터
    exercises = ['벤치프레스', '스쿼트', '데드리프트', '풀업', '푸쉬업', '런닝머신', '사이클']
    for i in range(50):
        member_id = random.randint(1, 5)
        exercise = random.choice(exercises)
        sets = random.randint(3, 5)
        reps = random.randint(8, 15)
        weight = random.randint(20, 100)
        duration = random.randint(30, 90)
        calories = random.randint(150, 400)
        date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        cursor.execute('''
            INSERT INTO workout_records 
            (member_id, exercise_name, sets, reps, weight, duration, calories_burned, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (member_id, exercise, sets, reps, weight, duration, calories, date.date()))
    
    # 샘플 수업 데이터
    classes_data = [
        ('아침 요가', 2, '2024-07-29', '07:00', 60, 15),
        ('점심 크로스핏', 3, '2024-07-29', '12:00', 45, 12),
        ('저녁 웨이트', 1, '2024-07-29', '19:00', 90, 8),
        ('수영 강습', 4, '2024-07-30', '10:00', 60, 10),
    ]
    
    for class_data in classes_data:
        cursor.execute('''
            INSERT INTO classes (class_name, trainer_id, date, time, duration, max_capacity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', class_data)
    
    conn.commit()
    conn.close()

# 회원권 만료 알림
def check_membership_expiry():
    conn = sqlite3.connect('gym_management.db')
    cursor = conn.cursor()
    
    today = datetime.now().date()
    warning_date = today + timedelta(days=7)
    
    cursor.execute('''
        SELECT name, email, end_date 
        FROM members 
        WHERE end_date <= ? AND status = 'active'
        ORDER BY end_date
    ''', (warning_date,))
    
    expiring_members = cursor.fetchall()
    conn.close()
    
    return expiring_members

# 운동 계획 추천
def recommend_workout_plan(member_id):
    conn = sqlite3.connect('gym_management.db')
    cursor = conn.cursor()
    
    # 최근 운동 기록 분석
    cursor.execute('''
        SELECT exercise_name, AVG(weight) as avg_weight, COUNT(*) as frequency
        FROM workout_records 
        WHERE member_id = ? AND date >= ?
        GROUP BY exercise_name
        ORDER BY frequency DESC
    ''', (member_id, (datetime.now() - timedelta(days=30)).date()))
    
    recent_exercises = cursor.fetchall()
    conn.close()
    
    recommendations = []
    
    if not recent_exercises:
        recommendations = [
            "초보자 추천: 기본 스쿼트 3세트 10회",
            "초보자 추천: 푸쉬업 3세트 8회",
            "초보자 추천: 런닝머신 20분"
        ]
    else:
        for exercise, avg_weight, freq in recent_exercises[:3]:
            new_weight = avg_weight * 1.05 if avg_weight else 0
            recommendations.append(f"{exercise}: {int(new_weight)}kg 3세트 8-10회")
    
    return recommendations

# Streamlit 앱 메인
def main():
    st.set_page_config(page_title="뼈는 남기고 살만 빼줄께", page_icon="🦴", layout="wide")
    
    # 데이터베이스 초기화
    init_database()
    insert_sample_data()
    
    # 헤더 및 로고
    col1, col2 = st.columns([1, 4])
    with col1:
        # 로고 디자인 (ASCII 아트 스타일)
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); border-radius: 15px; margin-bottom: 20px;'>
            <div style='font-size: 60px; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>🦴💪</div>
            <div style='font-size: 12px; color: white; font-weight: bold; margin-top: 5px;'>BONE GYM</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='padding: 20px;'>
            <h1 style='color: #2c3e50; margin-bottom: 10px; font-size: 2.5em;'>🦴 뼈는 남기고 살만 빼줄께</h1>
            <h3 style='color: #7f8c8d; margin-top: 0;'>💪 회원 관리 시스템</h3>
            <p style='color: #95a5a6; font-style: italic;'>"건강한 뼈, 탄탄한 근육, 완벽한 몸매를 만들어드립니다!"</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 메인 탭 메뉴
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 대시보드", 
        "👥 회원 관리", 
        "🏃‍♂️ 운동 기록", 
        "📅 수업 예약", 
        "👨‍🏫 트레이너 관리", 
        "📊 분석 리포트"
    ])
    
    with tab1:
        show_dashboard()
    with tab2:
        show_member_management()
    with tab3:
        show_workout_records()
    with tab4:
        show_class_booking()
    with tab5:
        show_trainer_management()
    with tab6:
        show_analytics()

def show_dashboard():
    st.header("📊 대시보드")
    
    # 새로고침 버튼
    col_refresh, col_space = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 새로고침", key="dashboard_refresh"):
            st.rerun()
    
    conn = sqlite3.connect('gym_management.db')
    
    # 주요 지표
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_members = pd.read_sql("SELECT COUNT(*) as count FROM members WHERE status='active'", conn)['count'][0]
        st.metric("활성 회원 수", total_members)
    
    with col2:
        total_trainers = pd.read_sql("SELECT COUNT(*) as count FROM trainers WHERE status='active'", conn)['count'][0]
        st.metric("트레이너 수", total_trainers)
    
    with col3:
        today_workouts = pd.read_sql(
            "SELECT COUNT(*) as count FROM workout_records WHERE date = ?", 
            conn, params=[datetime.now().date()]
        )['count'][0]
        st.metric("오늘 운동 기록", today_workouts)
    
    with col4:
        upcoming_classes = pd.read_sql(
            "SELECT COUNT(*) as count FROM classes WHERE date >= ?", 
            conn, params=[datetime.now().date()]
        )['count'][0]
        st.metric("예정된 수업", upcoming_classes)
    
    # 회원권 만료 알림
    st.subheader("⚠️ 회원권 만료 알림")
    expiring_members = check_membership_expiry()
    
    if expiring_members:
        for name, email, end_date in expiring_members:
            days_left = (datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.now().date()).days
            if days_left <= 0:
                st.error(f"⛔ {name} ({email}) - 회원권 만료됨!")
            else:
                st.warning(f"⚠️ {name} ({email}) - {days_left}일 후 만료")
    else:
        st.success("만료 예정 회원권이 없습니다.")
    
    conn.close()

def show_member_management():
    st.header("👥 회원 관리")
    
    # 새로고침 버튼
    col_refresh, col_space = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 새로고침", key="member_refresh"):
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["회원 목록", "회원 등록", "회원 삭제"])
    
    with tab1:
        conn = sqlite3.connect('gym_management.db')
        members_df = pd.read_sql("SELECT * FROM members", conn)
        conn.close()
        
        # 인덱스를 1부터 시작하도록 설정
        members_df.index = members_df.index + 1
        st.dataframe(members_df, use_container_width=True)
    
    with tab2:
        st.subheader("새 회원 등록")
        
        with st.form("member_registration"):
            name = st.text_input("이름")
            email = st.text_input("이메일")
            phone = st.text_input("전화번호")
            membership_type = st.selectbox("회원권 종류", ["일반", "프리미엄", "VIP"], key="member_registration_membership_type")
            start_date = st.date_input("시작일")
            
            # 회원권 기간 설정
            if membership_type == "일반":
                duration = 180  # 6개월
            elif membership_type == "프리미엄":
                duration = 365  # 1년
            else:  # VIP
                duration = 730  # 2년
            
            end_date = start_date + timedelta(days=duration)
            st.write(f"만료일: {end_date}")
            
            submitted = st.form_submit_button("등록")
            
            if submitted and name and email:
                conn = sqlite3.connect('gym_management.db')
                cursor = conn.cursor()
                
                try:
                    cursor.execute('''
                        INSERT INTO members (name, email, phone, membership_type, start_date, end_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (name, email, phone, membership_type, start_date, end_date))
                    conn.commit()
                    st.success("회원이 성공적으로 등록되었습니다!")
                    st.info("🔄 새로고침 버튼을 눌러 목록을 업데이트하세요.")
                except sqlite3.IntegrityError:
                    st.error("이미 등록된 이메일입니다.")
                
                conn.close()
    
    with tab3:
        st.subheader("🗑️ 회원 삭제")
        
        conn = sqlite3.connect('gym_management.db')
        
        # 회원 목록 조회
        members_df = pd.read_sql("SELECT * FROM members WHERE status='active'", conn)
        
        if not members_df.empty:
            # 인덱스를 1부터 시작하도록 설정
            members_df.index = members_df.index + 1
            st.dataframe(members_df, use_container_width=True)
            
            # 삭제할 회원 선택
            member_id = st.selectbox("삭제할 회원 선택", options=members_df['id'].tolist(),
                                   format_func=lambda x: f"{members_df[members_df['id']==x]['name'].iloc[0]} ({members_df[members_df['id']==x]['email'].iloc[0]})", 
                                   key="member_delete_select")
            
            if st.button("회원 삭제", type="secondary"):
                cursor = conn.cursor()
                
                # 회원 상태를 'inactive'로 변경 (완전 삭제 대신)
                cursor.execute("UPDATE members SET status = 'inactive' WHERE id = ?", (member_id,))
                
                conn.commit()
                st.success("회원이 비활성화되었습니다!")
                st.info("🔄 새로고침 버튼을 눌러 목록을 업데이트하세요.")
        else:
            st.info("삭제할 회원이 없습니다.")
        
        conn.close()

def show_workout_records():
    st.header("🏃‍♂️ 운동 기록")
    
    # 새로고침 버튼
    col_refresh, col_space = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 새로고침", key="workout_refresh"):
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["운동 기록 조회", "운동 기록 추가", "개인 운동 계획", "운동 기록 삭제"])
    
    with tab1:
        conn = sqlite3.connect('gym_management.db')
        
        # 회원 선택
        members_df = pd.read_sql("SELECT id, name FROM members WHERE status='active'", conn)
        member_options = {f"{row['name']} (ID: {row['id']})": row['id'] for _, row in members_df.iterrows()}
        
        selected_member = st.selectbox("회원 선택", options=list(member_options.keys()), key="workout_records_member_select")
        
        if selected_member:
            member_id = member_options[selected_member]
            
            # 운동 기록 조회
            workout_df = pd.read_sql('''
                SELECT exercise_name, sets, reps, weight, duration, calories_burned, date
                FROM workout_records 
                WHERE member_id = ?
                ORDER BY date DESC
            ''', conn, params=[member_id])
            
            if not workout_df.empty:
                # 인덱스를 1부터 시작하도록 설정
                workout_df.index = workout_df.index + 1
                st.dataframe(workout_df, use_container_width=True)
                
                # 운동 효과 시각화
                st.subheader("📈 운동 효과 분석")
                
                # 칼로리 소모 추이
                daily_calories = workout_df.groupby('date')['calories_burned'].sum().reset_index()
                fig_calories = px.line(daily_calories, x='date', y='calories_burned', 
                                     title='일별 칼로리 소모량')
                st.plotly_chart(fig_calories, use_container_width=True)
                
                # 운동별 빈도
                exercise_freq = workout_df['exercise_name'].value_counts()
                fig_freq = px.pie(values=exercise_freq.values, names=exercise_freq.index, 
                                title='운동별 빈도')
                st.plotly_chart(fig_freq, use_container_width=True)
            else:
                st.info("운동 기록이 없습니다.")
        
        conn.close()
    
    with tab2:
        st.subheader("운동 기록 추가")
        
        conn = sqlite3.connect('gym_management.db')
        members_df = pd.read_sql("SELECT id, name FROM members WHERE status='active'", conn)
        conn.close()
        
        with st.form("workout_record"):
            member_id = st.selectbox("회원", options=members_df['id'].tolist(), 
                                   format_func=lambda x: members_df[members_df['id']==x]['name'].iloc[0], key="workout_record_member_select")
            exercise_name = st.selectbox("운동", 
                                       ["벤치프레스", "스쿼트", "데드리프트", "풀업", "푸쉬업", "런닝머신", "사이클"], key="workout_record_exercise_select")
            sets = st.number_input("세트", min_value=1, max_value=10, value=3)
            reps = st.number_input("횟수", min_value=1, max_value=50, value=10)
            weight = st.number_input("무게(kg)", min_value=0.0, value=20.0)
            duration = st.number_input("시간(분)", min_value=1, value=30)
            calories_burned = st.number_input("소모 칼로리", min_value=0, value=200)
            date = st.date_input("날짜", value=datetime.now().date())
            
            submitted = st.form_submit_button("기록 추가")
            
            if submitted:
                conn = sqlite3.connect('gym_management.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO workout_records 
                    (member_id, exercise_name, sets, reps, weight, duration, calories_burned, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (member_id, exercise_name, sets, reps, weight, duration, calories_burned, date))
                
                conn.commit()
                conn.close()
                st.success("운동 기록이 추가되었습니다!")
                st.info("🔄 새로고침 버튼을 눌러 기록을 확인하세요.")
    
    with tab3:
        st.subheader("🎯 개인 맞춤 운동 계획")
        
        conn = sqlite3.connect('gym_management.db')
        members_df = pd.read_sql("SELECT id, name FROM members WHERE status='active'", conn)
        conn.close()
        
        member_id = st.selectbox("회원 선택", options=members_df['id'].tolist(), 
                               format_func=lambda x: members_df[members_df['id']==x]['name'].iloc[0], key="workout_plan_member_select")
        
        if st.button("운동 계획 생성"):
            recommendations = recommend_workout_plan(member_id)
            
            st.write("### 추천 운동 계획:")
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
    
    with tab4:
        st.subheader("🗑️ 운동 기록 삭제")
        
        conn = sqlite3.connect('gym_management.db')
        
        # 운동 기록 목록 조회
        workout_records_df = pd.read_sql('''
            SELECT wr.id, m.name as member_name, wr.exercise_name, wr.sets, wr.reps, 
                   wr.weight, wr.duration, wr.calories_burned, wr.date
            FROM workout_records wr
            JOIN members m ON wr.member_id = m.id
            ORDER BY wr.date DESC
        ''', conn)
        
        if not workout_records_df.empty:
            # 인덱스를 1부터 시작하도록 설정
            workout_records_df.index = workout_records_df.index + 1
            st.dataframe(workout_records_df, use_container_width=True)
            
            # 삭제할 기록 선택
            record_id = st.selectbox("삭제할 운동 기록 선택", options=workout_records_df['id'].tolist(),
                                   format_func=lambda x: f"{workout_records_df[workout_records_df['id']==x]['member_name'].iloc[0]} - {workout_records_df[workout_records_df['id']==x]['exercise_name'].iloc[0]} ({workout_records_df[workout_records_df['id']==x]['date'].iloc[0]})", 
                                   key="workout_record_delete_select")
            
            if st.button("운동 기록 삭제", type="secondary"):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM workout_records WHERE id = ?", (record_id,))
                conn.commit()
                st.success("운동 기록이 삭제되었습니다!")
                st.info("🔄 새로고침 버튼을 눌러 목록을 업데이트하세요.")
        else:
            st.info("삭제할 운동 기록이 없습니다.")
        
        conn.close()

def show_class_booking():
    st.header("📅 수업 예약 관리")
    
    # 새로고침 버튼
    col_refresh, col_space = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 새로고침", key="class_refresh"):
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["수업 예약", "수업 관리", "수업 삭제"])
    
    with tab1:
        st.subheader("수업 예약")
        
        conn = sqlite3.connect('gym_management.db')
        
        # 예약 가능한 수업 조회
        classes_df = pd.read_sql('''
            SELECT c.id, c.class_name, t.name as trainer_name, c.date, c.time, 
                   c.duration, c.max_capacity, c.current_bookings,
                   (c.max_capacity - c.current_bookings) as available_spots
            FROM classes c
            JOIN trainers t ON c.trainer_id = t.id
            WHERE c.date >= date('now')
            ORDER BY c.date, c.time
        ''', conn)
        
        if not classes_df.empty:
            # 인덱스를 1부터 시작하도록 설정
            classes_df.index = classes_df.index + 1
            st.dataframe(classes_df, use_container_width=True)
            
            # 예약하기
            class_id = st.selectbox("수업 선택", options=classes_df['id'].tolist(),
                                  format_func=lambda x: f"{classes_df[classes_df['id']==x]['class_name'].iloc[0]} - {classes_df[classes_df['id']==x]['date'].iloc[0]} {classes_df[classes_df['id']==x]['time'].iloc[0]}", key="class_booking_class_select")
            
            members_df = pd.read_sql("SELECT id, name FROM members WHERE status='active'", conn)
            member_id = st.selectbox("회원 선택", options=members_df['id'].tolist(),
                                   format_func=lambda x: members_df[members_df['id']==x]['name'].iloc[0], key="class_booking_member_select")
            
            if st.button("예약하기"):
                cursor = conn.cursor()
                
                # 예약 가능 여부 확인
                cursor.execute("SELECT max_capacity, current_bookings FROM classes WHERE id = ?", (class_id,))
                capacity, current = cursor.fetchone()
                
                if current < capacity:
                    cursor.execute('''
                        INSERT INTO bookings (member_id, class_id, booking_date)
                        VALUES (?, ?, ?)
                    ''', (member_id, class_id, datetime.now().date()))
                    
                    cursor.execute('''
                        UPDATE classes SET current_bookings = current_bookings + 1 WHERE id = ?
                    ''', (class_id,))
                    
                    conn.commit()
                    st.success("예약이 완료되었습니다!")
                    st.info("🔄 새로고침 버튼을 눌러 예약 현황을 확인하세요.")
                else:
                    st.error("수업이 만석입니다.")
        else:
            st.info("예약 가능한 수업이 없습니다.")
        
        conn.close()
    
    with tab2:
        st.subheader("수업 관리")
        
        with st.form("add_class"):
            st.write("새 수업 추가")
            
            conn = sqlite3.connect('gym_management.db')
            trainers_df = pd.read_sql("SELECT id, name, specialty FROM trainers WHERE status='active'", conn)
            conn.close()
            
            class_name = st.text_input("수업명")
            trainer_id = st.selectbox("트레이너", options=trainers_df['id'].tolist(),
                                    format_func=lambda x: f"{trainers_df[trainers_df['id']==x]['name'].iloc[0]} ({trainers_df[trainers_df['id']==x]['specialty'].iloc[0]})", key="class_management_trainer_select")
            date = st.date_input("날짜")
            time = st.time_input("시간")
            duration = st.number_input("시간(분)", min_value=30, max_value=180, value=60)
            max_capacity = st.number_input("최대 인원", min_value=1, max_value=30, value=10)
            
            submitted = st.form_submit_button("수업 추가")
            
            if submitted and class_name:
                conn = sqlite3.connect('gym_management.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO classes (class_name, trainer_id, date, time, duration, max_capacity)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (class_name, trainer_id, date, time.strftime('%H:%M'), duration, max_capacity))
                
                conn.commit()
                conn.close()
                st.success("수업이 추가되었습니다!")
                st.info("🔄 새로고침 버튼을 눌러 수업 목록을 확인하세요.")
    
    with tab3:
        st.subheader("🗑️ 수업 삭제")
        
        conn = sqlite3.connect('gym_management.db')
        
        # 수업 목록 조회
        classes_df = pd.read_sql('''
            SELECT c.id, c.class_name, t.name as trainer_name, c.date, c.time, 
                   c.duration, c.max_capacity, c.current_bookings
            FROM classes c
            JOIN trainers t ON c.trainer_id = t.id
            ORDER BY c.date DESC, c.time DESC
        ''', conn)
        
        if not classes_df.empty:
            # 인덱스를 1부터 시작하도록 설정
            classes_df.index = classes_df.index + 1
            st.dataframe(classes_df, use_container_width=True)
            
            # 삭제할 수업 선택
            class_id = st.selectbox("삭제할 수업 선택", options=classes_df['id'].tolist(),
                                  format_func=lambda x: f"{classes_df[classes_df['id']==x]['class_name'].iloc[0]} - {classes_df[classes_df['id']==x]['trainer_name'].iloc[0]} ({classes_df[classes_df['id']==x]['date'].iloc[0]} {classes_df[classes_df['id']==x]['time'].iloc[0]})", 
                                  key="class_delete_select")
            
            if st.button("수업 삭제", type="secondary"):
                cursor = conn.cursor()
                
                # 관련 예약도 함께 삭제
                cursor.execute("DELETE FROM bookings WHERE class_id = ?", (class_id,))
                cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
                
                conn.commit()
                st.success("수업과 관련 예약이 삭제되었습니다!")
                st.info("🔄 새로고침 버튼을 눌러 목록을 업데이트하세요.")
        else:
            st.info("삭제할 수업이 없습니다.")
        
        conn.close()

def show_trainer_management():
    st.header("👨‍🏫 트레이너 관리")
    
    # 새로고침 버튼
    col_refresh, col_space = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 새로고침", key="trainer_refresh"):
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["트레이너 목록", "트레이너 등록", "트레이너 삭제"])
    
    with tab1:
        conn = sqlite3.connect('gym_management.db')
        trainers_df = pd.read_sql("SELECT * FROM trainers", conn)
        conn.close()
        
        # 인덱스를 1부터 시작하도록 설정
        trainers_df.index = trainers_df.index + 1
        st.dataframe(trainers_df, use_container_width=True)
    
    with tab2:
        st.subheader("새 트레이너 등록")
        
        with st.form("trainer_registration"):
            name = st.text_input("이름")
            specialty = st.selectbox("전문 분야", 
                                   ["웨이트 트레이닝", "요가/필라테스", "크로스핏", "수영", "복싱", "댄스"], key="trainer_registration_specialty")
            experience_years = st.number_input("경력(년)", min_value=0, max_value=30, value=1)
            rating = st.slider("평점", 1.0, 5.0, 4.5, 0.1)
            
            submitted = st.form_submit_button("등록")
            
            if submitted and name:
                conn = sqlite3.connect('gym_management.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO trainers (name, specialty, experience_years, rating)
                    VALUES (?, ?, ?, ?)
                ''', (name, specialty, experience_years, rating))
                
                conn.commit()
                conn.close()
                st.success("트레이너가 등록되었습니다!")
                st.info("🔄 새로고침 버튼을 눌러 목록을 업데이트하세요.")
    
    with tab3:
        st.subheader("🗑️ 트레이너 삭제")
        
        conn = sqlite3.connect('gym_management.db')
        
        # 트레이너 목록 조회
        trainers_df = pd.read_sql("SELECT * FROM trainers WHERE status='active'", conn)
        
        if not trainers_df.empty:
            # 인덱스를 1부터 시작하도록 설정
            trainers_df.index = trainers_df.index + 1
            st.dataframe(trainers_df, use_container_width=True)
            
            # 삭제할 트레이너 선택
            trainer_id = st.selectbox("삭제할 트레이너 선택", options=trainers_df['id'].tolist(),
                                    format_func=lambda x: f"{trainers_df[trainers_df['id']==x]['name'].iloc[0]} ({trainers_df[trainers_df['id']==x]['specialty'].iloc[0]})", 
                                    key="trainer_delete_select")
            
            if st.button("트레이너 삭제", type="secondary"):
                cursor = conn.cursor()
                
                # 트레이너 상태를 'inactive'로 변경 (완전 삭제 대신)
                cursor.execute("UPDATE trainers SET status = 'inactive' WHERE id = ?", (trainer_id,))
                
                conn.commit()
                st.success("트레이너가 비활성화되었습니다!")
                st.info("🔄 새로고침 버튼을 눌러 목록을 업데이트하세요.")
        else:
            st.info("삭제할 트레이너가 없습니다.")
        
        conn.close()

def show_analytics():
    st.header("📊 분석 리포트")
    
    # 새로고침 버튼
    col_refresh, col_space = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 새로고침", key="analytics_refresh"):
            st.rerun()
    
    conn = sqlite3.connect('gym_management.db')
    
    # 회원 현황 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 회원권 유형별 분포")
        membership_stats = pd.read_sql('''
            SELECT membership_type, COUNT(*) as count
            FROM members 
            WHERE status = 'active'
            GROUP BY membership_type
        ''', conn)
        
        if not membership_stats.empty:
            # 도넛 차트로 변경
            fig_membership = px.pie(membership_stats, values='count', names='membership_type', 
                                  title='회원권 유형별 분포', hole=0.4,
                                  color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
            fig_membership.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_membership, use_container_width=True)
    
    with col2:
        st.subheader("⭐ 트레이너 평점 분포")
        trainer_ratings = pd.read_sql('''
            SELECT name, rating, specialty
            FROM trainers 
            WHERE status = 'active'
            ORDER BY rating DESC
        ''', conn)
        
        if not trainer_ratings.empty:
            # 막대 차트
            fig_ratings = px.bar(trainer_ratings, x='name', y='rating', 
                               color='specialty', title='트레이너별 평점',
                               color_discrete_sequence=['#FF9F43', '#10AC84', '#EE5A24', '#0ABDE3'])
            fig_ratings.update_layout(xaxis_title='트레이너', yaxis_title='평점')
            st.plotly_chart(fig_ratings, use_container_width=True)
    
    # 월별 운동 활동 분석
    st.subheader("📈 월별 운동 활동 추이")
    monthly_workouts = pd.read_sql('''
        SELECT strftime('%Y-%m', date) as month, 
               COUNT(*) as workout_count,
               AVG(calories_burned) as avg_calories,
               SUM(calories_burned) as total_calories
        FROM workout_records
        GROUP BY month
        ORDER BY month
    ''', conn)
    
    if not monthly_workouts.empty:
        # 복합 차트 (막대 + 선)
        fig_monthly = go.Figure()
        
        # 운동 횟수 (막대)
        fig_monthly.add_trace(go.Bar(
            x=monthly_workouts['month'], 
            y=monthly_workouts['workout_count'],
            name='운동 횟수',
            marker_color='#4ECDC4',
            yaxis='y'
        ))
        
        # 평균 칼로리 (선)
        fig_monthly.add_trace(go.Scatter(
            x=monthly_workouts['month'], 
            y=monthly_workouts['avg_calories'],
            mode='lines+markers',
            name='평균 칼로리',
            line=dict(color='#FF6B6B', width=3),
            yaxis='y2'
        ))
        
        fig_monthly.update_layout(
            title='월별 운동 활동 및 칼로리 소모 추이',
            xaxis_title='월',
            yaxis=dict(title='운동 횟수', side='left'),
            yaxis2=dict(title='평균 칼로리', side='right', overlaying='y'),
            hovermode='x unified'
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # 운동별 분석
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🏆 인기 운동 TOP 10")
        popular_exercises = pd.read_sql('''
            SELECT exercise_name, COUNT(*) as frequency,
                   AVG(weight) as avg_weight,
                   AVG(calories_burned) as avg_calories
            FROM workout_records
            GROUP BY exercise_name
            ORDER BY frequency DESC
            LIMIT 10
        ''', conn)
        
        if not popular_exercises.empty:
            # 수평 막대 차트
            fig_popular = px.bar(popular_exercises, 
                               x='frequency', y='exercise_name',
                               title='인기 운동 순위',
                               orientation='h',
                               color='frequency',
                               color_continuous_scale='Viridis')
            fig_popular.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_popular, use_container_width=True)
    
    with col4:
        st.subheader("🔥 운동별 평균 칼로리 소모")
        calorie_by_exercise = pd.read_sql('''
            SELECT exercise_name, AVG(calories_burned) as avg_calories
            FROM workout_records
            GROUP BY exercise_name
            ORDER BY avg_calories DESC
            LIMIT 8
        ''', conn)
        
        if not calorie_by_exercise.empty:
            # 레이더 차트
            fig_calories = go.Figure()
            fig_calories.add_trace(go.Scatterpolar(
                r=calorie_by_exercise['avg_calories'],
                theta=calorie_by_exercise['exercise_name'],
                fill='toself',
                name='평균 칼로리',
                line_color='#FF6B6B'
            ))
            fig_calories.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, calorie_by_exercise['avg_calories'].max()*1.1])
                ),
                title='운동별 평균 칼로리 소모량'
            )
            st.plotly_chart(fig_calories, use_container_width=True)
    
    # 트레이너 및 수업 분석
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("👨‍🏫 트레이너별 수업 현황")
        trainer_classes = pd.read_sql('''
            SELECT t.name, t.specialty,
                   COUNT(c.id) as class_count, 
                   COALESCE(AVG(c.current_bookings), 0) as avg_bookings
            FROM trainers t
            LEFT JOIN classes c ON t.id = c.trainer_id
            WHERE t.status = 'active'
            GROUP BY t.id, t.name, t.specialty
        ''', conn)
        
        if not trainer_classes.empty:
            # 버블 차트
            fig_trainers = px.scatter(trainer_classes, 
                                    x='class_count', y='avg_bookings',
                                    size='class_count', color='specialty',
                                    hover_name='name',
                                    title='트레이너별 수업 수 vs 평균 예약자 수',
                                    size_max=60)
            fig_trainers.update_layout(
                xaxis_title='수업 수',
                yaxis_title='평균 예약자 수'
            )
            st.plotly_chart(fig_trainers, use_container_width=True)
    
    with col6:
        st.subheader("📅 시간대별 수업 현황")
        time_distribution = pd.read_sql('''
            SELECT 
                CASE 
                    WHEN CAST(substr(time, 1, 2) AS INTEGER) < 9 THEN '새벽 (06-09)'
                    WHEN CAST(substr(time, 1, 2) AS INTEGER) < 12 THEN '오전 (09-12)'
                    WHEN CAST(substr(time, 1, 2) AS INTEGER) < 15 THEN '점심 (12-15)'
                    WHEN CAST(substr(time, 1, 2) AS INTEGER) < 18 THEN '오후 (15-18)'
                    ELSE '저녁 (18-22)'
                END as time_slot,
                COUNT(*) as class_count,
                AVG(current_bookings) as avg_bookings
            FROM classes
            GROUP BY time_slot
            ORDER BY avg_bookings DESC
        ''', conn)
        
        if not time_distribution.empty:
            # 선버스트 차트 대신 간단한 파이 차트
            fig_time = px.pie(time_distribution, 
                            values='class_count', names='time_slot',
                            title='시간대별 수업 분포',
                            color_discrete_sequence=['#FF9F43', '#10AC84', '#EE5A24', '#0ABDE3', '#A55EEA'])
            st.plotly_chart(fig_time, use_container_width=True)
    
    # 회원 활동 히트맵
    st.subheader("🔥 요일별 운동 활동 히트맵")
    activity_heatmap = pd.read_sql('''
        SELECT 
            CASE CAST(strftime('%w', date) AS INTEGER)
                WHEN 0 THEN '일요일'
                WHEN 1 THEN '월요일'
                WHEN 2 THEN '화요일'
                WHEN 3 THEN '수요일'
                WHEN 4 THEN '목요일'
                WHEN 5 THEN '금요일'
                WHEN 6 THEN '토요일'
            END as weekday,
            CASE 
                WHEN CAST(substr(date, 9, 2) AS INTEGER) <= 7 THEN '1주차'
                WHEN CAST(substr(date, 9, 2) AS INTEGER) <= 14 THEN '2주차'
                WHEN CAST(substr(date, 9, 2) AS INTEGER) <= 21 THEN '3주차'
                ELSE '4주차'
            END as week,
            COUNT(*) as workout_count
        FROM workout_records
        WHERE date >= date('now', '-30 days')
        GROUP BY weekday, week
    ''', conn)
    
    if not activity_heatmap.empty:
        # 피벗 테이블 생성
        heatmap_pivot = activity_heatmap.pivot(index='weekday', columns='week', values='workout_count').fillna(0)
        
        # 요일 순서 정렬
        day_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        heatmap_pivot = heatmap_pivot.reindex(day_order)
        
        # 히트맵
        fig_heatmap = px.imshow(heatmap_pivot.values,
                              x=heatmap_pivot.columns,
                              y=heatmap_pivot.index,
                              color_continuous_scale='YlOrRd',
                              title='요일별/주차별 운동 활동량')
        fig_heatmap.update_xaxes(title='주차')
        fig_heatmap.update_yaxes(title='요일')
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    conn.close()

if __name__ == "__main__":
    main()