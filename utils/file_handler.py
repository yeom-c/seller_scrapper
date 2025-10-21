import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def save_to_csv(data, filename, subfolder_name, column_mappings=None, column_order=None, log_handler=print):
    """스크랩핑한 데이터를 ./output/[subfolder_name] 폴더에 CSV 파일로 저장합니다.
    
    Args:
        data: 저장할 데이터 리스트
        filename: 파일명
        subfolder_name: 서브폴더명
        column_mappings: 컬럼명 매핑 딕셔너리 (원본키: 표시할이름)
        column_order: 컬럼 순서 리스트 (원본 키 순서)
        log_handler: 로그 출력 함수
    """
    if not data:
        log_handler("저장할 데이터가 없습니다.", "orange")
        return
    
    output_dir = os.path.join(BASE_DIR, 'output', subfolder_name)
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    # column_order가 지정된 경우 해당 순서 사용, 없으면 데이터 원본 순서
    if column_order:
        ordered_keys = column_order
    else:
        ordered_keys = None
    
    if ordered_keys:
        # 지정된 순서대로 DataFrame 생성
        df = pd.DataFrame(data, columns=ordered_keys)
        
        # column_mappings가 있으면 컬럼명 변경
        if column_mappings:
            df.columns = [column_mappings.get(key, key) for key in ordered_keys]
    else:
        df = pd.DataFrame(data)
    
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    log_handler(f"'{file_path}' 파일 저장이 완료되었습니다.", "blue")