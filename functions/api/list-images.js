// Cloudflare Pages Function: 安全获取云端媒体库图片列表
export async function onRequestGet(context) {
  const { env } = context;
  const githubToken = env.GITHUB_TOKEN;

  const headers = { 'User-Agent': 'Cloudflare-Pages-CMS' };
  if (githubToken) {
    headers['Authorization'] = `token ${githubToken}`;
  }

  try {
    const resp = await fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/public/images/uploads`, { headers });
    let files = [];
    if (resp.ok) {
      const data = await resp.json();
      if (Array.isArray(data)) {
        files = data.filter(f => f.name !== '.gitkeep').map(f => ({
          name: f.name,
          sha: f.sha,
          size: f.size,
          url: `/images/uploads/${f.name}`,
          download_url: f.download_url
        }));
      }
    }
    return new Response(JSON.stringify({ success: true, files }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
