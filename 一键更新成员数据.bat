@echo off
chcp 65001 >nul
title 王小治课题组 - 成员数据一键同步与云端发布工具

echo ============================================================
echo   王小治课题组 - 成员数据一键同步与云端发布
echo ============================================================
echo.

echo [步骤 1/3] 正在从 members.csv 转换生成网站前端数据...
python scripts\update_members_from_csv.py
if errorlevel 1 (
    echo.
    echo ❌ 数据生成遇到错误，请检查 members.csv 格式。
    pause
    exit /b 1
)

echo.
echo [步骤 2/3] 正在将更新提交并推送到云端仓库 (GitHub)...
git add members.csv src/data/ public/images/
git commit -m "update(members): sync members data and avatars via bat"
git push origin main

if errorlevel 1 (
    echo.
    echo ⚠️ 推送到云端遇到网络波动或未检测到新变动。
    echo 本地数据已生成成功。若需重试推送，可重新运行本工具。
) else (
    echo.
    echo ============================================================
    echo  🎉 恭喜！数据已成功推送到云端仓库！
    echo  ⚡ Cloudflare 正在自动为您编译并发布最新网站...
    echo  🌐 大约 1 分钟后，访问官网 (wxz.zxw.ac.cn) 即可看到最新成员！
    echo ============================================================
)

echo.
echo 按任意键退出...
pause >nul
