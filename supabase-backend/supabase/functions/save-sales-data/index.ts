import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

interface SalesDataItem {
  platform_name: string
  order_number: string
  sale_date: string
  product_name: string
  product_code?: string
  product_size?: string
  product_color?: string
  sale_price: number
  quantity: number
}

interface RequestBody {
  sales: SalesDataItem[]
}

Deno.serve(async (req) => {
  // OPTIONS 요청(preflight)을 처리하여 CORS 문제를 방지합니다.
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // POST 요청만 허용
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed' }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 405,
        }
      )
    }

    // Supabase 클라이언트를 생성합니다.
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    // 요청 헤더의 JWT를 사용하여 현재 로그인한 사용자의 정보를 가져옵니다.
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 401,
        }
      )
    }

    // 요청 바디에서 판매 데이터를 파싱합니다.
    const requestBody: RequestBody = await req.json()
    
    if (!requestBody.sales || !Array.isArray(requestBody.sales)) {
      return new Response(
        JSON.stringify({ error: 'Invalid request body. Expected { sales: [...] }' }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 400,
        }
      )
    }

    if (requestBody.sales.length === 0) {
      return new Response(
        JSON.stringify({ message: 'No sales data to save', inserted: 0, errors: [] }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200,
        }
      )
    }

    // 각 판매 데이터에 user_id를 추가합니다.
    const salesWithUserId = requestBody.sales.map(sale => ({
      user_id: user.id,
      ...sale,
    }))

    // 판매 데이터를 데이터베이스에 삽입합니다.
    // upsert를 사용하여 중복된 데이터는 업데이트하고, 새로운 데이터는 삽입합니다.
    const { data, error } = await supabase
      .from('sales')
      .upsert(salesWithUserId, {
        onConflict: 'user_id,platform_name,order_number',
        ignoreDuplicates: false, // 중복 시 업데이트
      })
      .select()

    if (error) {
      console.error('Error inserting sales data:', error)
      return new Response(
        JSON.stringify({ 
          error: 'Failed to save sales data',
          details: error.message,
        }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 500,
        }
      )
    }

    return new Response(
      JSON.stringify({
        message: 'Sales data saved successfully',
        inserted: data?.length || 0,
        data: data,
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    )

  } catch (error) {
    console.error('Unexpected error:', error)
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    )
  }
})
