import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Set
import random

class TeamBasedScheduler:
    def __init__(self):
        self.staff_data = None
        self.offering_teams = []  # 헌금위원 팀 목록
        self.guide_pool = []      # 내부안내위원 풀
        self.last_team_index = -1
        self.last_guide_index = -1
        
    def load_staff_data(self, df: pd.DataFrame) -> None:
        """교인 데이터를 로드하고 팀을 구성합니다."""
        self.staff_data = df
        self._create_offering_teams()
        self._create_guide_pool()
        
    def _create_offering_teams(self) -> None:
        """헌금위원 팀을 구성합니다."""
        # 헌금위원 후보 필터링
        candidates = self.staff_data[
            (self.staff_data['직책'].isin(['임원', '리더'])) & 
            (~self.staff_data['소속'].str.contains('서기', na=False))
        ]['이름'].tolist()
        
        # 3명씩 팀 구성
        random.shuffle(candidates)  # 랜덤하게 섞기
        self.offering_teams = []
        for i in range(0, len(candidates), 3):
            team = candidates[i:i+3]
            if len(team) == 3:  # 3명이 되는 팀만 추가
                self.offering_teams.append(team)
                
    def _create_guide_pool(self) -> None:
        """내부안내위원 풀을 생성합니다."""
        self.guide_pool = self.staff_data[
            (self.staff_data['직책'].isin(['임원', '리더', '에벤에셀'])) & 
            (~self.staff_data['소속'].str.contains('아동부|찬양팀', na=False))
        ]['이름'].tolist()
        random.shuffle(self.guide_pool)  # 가이드 풀도 랜덤하게 섞기
        
    def get_next_offering_team(self) -> List[str]:
        """다음 헌금위원 팀을 순환하여 반환합니다."""
        self.last_team_index = (self.last_team_index + 1) % len(self.offering_teams)
        return self.offering_teams[self.last_team_index]
        
    def get_next_guide(self, current_offering_team: List[str]) -> str:
        """다음 내부안내위원을 순환하여 반환합니다.
        현재 헌금위원으로 배정된 사람은 제외합니다."""
        original_index = self.last_guide_index
        
        while True:
            self.last_guide_index = (self.last_guide_index + 1) % len(self.guide_pool)
            candidate = self.guide_pool[self.last_guide_index]
            
            # 현재 헌금위원이 아닌 경우에만 선택
            if candidate not in current_offering_team:
                return candidate
                
            # 한바퀴 돌았는데도 적절한 후보를 못 찾은 경우
            if self.last_guide_index == original_index:
                raise ValueError("모든 가능한 내부안내위원이 현재 헌금위원으로 배정되어 있습니다.")
    
    def generate_sundays(self, start_date: str, end_date: str = None) -> List[datetime]:
        """주어진 기간의 모든 일요일 날짜를 생성합니다."""
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
    
    def generate_schedule(self, sundays: List[datetime]) -> pd.DataFrame:
        """주어진 일요일 목록으로 스케줄을 생성합니다."""
        if not self.offering_teams or not self.guide_pool:
            raise ValueError("팀이 구성되지 않았습니다. load_staff_data()를 먼저 호출하세요.")
            
        schedule_data = {
            '날짜': [sunday.strftime('%Y-%m-%d') for sunday in sundays],
            '헌금위원': [],
            '내부안내': []
        }
        
        # 각 주별로 팀 선택
        for _ in sundays:
            offering_team = self.get_next_offering_team()
            try:
                guide = self.get_next_guide(offering_team)  # 현재 헌금위원 목록 전달
                schedule_data['헌금위원'].append(', '.join(offering_team))
                schedule_data['내부안내'].append(guide)
            except ValueError as e:
                print(f"경고: {e}")
                # 에러 발생 시 가이드 풀을 다시 섞고 재시도
                random.shuffle(self.guide_pool)
                self.last_guide_index = -1
                guide = self.get_next_guide(offering_team)
                schedule_data['헌금위원'].append(', '.join(offering_team))
                schedule_data['내부안내'].append(guide)
            
        return pd.DataFrame(schedule_data)

    def print_team_info(self) -> None:
        """현재 구성된 팀 정보를 출력합니다."""
        print("\n=== 헌금위원 팀 구성 ===")
        for i, team in enumerate(self.offering_teams, 1):
            print(f"팀 {i}: {', '.join(team)}")
            
        print("\n=== 내부안내위원 풀 ===")
        print(', '.join(self.guide_pool))