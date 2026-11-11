import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

# 确保在各平台终端标准输出均使用 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CF_TOKEN = os.environ.get('CF_ACCESS_TOKEN')
CF_ACCOUNT_ID = os.environ.get('CF_ACCOUNT_ID')

# 最大在册席位水位线（超过此阈值即自动按 LRU 淘汰最久未登录用户，严格压降至此水平）
MAX_SEAT_LIMIT = 45

# 超级管理员账号豁免白名单（绝对不可误删，永久受保护）
EXEMPT_EMAILS = {
    'zxw@zxw.ac.cn',
    'zxwujs@gmail.com'
}

if not CF_TOKEN or not CF_ACCOUNT_ID:
    print("Error: CF_ACCESS_TOKEN or CF_ACCOUNT_ID environment variable not set.")
    sys.exit(1)

headers = {
    'Authorization': f'Bearer {CF_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 65)
print("[Robot] 王小治课题组 Cloudflare Zero Trust 席位智能巡航机器人")
print(f"[Robot] 当前执行时间 (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
print(f"[Robot] 席位安全警戒线设定: {MAX_SEAT_LIMIT} 人 (超过立即按最后登录时间淘汰)")
print(f"[Robot] 永久豁免保护管理员: {', '.join(EXEMPT_EMAILS)}")
print("=" * 65)

# 1. 获取所有在册 Access 用户
req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/access/users',
    headers=headers
)

try:
    with urllib.request.urlopen(req) as resp:
        users = json.loads(resp.read().decode('utf-8')).get('result', [])
except Exception as e:
    print(f"[ERR] 获取用户列表失败: {e}")
    sys.exit(1)

total_count = len(users)
print(f"[*] 当前系统在册占用席位总数: {total_count} / 50 (Cloudflare 免费版上限 50)")

now = datetime.now(timezone.utc)

# 解析并格式化所有用户信息
parsed_users = []
for u in users:
    email = u.get('email', '未知邮箱').strip().lower()
    uid = u.get('id')
    last_login_str = u.get('last_successful_login')

    last_login_dt = None
    inactive_days = 99999  # 若从无登录记录，赋予最大天数优先淘汰

    if last_login_str:
        try:
            last_login_dt = datetime.fromisoformat(last_login_str.replace('Z', '+00:00'))
            inactive_days = (now - last_login_dt).days
        except Exception:
            pass

    is_exempt = email in EXEMPT_EMAILS

    parsed_users.append({
        'uid': uid,
        'email': email,
        'last_login_str': last_login_str or '从未登录',
        'last_login_dt': last_login_dt,
        'inactive_days': inactive_days,
        'is_exempt': is_exempt
    })

print("\n--- [在册成员状态清单 (按登录活跃度由旧至新排序)] ---")

# 排序规则：
# 1. 豁免账号排在最后（绝对不淘汰）
# 2. 从未登录过的排在最前（优先淘汰）
# 3. 登录时间越久远（inactive_days 越大）排越前
def sort_key(user):
    if user['is_exempt']:
        return (1, 0)  # 豁免账号
    # 未登录优先
    if user['last_login_dt'] is None:
        return (0, 0)
    # 按最后登录时间戳升序（时间越早越小，排越前）
    return (0, user['last_login_dt'].timestamp())

sorted_users = sorted(parsed_users, key=sort_key)

for idx, u in enumerate(sorted_users, 1):
    tag = " [👑豁免管理员]" if u['is_exempt'] else ""
    print(f"{idx:02d}. 用户: {u['email']:<28} | 最后登录: {u['last_login_str']:<22} | 未登录: {u['inactive_days']}天{tag}")

# 2. 判断是否超过安全水位线 (45 人)
excess_count = total_count - MAX_SEAT_LIMIT
cleaned_count = 0

if excess_count <= 0:
    print("\n[OK] 席位状态极佳！当前人数未超过 45 人安全水位线，无需执行淘汰。")
else:
    print(f"\n[!] 警告：当前在册席位 ({total_count}) 已超过 {MAX_SEAT_LIMIT} 人水位线！")
    print(f"[!] 正在自动按【最后登录时间最久远】顺序淘汰清理 {excess_count} 名不活跃用户，以保持在 {MAX_SEAT_LIMIT} 人水平...")

    # 从排序后的列表中筛选可淘汰的用户（排除管理员）
    candidates_to_delete = [u for u in sorted_users if not u['is_exempt']][:excess_count]

    for victim in candidates_to_delete:
        v_email = victim['email']
        v_uid = victim['uid']
        v_last = victim['last_login_str']
        v_days = victim['inactive_days']

        print(f"\n>>> 正在淘汰注销: {v_email} (最后登录: {v_last}, 距今 {v_days} 天)...")

        del_req = urllib.request.Request(
            f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/access/users/{v_uid}',
            headers=headers,
            method='DELETE'
        )
        try:
            with urllib.request.urlopen(del_req) as del_resp:
                res = json.loads(del_resp.read().decode('utf-8'))
                if res.get('success'):
                    print(f"    ✔ 成功释放该席位！({v_email})")
                    cleaned_count += 1
                else:
                    print(f"    ✖ 注销失败: {res.get('errors')}")
        except Exception as err:
            print(f"    ✖ 删除请求异常: {err}")

print("\n" + "=" * 65)
print(f"[Done] 巡航任务完成！本次共自动回收清理 {cleaned_count} 个席位。")
print(f"[Done] 最终当前在册席位数: {total_count - cleaned_count} / {MAX_SEAT_LIMIT} 人。")
print("=" * 65)
