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
from src.scheduler import ChurchScheduler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.excel_handler = ExcelHandler()
        self.scheduler = ChurchScheduler()
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
            self.scheduler.load_staff_data(df)
            
            # 날짜 계산
            start_date = self.date_picker.date().toPyDate()
            sundays = self.scheduler.generate_sundays(start_date.strftime('%Y-%m-%d'))
            
            # 스케줄 생성
            schedule_df = self.scheduler.create_schedule_dataframe(sundays)
            
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