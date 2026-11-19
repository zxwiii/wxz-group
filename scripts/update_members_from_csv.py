#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课题组网站成员数据自动同步脚本 (members.csv -> members.js & members.json)
========================================================================
功能：
1. 读取项目根目录下的 members.csv（支持 UTF-8 及带 BOM 的 Excel 格式）
2. 规范化并清洗各项数据（教师、在读研究生、校友，电话与邮箱分离，教育经历换行切分，毕业去向解析，头像防丢兼容）
3. 自动生成前端成员页直接引入的纯 JS 模块：src/data/members.js
4. 同步生成兼容的 JSON 文件：src/data/members.json
5. 支持双击直接运行更新，方便日常成员变更运维。
"""

import os
import sys
import csv
import json
import re

# 确定项目根目录（无论在项目根目录运行还是在 scripts/ 子目录下运行）
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'scripts' else current_dir

csv_path = os.path.join(project_root, 'members.csv')
target_js_path = os.path.join(project_root, 'src', 'data', 'members.js')
target_json_path = os.path.join(project_root, 'src', 'data', 'members.json')
avatar_dir = os.path.join(project_root, 'public', 'images', 'members')

def main():
    print("=" * 60)
    print("王小治课题组 - 成员数据同步工具 (CSV -> members.js)")
    print("=" * 60)

    if not os.path.exists(csv_path):
        print(f"❌ 错误：未找到 CSV 文件：{csv_path}")
        input("\n按回车键退出...")
        sys.exit(1)

    print(f"📄 正在读取数据源：{csv_path}")

    # 扫描已有的头像文件，避免图片后缀写错破图
    avatar_map = {}
    if os.path.exists(avatar_dir):
        for fn in os.listdir(avatar_dir):
            base, ext = os.path.splitext(fn)
            avatar_map[base] = f"/images/members/{fn}"

    members = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            m_id = row.get('id', '').strip()
            name = row.get('name', '').strip()
            if not name:
                continue

            category = row.get('category', '').strip()
            # 严格规整为三大分类
            if category not in ['教师', '在读研究生', '校友']:
                if '教师' in category or m_id.startswith('faculty_'):
                    category = '教师'
                elif '校友' in category or '毕业' in category:
                    category = '校友'
                else:
                    category = '在读研究生'

            title = row.get('title', '').strip()
            grade = row.get('grade', '').strip()
            research = row.get('research', '').strip()
            email = row.get('email', '').strip()
            phone = row.get('phone', '').strip()
            career = row.get('career', '').strip()
            education = row.get('education', '').strip()
            homepage_url = row.get('homepage_url', '').strip()
            avatar_url = row.get('avatar_url', '').strip()

            # 仅教师保留官方主页（学生与校友清空，彻底避免指向将迁移的 wxz.group 旧站点）
            if category != '教师' or 'wxz.group' in homepage_url:
                homepage_url = ''

            # 电话与邮箱容错
            if not phone and re.match(r'^1[3-9]\d{9}$', email):
                phone = email
                email = ''

            # 教育经历结构化：修复连字符断行并按经历分项
            edu_lines = []
            if education:
                # 彻底消除 2022.09-\n2024.07 等因破折号造成的错误断行
                education = re.sub(r'([-\u2013\u2014~至])\s*[\r\n]+\s*', r'\1', education)
                raw_lines = re.split(r'[\r\n]+', education)
                for l in raw_lines:
                    l = l.strip()
                    if not l:
                        continue
                    # 避免在连字符处切分，仅在以年份开头的完整经历处切分
                    subparts = re.split(r'(?<![-\u2013\u2014~至\d])(?=(?:19|20)\d{2}[.\-年/])', l)
                    for sp in subparts:
                        sp = sp.strip().strip('；;，, ')
                        if sp:
                            edu_lines.append(sp)

            # 头像映射校验
            if m_id in avatar_map:
                avatar_url = avatar_map[m_id]
            elif not avatar_url or avatar_url == '/images/default_avatar.jpg':
                avatar_url = '/images/members/default_avatar.jpg'

            members.append({
                'id': m_id,
                'category': category,
                'name': name,
                'title': title,
                'grade': grade,
                'research': research,
                'email': email,
                'phone': phone,
                'career': career,
                'education': education,
                'education_list': edu_lines,
                'homepage_url': homepage_url,
                'avatar_url': avatar_url
            })

    print(f"✅ 成功解析 {len(members)} 位成员数据：")
    faculty_count = sum(1 for m in members if m['category'] == '教师')
    student_count = sum(1 for m in members if m['category'] == '在读研究生')
    alumni_count = sum(1 for m in members if m['category'] == '校友')
    print(f"   - 教师：{faculty_count} 位")
    print(f"   - 在读研究生：{student_count} 位")
    print(f"   - 毕业校友：{alumni_count} 位")

    # 1. 生成 src/data/members.js
    os.makedirs(os.path.dirname(target_js_path), exist_ok=True)
    js_content = f"""// ==========================================================================
// 王小治课题组成员数据配置 (members.js)
// 本文件由 scripts/update_members_from_csv.py 自动生成，请勿在此手动修改！
// 如需更新成员信息，请直接修改根目录下 members.csv 并重新运行该脚本。
// 生成时间: {import_time()}
// ==========================================================================

export const membersData = {json.dumps(members, ensure_ascii=False, indent=2)};

export default membersData;
"""
    with open(target_js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"🚀 已成功生成前端 JS 模块：{target_js_path}")

    # 2. 同步生成 src/data/members.json (向后兼容)
    with open(target_json_path, 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)
    print(f"📦 已同步更新 JSON 数据：{target_json_path}")

    print("=" * 60)
    print("🎉 成员数据同步全部完成！前端已立即生效。")
    print("=" * 60)

def import_time():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    main()
