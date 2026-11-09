// Cloudflare Pages Function: 安全获取课题组文档与附件列表
export async function onRequestGet(context) {
  const { env } = context;
  const githubToken = env.GITHUB_TOKEN;

  const headers = { 'User-Agent': 'Cloudflare-Pages-CMS' };
  if (githubToken) {
    headers['Authorization'] = `token ${githubToken}`;
  }

  try {
    const [pubResp, intResp] = await Promise.all([
      fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/public/downloads`, { headers }),
      fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/public/internal/downloads`, { headers })
    ]);

    let allFiles = [];
    if (pubResp.ok) {
      const pubFiles = await pubResp.json();
      if (Array.isArray(pubFiles)) {
        pubFiles.filter(f => f.name !== '.gitkeep').forEach(f => {
          allFiles.push({
            name: f.name,
            size: f.size,
            sha: f.sha,
            isInternal: false,
            url: `/downloads/${f.name}`,
            fullPath: `public/downloads/${f.name}`
          });
        });
      }
    }

    if (intResp.ok) {
      const intFiles = await intResp.json();
      if (Array.isArray(intFiles)) {
        intFiles.filter(f => f.name !== '.gitkeep').forEach(f => {
          allFiles.push({
            name: f.name,
            size: f.size,
            sha: f.sha,
            isInternal: true,
            url: `/internal/downloads/${f.name}`,
            fullPath: `public/internal/downloads/${f.name}`
          });
        });
      }
    }

    return new Response(JSON.stringify({ success: true, files: allFiles }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
