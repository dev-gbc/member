import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

class ChurchScheduler:
    def __init__(self):
        self.assignments: Dict[str, List[str]] = {
            'offering': [],  # 헌금위원 배정 기록
            'guide': []      # 내부안내위원 배정 기록
        }
    
    def generate_sundays(self, start_date: str, end_date: str = None) -> List[datetime]:
        """주어진 기간의 모든 일요일 날짜를 생성합니다.
        
        Args:
            start_date: 시작 날짜 (YYYY-MM-DD 형식)
            end_date: 종료 날짜 (YYYY-MM-DD 형식, 기본값: 해당 연도 12월 31일)
            
        Returns:
            List[datetime]: 해당 기간의 모든 일요일 날짜 리스트
        """
        # 시작 날짜 파싱
        start = datetime.strptime(start_date, '%Y-%m-%d')
        
        # 종료 날짜가 지정되지 않은 경우 해당 연도 말까지로 설정
        if end_date is None:
            end = datetime(start.year, 12, 31)
        else:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
        # 첫 번째 일요일 찾기
        current = start
        while current.weekday() != 6:  # 0=월요일, 6=일요일
            current += timedelta(days=1)
            
        # 모든 일요일 수집
        sundays = []
        while current <= end:
            sundays.append(current)
            current += timedelta(days=7)
            
        return sundays
    
    def format_schedule_date(self, date: datetime) -> str:
        """날짜를 'YYYY-MM-DD' 형식의 문자열로 변환합니다."""
        return date.strftime('%Y-%m-%d')
    
    def create_schedule_dataframe(self, sundays: List[datetime]) -> pd.DataFrame:
        """주어진 일요일 목록으로 빈 스케줄 DataFrame을 생성합니다."""
        schedule_data = {
            '날짜': [self.format_schedule_date(sunday) for sunday in sundays],
            '헌금위원': [''] * len(sundays),
            '내부안내': [''] * len(sundays)
        }
        return pd.DataFrame(schedule_data)