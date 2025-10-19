from typing import Dict
from .supabase_client import supabase


def get_workflows() -> Dict[str, str]:
    """
    사용자의 권한에 맞는 워크플로우 목록을 가져옵니다.
    Supabase RPC 함수(get_user_workflows)를 호출하여 조회합니다.
    
    Returns:
        권한별 워크플로우 JSON 문자열 딕셔너리
        예: {
            "kream": '{"site_name": "크림", "steps": [...]}',
        }
    """
    try:
        # RPC 함수 직접 호출
        response = supabase.rpc('get_user_workflows').execute()
        
        if not response.data:
            return {}
        
        # 결과를 {permission_name: workflow_json} 형태로 변환
        workflows = {}
        
        for item in response.data:
            permission_name = item.get('permission_name')
            workflow_json = item.get('workflow_json')
            
            if permission_name and workflow_json:
                # workflow_json이 dict면 JSON 문자열로 변환
                if isinstance(workflow_json, dict):
                    import json
                    workflows[permission_name] = json.dumps(workflow_json, ensure_ascii=False)
                else:
                    workflows[permission_name] = workflow_json
        
        return workflows
        
    except Exception as e:
        return {}

