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

if not CF_TOKEN or not CF_ACCOUNT_ID:
    print("Error: CF_ACCESS_TOKEN or CF_ACCOUNT_ID environment variable not set.")
    sys.exit(1)

headers = {
    'Authorization': f'Bearer {CF_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 60)
print("[Robot] 开始执行：王小治课题组 Zero Trust 席位巡检与半年不活跃清理机器人")
print(f"[Robot] 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# 获取所有在册 Access 用户
req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/access/users',
    headers=headers
)

try:
    with urllib.request.urlopen(req) as resp:
        users = json.loads(resp.read().decode('utf-8')).get('result', [])
except Exception as e:
    print(f"获取用户列表失败: {e}")
    sys.exit(1)

print(f"[*] 当前在册占用席位总数: {len(users)} / 50")

now = datetime.now(timezone.utc)
cleaned_count = 0

for u in users:
    email = u.get('email', '未知邮箱')
    uid = u.get('id')
    last_login_str = u.get('last_successful_login')

    if not last_login_str:
        print(f"[!] 用户 {email} 无成功登录记录，暂时保留。")
        continue

    # 解析最后登录时间 (格式例如: 2026-11-09T11:07:27Z)
    try:
        last_login = datetime.fromisoformat(last_login_str.replace('Z', '+00:00'))
    except Exception:
        continue

    inactive_days = (now - last_login).days
    print(f"[-] 用户: {email} | 最后登录: {last_login_str} | 已未登录天数: {inactive_days} 天")

    # 超过 180 天（半年）未登录，自动清理释放席位
    if inactive_days >= 180:
        print(f"[!] 用户 {email} 超过 180 天未登录，正在执行清理与席位回收...")
        del_req = urllib.request.Request(
            f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/access/users/{uid}',
            headers=headers,
            method='DELETE'
        )
        try:
            with urllib.request.urlopen(del_req) as del_resp:
                res = json.loads(del_resp.read().decode('utf-8'))
                if res.get('success'):
                    print(f"[OK] 成功注销用户 {email}，已释放 1 个免费席位！")
                    cleaned_count += 1
                else:
                    print(f"[ERR] 注销用户 {email} 失败: {res.get('errors')}")
        except Exception as err:
            print(f"[ERR] 调用删除接口异常: {err}")

print("-" * 60)
print(f"[Done] 巡检完成！本次共自动清理释放 {cleaned_count} 个不活跃席位。")
print("=" * 60)
