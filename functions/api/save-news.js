// Cloudflare Pages Function: 安全云端文章发布与修改接口
export async function onRequestPost(context) {
  const { request, env } = context;

  const githubToken = env.GITHUB_TOKEN;
  if (!githubToken) {
    return new Response(JSON.stringify({ 
      error: 'Cloudflare 环境变量未检测到 GITHUB_TOKEN，请在 Cloudflare Pages 设置中配置！' 
    }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }

  try {
    const data = await request.json();
    const { title, date, category, accessLevel, content, slug } = data;

    if (!title || !date || !content) {
      return new Response(JSON.stringify({ error: '标题、日期和正文内容不能为空！' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const safeSlug = slug || `${date}-${Date.now().toString().slice(-4)}`;
    const mdContent = `---
title: "${title.replace(/"/g, '\\"')}"
date: "${date}"
category: "${category || '科研进展'}"
accessLevel: "${accessLevel || 'public'}"
---

${content}
`;

    // 将 UTF-8 内容转换为 Base64
    const encoder = new TextEncoder();
    const uint8Array = encoder.encode(mdContent);
    let binary = '';
    for (let i = 0; i < uint8Array.length; i++) {
      binary += String.fromCharCode(uint8Array[i]);
    }
    const b64 = btoa(binary);

    // 查询现有文件的 SHA（如果是修改现有文章）
    let sha = null;
    try {
      const getResp = await fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/src/content/news/${safeSlug}.md`, {
        headers: {
          'Authorization': `token ${githubToken}`,
          'User-Agent': 'Cloudflare-Pages-CMS'
        }
      });
      if (getResp.ok) {
        const existingData = await getResp.json();
        if (existingData.sha) sha = existingData.sha;
      }
    } catch(e) {}

    const payload = {
      message: sha ? `feat(news): update article ${title}` : `feat(news): publish article ${title}`,
      content: b64
    };
    if (sha) payload.sha = sha;

    const putResp = await fetch(`https://api.github.com/repos/zxwiii/wxz-group/contents/src/content/news/${safeSlug}.md`, {
      method: 'PUT',
      headers: {
        'Authorization': `token ${githubToken}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Cloudflare-Pages-CMS'
      },
      body: JSON.stringify(payload)
    });

    if (putResp.ok) {
      return new Response(JSON.stringify({
        success: true,
        message: '文章发布成功，Cloudflare 已触发自动构建部署！',
        slug: safeSlug
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      const err = await putResp.json().catch(() => ({}));
      return new Response(JSON.stringify({ error: err.message || 'GitHub 提交失败' }), {
        status: putResp.status,
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
