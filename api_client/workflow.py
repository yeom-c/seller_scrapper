from typing import Dict
from .supabase_client import supabase
import json

def get_workflows() -> Dict[str, str]:
    """
    사용자의 권한에 맞는 워크플로우 목록을 가져옵니다.
    Supabase Edge Function (get-my-workflows)을 호출하여 조회합니다.
    
    Returns:
        권한별 워크플로우 JSON 문자열 딕셔너리
        예: {
            "kream": '{"site_name": "크림", "steps": [...]}',
        }
    """
    try:
        # Edge Function 호출
        response_data = supabase.functions.invoke('get-my-workflows')
        
        # response_data가 bytes일 경우 디코딩
        if isinstance(response_data, bytes):
            data = json.loads(response_data.decode('utf-8'))
        else:
            # 만약 이미 dict/list로 파싱되었다면 그대로 사용
            data = response_data

        if not data:
            return {}
        
        # 결과를 {permission_name: workflow_json} 형태로 변환
        # Edge Function이 RPC와 동일하게 list of dicts를 반환한다고 가정
        workflows = {}
        for item in data:
            permission = item.get('permission', {})
            workflow = item.get('workflow', {})
            
            if permission and workflow:
                # workflow_json이 dict면 JSON 문자열로 변환
                permission_type = permission.get('type')
                workflow_json = workflow.get('workflow_json')
                if workflow_json:
                    if isinstance(workflow_json, dict):
                        workflows[permission_type] = json.dumps(workflow_json, ensure_ascii=False)
                    else:
                        workflows[permission_type] = workflow_json
        
        return workflows
        
    except Exception as e:
        print(f"Edge Function 호출 중 오류: {e}")
        return {}

