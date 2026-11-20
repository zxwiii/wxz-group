// Cloudflare Pages 自定义 404 全局拦截与回退中间件
export async function onRequest(context) {
  const response = await context.next();
  if (response.status === 404) {
    try {
      const url = new URL(context.request.url);
      const notFoundUrl = new URL('/404.html', url.origin);
      const notFoundResponse = await context.env.ASSETS.fetch(notFoundUrl);
      return new Response(notFoundResponse.body, {
        status: 404,
        headers: {
          'Content-Type': 'text/html; charset=utf-8'
        }
      });
    } catch (e) {
      return response;
    }
  }
  return response;
}
