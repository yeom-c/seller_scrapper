import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def save_to_csv(data, filename, subfolder_name, column_mappings=None, log_handler=print):
    """스크랩핑한 데이터를 ./output/[subfolder_name] 폴더에 CSV 파일로 저장합니다."""
    if not data:
        log_handler("저장할 데이터가 없습니다.", "orange")
        return
    
    output_dir = os.path.join(BASE_DIR, 'output', subfolder_name)
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    if column_mappings:
        # column_mappings의 키 순서대로 DataFrame 생성하여 순서 보장
        ordered_keys = list(column_mappings.keys())
        df = pd.DataFrame(data, columns=ordered_keys)
        df.columns = [column_mappings[key] for key in ordered_keys]
    else:
        df = pd.DataFrame(data)
    
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    log_handler(f"'{file_path}' 파일 저장이 완료되었습니다.", "blue")