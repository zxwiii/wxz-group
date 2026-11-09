// Cloudflare Pages Function: 安全云端文件删除接口
export async function onRequestPost(context) {
  const { request, env } = context;

  const githubToken = env.GITHUB_TOKEN;
  if (!githubToken) {
    return new Response(JSON.stringify({ 
      error: 'Cloudflare 环境变量未检测到 GITHUB_TOKEN！' 
    }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }

  try {
    const data = await request.json();
    const { path, sha } = data;

    if (!path) {
      return new Response(JSON.stringify({ error: '路径不能为空' }), { status: 400 });
    }

    let targetSha = sha;
    // 如果前端未提供 SHA，服务端自动向 GitHub 探查
    if (!targetSha) {
      const getResp = await fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/${path}`, {
        headers: {
          'Authorization': `token ${githubToken}`,
          'User-Agent': 'Cloudflare-Pages-CMS'
        }
      });
      if (getResp.ok) {
        const fileInfo = await getResp.json();
        targetSha = fileInfo.sha;
      }
    }

    if (!targetSha) {
      return new Response(JSON.stringify({ error: '未找到文件 SHA，可能已被删除' }), { status: 404 });
    }

    const delResp = await fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/${path}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `token ${githubToken}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Cloudflare-Pages-CMS'
      },
      body: JSON.stringify({
        message: `chore: delete file ${path}`,
        sha: targetSha
      })
    });

    if (delResp.ok) {
      return new Response(JSON.stringify({ success: true, message: '删除成功！' }), {
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      const err = await delResp.json().catch(() => ({}));
      return new Response(JSON.stringify({ error: err.message || '删除失败' }), {
        status: delResp.status,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
