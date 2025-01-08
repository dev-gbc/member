import pytest
from datetime import datetime
from src.scheduler import ChurchScheduler

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

def test_create_schedule_dataframe():
    scheduler = ChurchScheduler()
    
    # 테스트용 일요일 날짜들
    test_dates = [
        datetime(2024, 1, 7),
        datetime(2024, 1, 14)
    ]
    
    df = scheduler.create_schedule_dataframe(test_dates)
    
    # DataFrame 구조 검증
    assert len(df) == 2
    assert list(df.columns) == ['날짜', '헌금위원', '내부안내']
    assert df['날짜'].tolist() == ['2024-01-07', '2024-01-14']
    assert all(df['헌금위원'] == '')
    assert all(df['내부안내'] == '')