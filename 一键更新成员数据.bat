@echo off
chcp 65001 >nul
title 王小治课题组 - 成员数据同步工具

echo ============================================================
echo   王小治课题组 - 一键同步成员数据
echo   (从 members.csv 自动生成 src/data/members.js)
echo ============================================================
echo.

python scripts\update_members_from_csv.py

echo.
pause
