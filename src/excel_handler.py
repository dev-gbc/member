import pandas as pd
from pathlib import Path

class ExcelHandler:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 다운로드 폴더로 변경
        self.downloads_dir = Path.home() / "Downloads"
        self.generated_dir = self.downloads_dir / "교회_스케줄"
        self.generated_dir.mkdir(exist_ok=True)
        
        print(f"📁 스케줄 저장 위치: {self.generated_dir}")

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

    def save_schedule(self, schedule_df, filename=None):
        """생성된 스케줄 저장 - 다운로드 폴더에 저장"""
        if filename is None:
            # 날짜가 포함된 파일명으로 자동 생성
            from datetime import datetime
            today = datetime.now().strftime("%Y%m%d")
            filename = f"교회_봉사자_스케줄_{today}.xlsx"
        
        output_path = self.generated_dir / filename
        
        print(f"💾 저장 시도: {output_path}")
        print(f"📊 데이터 크기: {len(schedule_df)} 행")
        
        # 헌금위원을 3개 컬럼으로 분리
        export_df = schedule_df.copy()
        
        # 헌금위원 컬럼을 분리
        offering_split = export_df['헌금위원'].str.split(', ', expand=True)
        export_df['헌금위원1'] = offering_split[0] if 0 in offering_split.columns else ''
        export_df['헌금위원2'] = offering_split[1] if 1 in offering_split.columns else ''
        export_df['헌금위원3'] = offering_split[2] if 2 in offering_split.columns else ''
        
        # 기존 헌금위원 컬럼 제거
        export_df = export_df.drop('헌금위원', axis=1)
        
        # 컬럼 순서 재정렬: 날짜, 헌금위원1, 헌금위원2, 헌금위원3, 내부안내
        export_df = export_df[['날짜', '헌금위원1', '헌금위원2', '헌금위원3', '내부안내']]
        
        try:
            # 엑셀 저장 시 한글 깨짐 방지
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='봉사자스케줄')
                
                # 워크시트 가져와서 컬럼 너비 조정
                worksheet = writer.sheets['봉사자스케줄']
                worksheet.column_dimensions['A'].width = 12  # 날짜
                worksheet.column_dimensions['B'].width = 10  # 헌금위원1
                worksheet.column_dimensions['C'].width = 10  # 헌금위원2
                worksheet.column_dimensions['D'].width = 10  # 헌금위원3
                worksheet.column_dimensions['E'].width = 10  # 내부안내
            
            print(f"✅ 저장 완료! 파일 위치: {output_path}")
            print(f"📋 컬럼 구조: A(날짜), B(헌금위원1), C(헌금위원2), D(헌금위원3), E(내부안내)")
            return output_path
            
        except PermissionError:
            # 파일이 열려있는 경우 새로운 이름으로 저장
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"교회_봉사자_스케줄_{timestamp}.xlsx"
            new_output_path = self.generated_dir / new_filename
            
            with pd.ExcelWriter(new_output_path, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='봉사자스케줄')
                
                # 워크시트 가져와서 컬럼 너비 조정
                worksheet = writer.sheets['봉사자스케줄']
                worksheet.column_dimensions['A'].width = 12
                worksheet.column_dimensions['B'].width = 10
                worksheet.column_dimensions['C'].width = 10
                worksheet.column_dimensions['D'].width = 10
                worksheet.column_dimensions['E'].width = 10
            
            print(f"⚠️  기존 파일이 사용 중이어서 새 파일로 저장: {new_output_path}")
            return new_output_path
            
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
            raise e