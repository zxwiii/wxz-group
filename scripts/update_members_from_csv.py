#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课题组网站成员数据自动同步脚本 (members.csv -> members.js & members.json)
========================================================================
规则说明：
1. 仅读取 members.csv，绝不修改、覆盖或格式化 CSV 文件本身！
2. 完整读取新增字段，包括 update（更新时间）
3. 严格遵循用户指定的排序规则：
   - 教师：严格保持当前在 CSV 中的排序
   - 在读研究生：以 p_ 开头的博士生置顶，其余按年级降序排序（高年级/入学早的在下面）
   - 校友：按年级降序排序（入学年份早的在下面，2023级在最上，2008级在最底）
4. 输出纯 JS 模块 src/data/members.js 和同步兼容的 JSON 数据
"""

import os
import sys
import csv
import json
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'scripts' else current_dir

csv_path = os.path.join(project_root, 'members.csv')
target_js_path = os.path.join(project_root, 'src', 'data', 'members.js')
target_json_path = os.path.join(project_root, 'src', 'data', 'members.json')
avatar_dir = os.path.join(project_root, 'public', 'images', 'members')

def get_grade_number(text):
    if not text:
        return 0
    m = re.search(r'(\d{4})', str(text))
    return int(m.group(1)) if m else 0

def main():
    print("=" * 60)
    print("王小治课题组 - 成员数据同步工具 (CSV -> members.js)")
    print("=" * 60)

    if not os.path.exists(csv_path):
        print(f"❌ 错误：未找到 CSV 文件：{csv_path}")
        input("\n按回车键退出...")
        sys.exit(1)

    print(f"📄 正在读取数据源：{csv_path}")

    # 扫描已有的头像文件
    avatar_map = {}
    if os.path.exists(avatar_dir):
        for fn in os.listdir(avatar_dir):
            base, ext = os.path.splitext(fn)
            avatar_map[base] = f"/images/members/{fn}"

    teachers = []
    students = []
    alumni = []

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
            update = row.get('update', '').strip()

            # 仅教师保留官方主页（学生与校友清空，避免指向旧站点）
            if category != '教师' or 'wxz.group' in homepage_url:
                homepage_url = ''

            # 电话与邮箱容错
            if not phone and re.match(r'^1[3-9]\d{9}$', email):
                phone = email
                email = ''

            # 教育经历结构化：修复连字符断行并按经历分项
            edu_lines = []
            if education:
                education = re.sub(r'([-\u2013\u2014~至])\s*[\r\n]+\s*', r'\1', education)
                raw_lines = re.split(r'[\r\n]+', education)
                for l in raw_lines:
                    l = l.strip()
                    if not l:
                        continue
                    subparts = re.split(r'(?<![-\u2013\u2014~至\d])(?=(?:19|20)\d{2}[.\-年/])', l)
                    for sp in subparts:
                        sp = sp.strip().strip('；;，, ')
                        if sp:
                            edu_lines.append(sp)

                # 双重保护：合并末尾带连字符的分裂项，杜绝任何断行
                merged_lines = []
                idx = 0
                while idx < len(edu_lines):
                    cur = edu_lines[idx]
                    if re.search(r'[-\u2013\u2014~至]$', cur) and idx + 1 < len(edu_lines):
                        merged_lines.append(cur + edu_lines[idx + 1])
                        idx += 2
                    else:
                        merged_lines.append(cur)
                        idx += 1
                edu_lines = merged_lines

            # 头像映射：优先使用用户在 CSV 中指定的 avatar_url
            if not avatar_url or avatar_url == '/images/default_avatar.jpg':
                if m_id in avatar_map:
                    avatar_url = avatar_map[m_id]
                else:
                    avatar_url = '/images/members/default_avatar.jpg'

            item = {
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
                'avatar_url': avatar_url,
                'update': update
            }

            if category == '教师':
                teachers.append(item)
            elif category == '在读研究生':
                students.append(item)
            else:
                alumni.append(item)

    # 排序规则执行：
    # 1. 教师：严格保持用户当前在 CSV 中的顺序
    # 2. 在读学生：p_X（博士生）置顶，其余按年级降序（年级大的/入学早的在下面）
    students.sort(key=lambda s: (0 if s['id'].startswith('p_') else 1, -get_grade_number(s['grade'] or s['title'])))

    # 3. 校友：按年级降序排序（年级大的在下面，例如 2023级在上面，2008级在最底）
    alumni.sort(key=lambda a: -get_grade_number(a['grade'] or a['title']))

    # 汇总全部成员
    all_members = teachers + students + alumni

    print(f"✅ 成功解析 {len(all_members)} 位成员数据：")
    print(f"   - 教师：{len(teachers)} 位 (保持原序)")
    print(f"   - 在读研究生：{len(students)} 位 (p_X置顶，年级降序)")
    print(f"   - 毕业校友：{len(alumni)} 位 (年级降序)")

    # 1. 生成 src/data/members.js
    os.makedirs(os.path.dirname(target_js_path), exist_ok=True)
    js_content = f"""// ==========================================================================
// 王小治课题组成员数据配置 (members.js)
// 本文件由 scripts/update_members_from_csv.py 自动生成，请勿在此手动修改！
// 如需更新成员信息，请直接修改根目录下 members.csv 并重新运行该脚本。
// 生成时间: {import_time()}
// ==========================================================================

export const membersData = {json.dumps(all_members, ensure_ascii=False, indent=2)};

export default membersData;
"""
    with open(target_js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"🚀 已成功生成前端 JS 模块：{target_js_path}")

    # 2. 同步生成 src/data/members.json (向后兼容)
    with open(target_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_members, f, ensure_ascii=False, indent=2)
    print(f"📦 已同步更新 JSON 数据：{target_json_path}")

    print("=" * 60)
    print("🎉 成员数据同步全部完成！前端已立即生效。")
    print("=" * 60)

def import_time():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    main()
