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