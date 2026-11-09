// Cloudflare Pages Function: 安全云端多媒体与附件上传接口
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
    const { fileName, base64Content, type, isInternal } = data;

    if (!fileName || !base64Content) {
      return new Response(JSON.stringify({ error: '文件名和文件内容不能为空！' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const cleanName = fileName.replace(/[^a-zA-Z0-9._\-\u4e00-\u9fa5]/g, '_');
    const safeName = `${Date.now()}_${cleanName}`;

    let filePath = '';
    let publicUrl = '';

    if (type === 'image') {
      filePath = `public/images/uploads/${safeName}`;
      publicUrl = `/images/uploads/${safeName}`;
    } else {
      // 附件文档：根据 isInternal 决定是否隔离入 /internal 路由
      if (isInternal) {
        filePath = `public/internal/downloads/${safeName}`;
        publicUrl = `/internal/downloads/${safeName}`;
      } else {
        filePath = `public/downloads/${safeName}`;
        publicUrl = `/downloads/${safeName}`;
      }
    }

    const resp = await fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/${filePath}`, {
      method: 'PUT',
      headers: {
        'Authorization': `token ${githubToken}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Cloudflare-Pages-CMS'
      },
      body: JSON.stringify({
        message: `feat(media): upload ${safeName}`,
        content: base64Content
      })
    });

    if (resp.ok) {
      return new Response(JSON.stringify({
        success: true,
        fileName: safeName,
        url: publicUrl,
        filePath: filePath
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      const err = await resp.json().catch(() => ({}));
      return new Response(JSON.stringify({ error: err.message || '上传写入 GitHub 仓库失败' }), {
        status: resp.status,
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
