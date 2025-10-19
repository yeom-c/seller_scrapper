import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

Deno.serve(async (req) => {
  // OPTIONS 요청(preflight)을 처리하여 CORS 문제를 방지합니다.
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Supabase 클라이언트를 생성합니다.
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    // 요청 헤더의 JWT를 사용하여 현재 로그인한 사용자의 정보를 가져옵니다.
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 401,
      })
    }

    // 사용자의 ID를 기반으로, 만료되지 않은 권한에 해당하는 워크플로우를 조회합니다.
    const { data: workflows, error } = await supabase
      .from('user_permissions')
      .select(`
        permissions (
          workflows (
            id,
            name,
            workflow_json
          )
        )
      `)
      .eq('user_id', user.id)
      .gt('expires_at', new Date().toISOString()) // expires_at > now()

    if (error) {
      throw error
    }

    // 데이터 구조를 클라이언트가 사용하기 쉽게 가공합니다.
    const workflowList = workflows.map(item => item.permissions.workflows);

    return new Response(JSON.stringify(workflowList), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    })
  } catch (err) {
    return new Response(String(err?.message ?? err), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 500,
    })
  }
})