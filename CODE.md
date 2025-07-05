# member
## Project Structure

```
member/
├── src/
    ├── create_test_data.py
    ├── excel_handler.py
    ├── gui.py
    ├── main.py
    └── scheduler.py
└── tests/
    ├── test_excel.py
    └── test_scheduler.py
```

## src/create_test_data.py
```py
import pandas as pd
from pathlib import Path

def create_test_data():
    """테스트용 교인 데이터 생성"""
    data = {
        '이름': [
            '김성실', '이믿음', '박소망', '정사랑', '최기쁨',
            '강충성', '윤온유', '한겸손', '송인내', '임화평',
            '고은혜', '오진리', '서선한', '류지혜', '문축복'
        ],
        '직책': [
            '임원', '리더', '임원', '에벤에셀', '리더',
            '임원', '리더', '임원', '리더', '에벤에셀',
            '임원', '리더', '임원', '리더', '에벤에셀'
        ],
        '소속': [
            '찬양팀', '중보기도부', '새가족부', '서기,찬양팀', '차량부',
            '주차부', '재정부,아동부', '아동부,서기', '찬양팀', '새가족부',
            '차량부', '중보기도부', '재정부', '서기', '주차부'
        ]
    }
    
    # DataFrame 생성
    df = pd.DataFrame(data)
    
    # 데이터 디렉토리 생성
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 엑셀 파일로 저장
    output_path = data_dir / "test_data.xlsx"
    df.to_excel(output_path, index=False)
    print(f"테스트 데이터가 생성되었습니다: {output_path}")
    return output_path

if __name__ == '__main__':
    create_test_data()
```
## src/excel_handler.py
```py
import pandas as pd
from pathlib import Path

class ExcelHandler:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.generated_dir = self.data_dir / "generated"
        self.generated_dir.mkdir(exist_ok=True)

    def create_test_data(self):
        """테스트용 교인 데이터 생성"""
        data = {
            '이름': [
                '김철수', '이영희', '박지성', '최민수', '정태준', 
                '강다희', '윤서연', '한미영', '송재욱', '임수진'
            ],
            '직책': [
                '임원', '리더', '임원', '에벤에셀', '리더',
                '임원', '리더', '임원', '리더', '에벤에셀'
            ],
            '소속': [
                '찬양팀', '아동부,서기', '아동부', '서기', '찬양팀',
                '아동부', '찬양팀,서기', '아동부', '찬양팀', '서기'
            ]
        }
        
        df = pd.DataFrame(data)
        output_path = self.data_dir / "test_data.xlsx"
        df.to_excel(output_path, index=False)
        return output_path

    def read_staff_data(self, file_path):
        """교인 데이터 읽기"""
        return pd.read_excel(file_path)

    def save_schedule(self, schedule_df, filename="yearly_schedule.xlsx"):
        """생성된 스케줄 저장"""
        output_path = self.generated_dir / filename
        schedule_df.to_excel(output_path, index=False)
        return output_path
```
## src/gui.py
```py
import sys
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QDateEdit, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from src.excel_handler import ExcelHandler
from src.scheduler import TeamBasedScheduler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.excel_handler = ExcelHandler()
        self.scheduler = TeamBasedScheduler()  # 초기화만 하고
        self.selected_file = None
        
        self.setWindowTitle("교회 안내/헌금위원 스케줄러")
        self.setMinimumSize(800, 600)
        
        # 메인 위젯과 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 파일 선택 섹션
        file_section = QHBoxLayout()
        self.file_label = QLabel("선택된 파일: 없음")
        self.file_button = QPushButton("엑셀 파일 선택")
        self.file_button.clicked.connect(self.select_file)
        file_section.addWidget(self.file_label)
        file_section.addWidget(self.file_button)
        layout.addLayout(file_section)
        
        # 날짜 선택 섹션
        date_section = QHBoxLayout()
        date_section.addWidget(QLabel("시작 날짜:"))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        date_section.addWidget(self.date_picker)
        layout.addLayout(date_section)
        
        # 스케줄 생성 버튼
        self.generate_button = QPushButton("스케줄 생성")
        self.generate_button.clicked.connect(self.generate_schedule)
        layout.addWidget(self.generate_button)
        
        # 결과 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["날짜", "헌금위원", "내부안내"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, header.Stretch)  # 헌금위원 칼럼 늘리기
        layout.addWidget(self.table)
        
        # 내보내기 버튼
        self.export_button = QPushButton("엑셀로 내보내기")
        self.export_button.clicked.connect(self.export_schedule)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)
        
    def select_file(self):
        """엑셀 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "엑셀 파일 선택",
            str(Path.home()),
            "Excel files (*.xlsx *.xls)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"선택된 파일: {Path(file_path).name}")
            
    def generate_schedule(self):
        """스케줄 생성"""
        if not self.selected_file:
            QMessageBox.warning(self, "경고", "엑셀 파일을 먼저 선택해주세요.")
            return
            
        try:
            # 데이터 로드
            df = self.excel_handler.read_staff_data(self.selected_file)
            self.scheduler.load_staff_data(df)  # 여기서 데이터 로드
            
            # 날짜 계산
            start_date = self.date_picker.date().toPyDate()
            sundays = self.scheduler.generate_sundays(start_date.strftime('%Y-%m-%d'))
            
            # 스케줄 생성
            schedule_df = self.scheduler.generate_schedule(sundays)  # 여기서 스케줄 생성
            
            # 테이블에 결과 표시
            self.table.setRowCount(len(schedule_df))
            for i, row in schedule_df.iterrows():
                date_item = QTableWidgetItem(row['날짜'])
                offering_item = QTableWidgetItem(row['헌금위원'])
                guide_item = QTableWidgetItem(row['내부안내'])
                
                self.table.setItem(i, 0, date_item)
                self.table.setItem(i, 1, offering_item)
                self.table.setItem(i, 2, guide_item)
                
            self.export_button.setEnabled(True)
            self.schedule_df = schedule_df  # 내보내기용으로 저장
            
        except Exception as e:
            QMessageBox.critical(self, "에러", f"스케줄 생성 중 오류가 발생했습니다:\n{str(e)}")
            
    def export_schedule(self):
        """생성된 스케줄을 엑셀로 내보내기"""
        if not hasattr(self, 'schedule_df'):
            return
            
        try:
            output_path = self.excel_handler.save_schedule(self.schedule_df)
            QMessageBox.information(
                self,
                "완료",
                f"스케줄이 저장되었습니다:\n{output_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "에러",
                f"파일 저장 중 오류가 발생했습니다:\n{str(e)}"
            )
```
## src/main.py
```py
import sys
from PyQt5.QtWidgets import QApplication
from src.gui import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```
## src/scheduler.py
```py
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
```
## tests/test_excel.py
```py
import pytest
import pandas as pd
from pathlib import Path
from src.excel_handler import ExcelHandler
 
@pytest.fixture
def excel_handler():
    """테스트에서 사용할 ExcelHandler 인스턴스를 제공하는 fixture"""
    handler = ExcelHandler()
    yield handler
    # 테스트 후 생성된 파일들 정리
    for file in handler.data_dir.glob("*.xlsx"):
        file.unlink(missing_ok=True)
    for file in handler.generated_dir.glob("*.xlsx"):
        file.unlink(missing_ok=True)

def test_init_creates_directories(excel_handler):
    """초기화 시 필요한 디렉토리들이 생성되는지 테스트"""
    assert excel_handler.data_dir.exists()
    assert excel_handler.generated_dir.exists()

def test_create_test_data(excel_handler):
    """테스트 데이터 생성 기능 테스트"""
    file_path = excel_handler.create_test_data()
    
    # 파일이 생성되었는지 확인
    assert file_path.exists()
    
    # 데이터 내용 검증
    df = pd.read_excel(file_path)
    assert len(df) == 10
    assert list(df.columns) == ['이름', '직책', '소속']
    
    # 데이터 타입 검증
    assert all(isinstance(name, str) for name in df['이름'])
    assert all(isinstance(role, str) for role in df['직책'])
    assert all(isinstance(dept, str) for dept in df['소속'])
    
    # 직책 값이 유효한지 검증
    valid_roles = {'임원', '리더', '에벤에셀'}
    assert all(role in valid_roles for role in df['직책'])

def test_read_staff_data(excel_handler):
    """교인 데이터 읽기 기능 테스트"""
    # 먼저 테스트 데이터 생성
    file_path = excel_handler.create_test_data()
    
    # 데이터 읽기 테스트
    df = excel_handler.read_staff_data(file_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ['이름', '직책', '소속'])

def test_save_schedule(excel_handler):
    """스케줄 저장 기능 테스트"""
    # 테스트용 스케줄 데이터 생성
    schedule_data = {
        '날짜': ['2024-01-07', '2024-01-14'],
        '헌금위원': ['김철수,이영희,박지성', '강다희,윤서연,한미영'],
        '내부안내': ['최민수', '임수진']
    }
    schedule_df = pd.DataFrame(schedule_data)
    
    # 스케줄 저장
    output_path = excel_handler.save_schedule(schedule_df)
    
    # 파일이 생성되었는지 확인
    assert output_path.exists()
    
    # 저장된 데이터 검증
    saved_df = pd.read_excel(output_path)
    assert len(saved_df) == len(schedule_df)
    assert list(saved_df.columns) == list(schedule_df.columns)
    
def test_invalid_file_path(excel_handler):
    """존재하지 않는 파일 경로로 읽기 시도할 때 예외 처리 테스트"""
    with pytest.raises(FileNotFoundError):
        excel_handler.read_staff_data(Path("non_existent.xlsx"))

def test_multiple_saves(excel_handler):
    """여러 번 저장 시 파일이 올바르게 덮어써지는지 테스트"""
    schedule_data = {'날짜': ['2024-01-07'], '헌금위원': ['test'], '내부안내': ['test']}
    schedule_df = pd.DataFrame(schedule_data)
    
    # 첫 번째 저장
    first_path = excel_handler.save_schedule(schedule_df)
    first_modified_time = first_path.stat().st_mtime
    
    # 잠시 대기
    import time
    time.sleep(1)
    
    # 두 번째 저장
    second_path = excel_handler.save_schedule(schedule_df)
    second_modified_time = second_path.stat().st_mtime
    
    # 같은 경로이지만 새로운 파일이 생성되었는지 확인
    assert first_path == second_path
    assert second_modified_time > first_modified_time
```
## tests/test_scheduler.py
```py
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
```
