# 扬州大学环境科学与工程学院王小治课题组官方网站

本仓库是王小治课题组官方网站的源码仓库，采用现代前端静态生成框架 **Astro** 构建，搭配 **Decap CMS** 实现可视化内容管理，由 **Cloudflare Pages** 提供全球边缘加速与自动化持续集成（CI/CD），并由 **Cloudflare Zero Trust** 提供组内内部专区安全防护。

---

## 目录结构

```text
├── public/                 # 静态资源目录
│   ├── admin/              # Decap CMS 可视化管理后台
│   │   ├── config.yml      # 后台字段与 GitHub 仓库配置
│   │   └── index.html      # 后台单页应用
│   └── images/             # 网站图片、教师立绘及上传素材
├── src/                    # 源代码
│   ├── content/
│   │   ├── config.ts       # Astro Content Collections 模式定义
│   │   └── news/           # 组内全部新闻动态 Markdown 文件
│   ├── data/               # 课题组师生结构化数据 (JSON)
│   ├── layouts/
│   │   └── Layout.astro    # 全站统一中文导航条与统一底部布局
│   └── pages/              # 各栏目主页
│       ├── index.astro     # 课题组主页 (王小治教授立绘与组况)
│       ├── research.astro  # 研究方向
│       ├── publications.astro # 学术文章 (集成 WoS 官方认证与动态引证)
│       ├── patents.astro   # 专利成果 (已授权翡翠绿专利管理系统)
│       ├── members.astro   # 团队成员 (PI独占首行、教师4列网格、学生与校友)
│       ├── news/           # 新闻动态列表与详情
│       ├── internal/       # 内部专区 (受 Cloudflare Zero Trust 保护)
│       ├── joinus.astro    # 诚邀英才
│       └── contact.astro   # 联系我们
├── astro.config.mjs        # Astro 配置文件
├── package.json            # 依赖与编译脚本
└── tsconfig.json           # TypeScript 配置
```

---

## 云端全自动构建设置 (Cloudflare Pages)

- **构建命令 (Build command)**: `npm run build`
- **输出目录 (Build output directory)**: `dist`
- **Node.js 版本 (环境变量)**: `NODE_VERSION: 18` 或以上
