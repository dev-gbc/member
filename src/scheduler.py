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
        self.staff_data = None  # 교인 데이터 DataFrame
        
    def load_staff_data(self, df: pd.DataFrame) -> None:
        """교인 데이터를 로드합니다."""
        self.staff_data = df
        
    def get_offering_candidates(self) -> pd.DataFrame:
        """헌금위원 후보를 필터링합니다.
        - 직책이 임원 또는 리더인 사람만 선택
        - 소속에 '서기'가 포함된 사람은 제외
        """
        if self.staff_data is None:
            raise ValueError("교인 데이터가 로드되지 않았습니다.")
            
        return self.staff_data[
            (self.staff_data['직책'].isin(['임원', '리더'])) & 
            (~self.staff_data['소속'].str.contains('서기', na=False))
        ].copy()
        
    def get_guide_candidates(self) -> pd.DataFrame:
        """내부안내위원 후보를 필터링합니다.
        - 직책이 임원, 리더, 에벤에셀인 사람만 선택
        - 소속에 '아동부' 또는 '찬양팀'이 포함된 사람은 제외
        """
        if self.staff_data is None:
            raise ValueError("교인 데이터가 로드되지 않았습니다.")
            
        return self.staff_data[
            (self.staff_data['직책'].isin(['임원', '리더', '에벤에셀'])) & 
            (~self.staff_data['소속'].str.contains('아동부|찬양팀', na=False))
        ].copy()
        
    def select_staff(self, 
                    candidates: pd.DataFrame, 
                    count: int, 
                    history: List[str]) -> List[str]:
        """후보자 중에서 지정된 수만큼 인원을 선택합니다.
        최근에 선택되지 않은 사람을 우선적으로 선택합니다.
        """
        # 후보자가 충분하지 않으면 에러
        if len(candidates) < count:
            raise ValueError(f"후보자가 부족합니다. (필요: {count}, 가능: {len(candidates)})")
        
        # 후보자들을 최근 선택 여부에 따라 정렬
        candidates = candidates.copy()
        candidates['last_selected'] = float('inf')
        
        for idx, name in enumerate(reversed(history)):
            if name in candidates['이름'].values:
                candidates.loc[candidates['이름'] == name, 'last_selected'] = idx
                
        candidates = candidates.sort_values('last_selected', ascending=False)
        
        # 필요한 수만큼 선택
        selected = candidates.head(count)
        return selected['이름'].tolist()
    
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
        """주어진 일요일 목록으로 스케줄 DataFrame을 생성합니다."""
        if self.staff_data is None:
            raise ValueError("교인 데이터가 로드되지 않았습니다.")
            
        schedule_data = {
            '날짜': [self.format_schedule_date(sunday) for sunday in sundays],
            '헌금위원': [],
            '내부안내': []
        }
        
        # 각 주별로 인원 선택
        for _ in sundays:
            # 헌금위원 선택 (3명)
            offering_candidates = self.get_offering_candidates()
            offering_staff = self.select_staff(offering_candidates, 3, self.assignments['offering'])
            self.assignments['offering'].extend(offering_staff)
            schedule_data['헌금위원'].append(','.join(offering_staff))
            
            # 내부안내위원 선택 (1명)
            guide_candidates = self.get_guide_candidates()
            guide_staff = self.select_staff(guide_candidates, 1, self.assignments['guide'])
            self.assignments['guide'].extend(guide_staff)
            schedule_data['내부안내'].append(guide_staff[0])
            
        return pd.DataFrame(schedule_data)