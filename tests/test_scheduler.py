import pytest
import pandas as pd
from datetime import datetime
from src.scheduler import ChurchScheduler

@pytest.fixture
def staff_data():
    """테스트용 교인 데이터"""
    return pd.DataFrame({
        '이름': ['김철수', '이영희', '박지성', '최민수', '정태준', 
                '강다희', '윤서연', '한미영', '송재욱', '임수진'],
        '직책': ['임원', '리더', '임원', '에벤에셀', '리더',
                '임원', '리더', '임원', '리더', '에벤에셀'],
        '소속': ['찬양팀', '아동부,서기', '아동부', '서기', '찬양팀',
                '아동부', '찬양팀,서기', '아동부', '찬양팀', '서기']
    })

@pytest.fixture
def scheduler(staff_data):
    """테스트용 스케줄러"""
    scheduler = ChurchScheduler()
    scheduler.load_staff_data(staff_data)
    return scheduler

def test_generate_sundays():
    scheduler = ChurchScheduler()
    
    # 2024년 1월의 일요일들 테스트
    sundays = scheduler.generate_sundays('2024-01-01', '2024-01-31')
    expected_dates = ['2024-01-07', '2024-01-14', '2024-01-21', '2024-01-28']
    
    assert len(sundays) == 4
    for sunday, expected in zip(sundays, expected_dates):
        assert sunday.strftime('%Y-%m-%d') == expected

def test_generate_sundays_year_end():
    scheduler = ChurchScheduler()
    
    # 종료 날짜 미지정 시 연말까지 계산
    sundays = scheduler.generate_sundays('2024-12-01')
    expected_dates = ['2024-12-01', '2024-12-08', '2024-12-15', 
                     '2024-12-22', '2024-12-29']
    
    assert len(sundays) == 5
    for sunday, expected in zip(sundays, expected_dates):
        assert sunday.strftime('%Y-%m-%d') == expected

def test_get_offering_candidates(scheduler, staff_data):
    """헌금위원 후보 필터링 테스트"""
    candidates = scheduler.get_offering_candidates()
    
    # 임원/리더이면서 서기가 아닌 사람만 선택되어야 함
    for _, row in candidates.iterrows():
        assert row['직책'] in ['임원', '리더']
        assert '서기' not in str(row['소속'])

def test_get_guide_candidates(scheduler, staff_data):
    """내부안내위원 후보 필터링 테스트"""
    candidates = scheduler.get_guide_candidates()
    
    # 임원/리더/에벤에셀이면서 아동부/찬양팀이 아닌 사람만 선택되어야 함
    for _, row in candidates.iterrows():
        assert row['직책'] in ['임원', '리더', '에벤에셀']
        assert not any(dept in str(row['소속']) for dept in ['아동부', '찬양팀'])

def test_select_staff(scheduler):
    """인원 선택 로직 테스트"""
    candidates = pd.DataFrame({
        '이름': ['A', 'B', 'C', 'D'],
        '직책': ['임원'] * 4,
        '소속': [''] * 4
    })
    
    # 이전 배정 기록이 있는 경우
    history = ['A', 'B']
    selected = scheduler.select_staff(candidates, 2, history)
    
    # 최근에 선택되지 않은 사람이 우선 선택되어야 함
    assert 'C' in selected
    assert 'D' in selected

def test_create_schedule_dataframe(scheduler):
    """전체 스케줄 생성 테스트"""
    test_dates = [
        datetime(2024, 1, 7),
        datetime(2024, 1, 14)
    ]
    
    df = scheduler.create_schedule_dataframe(test_dates)
    
    # 기본 구조 검증
    assert len(df) == 2
    assert list(df.columns) == ['날짜', '헌금위원', '내부안내']
    assert df['날짜'].tolist() == ['2024-01-07', '2024-01-14']
    
    # 각 칸이 채워져 있는지 확인
    assert all(df['헌금위원'].str.count(',') == 2)  # 헌금위원 3명
    assert all(df['내부안내'].str.len() > 0)  # 내부안내위원 1명