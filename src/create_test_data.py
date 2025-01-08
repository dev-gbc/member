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