import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  // CORS preflight 처리
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Authorization 헤더에서 JWT 토큰 추출
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Authorization 헤더가 필요합니다.' }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Supabase 클라이언트 생성
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // 사용자 인증 확인
    const token = authHeader.replace('Bearer ', '')
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)

    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: '인증에 실패했습니다.' }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

        // 사용자의 권한 조회 (user_permissions와 permissions, permission_workflows, workflows 조인)
    const { data: userPermissions, error: queryError } = await supabase
      .from('user_permissions')
      .select(`
        id,
        created_at,
        expires_at,
        permission:permissions (
          id,
          name,
          type,
          payment_type,
          workflows:permission_workflows (
            workflow:workflows (
              id,
              name,
              workflow_json
            )
          )
        )
      `)
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (queryError) {
      console.error('권한 조회 오류:', queryError)
      return new Response(
        JSON.stringify({ error: '권한 조회에 실패했습니다.', details: queryError.message }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // 응답 데이터 포맷팅 (workflows 배열로 평탄화)
    const formattedPermissions = userPermissions?.map(up => {
      // permission_workflows에서 workflow 데이터만 추출
      const workflows = up.permission?.workflows?.map((pw: any) => pw.workflow) || []
      
      return {
        id: up.id,
        created_at: up.created_at,
        expires_at: up.expires_at,
        permission: {
          id: up.permission?.id,
          name: up.permission?.name,
          type: up.permission?.type,
          payment_type: up.permission?.payment_type,
          workflows: workflows
        }
      }
    }) || []

    return new Response(
      JSON.stringify({
        permissions: formattedPermissions
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    console.error('처리 중 오류 발생:', error)
    return new Response(
      JSON.stringify({ 
        error: '서버 오류가 발생했습니다.', 
        details: error instanceof Error ? error.message : String(error) 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})
