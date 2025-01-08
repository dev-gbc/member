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