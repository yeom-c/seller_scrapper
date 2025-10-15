import os
import json
from datetime import datetime
from core.scraper import WorkflowScraper

# 워크플로우 파일이 저장된 디렉토리 경로
WORKFLOW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workflows')

def get_date_input(prompt):
    """사용자로부터 YYYY-MM-DD 형식의 날짜를 입력받고 datetime 객체로 변환합니다."""
    while True:
        date_str = input(prompt)
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("오류: 날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 다시 입력해주세요.")

def find_authorized_workflows(permissions):
    """보유한 권한과 일치하는 워크플로우 파일 목록을 반환합니다."""
    if not os.path.exists(WORKFLOW_DIR):
        return []
    
    authorized_workflows = []
    all_files = os.listdir(WORKFLOW_DIR)
    
    for p in permissions:
        expected_filename = f"{p}_workflow.json"
        if expected_filename in all_files:
            authorized_workflows.append(expected_filename)
            
    return authorized_workflows

def select_workflow(workflows):
    """사용자에게 워크플로우 목록을 보여주고 선택하게 합니다."""
    if not workflows:
        print("실행 가능한 워크플로우를 찾을 수 없거나, 보유한 권한이 없습니다.")
        return None

    print("\n🚀 실행할 워크플로우를 선택하세요:\n")
    for i, wf in enumerate(workflows):
        print(f"  [{i + 1}] {wf}")
    
    while True:
        try:
            choice = int(input("\n번호를 입력하세요: "))
            if 1 <= choice <= len(workflows):
                return workflows[choice - 1]
            else:
                print("잘못된 번호입니다. 다시 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

def load_workflow(filename):
    """선택된 워크플로우 파일을 JSON 객체로 로드합니다."""
    workflow_path = os.path.join(WORKFLOW_DIR, filename)
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            print(f"\n워크플로우 '{filename}'을(를) 로드합니다.")
            return json.load(f)
    except FileNotFoundError:
        print(f"에러: '{workflow_path}' 파일을 찾을 수 없습니다.")
        return None

if __name__ == "__main__":
    # 사용자가 'kream' 권한만 가지고 있다고 지정
    user_permissions = ['kream']
    
    print(f"현재 보유 권한: {user_permissions}")

    # 보유 권한에 맞는 워크플로우 탐색
    available_workflows = find_authorized_workflows(user_permissions)
    
    # 사용자로부터 실행할 워크플로우 선택
    selected_workflow_file = select_workflow(available_workflows)
    
    if selected_workflow_file:
        date_range = {}
        # 선택된 파일이 kream 워크플로우일 경우에만 날짜를 입력받음
        if 'kream_workflow' in selected_workflow_file:
            print("\n🗓️ 스크랩할 기간을 입력하세요. (전체 기간은 그냥 Enter)")
            start_date = get_date_input("시작일 (YYYY-MM-DD): ")
            end_date = get_date_input("종료일 (YYYY-MM-DD): ")
            date_range = {'start_date': start_date, 'end_date': end_date}

        # 선택된 워크플로우 로드
        workflow_data = load_workflow(selected_workflow_file)
    
        if workflow_data and 'steps' in workflow_data:
            # 스크레이퍼를 통해 워크플로우 실행 (날짜 정보 전달)
            scraper = WorkflowScraper()
            scraper.run_workflow(workflow_data['steps'], **date_range)