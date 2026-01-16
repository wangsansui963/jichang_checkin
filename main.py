import requests
import json
import os
import traceback
import time

# 环境变量
# AIRPORT_CONFIG: JSON string [{"url": "...", "email": "...", "password": "..."}, ...]
# WECOM_WEBHOOK: Enterprise WeChat Webhook URL
# SCKEY: ServerChan Key (Optional, Legacy)

def load_config():
    config_list = []
    
    # Try loading JSON config first
    json_config = os.environ.get('AIRPORT_CONFIG')
    if json_config:
        try:
            config_list = json.loads(json_config)
            print("Loaded configuration from AIRPORT_CONFIG")
        except json.JSONDecodeError:
            print("Error: AIRPORT_CONFIG is not valid JSON")
    
    # If no JSON config, try legacy format
    if not config_list:
        url = os.environ.get('URL')
        config_str = os.environ.get('CONFIG')
        
        if url and config_str:
            print("Loading configuration from legacy URL and CONFIG environment variables")
            lines = config_str.splitlines()
            if len(lines) % 2 == 0 and len(lines) > 0:
                for i in range(0, len(lines), 2):
                    config_list.append({
                        'url': url,
                        'email': lines[i].strip(),
                        'password': lines[i+1].strip()
                    })
            else:
                print("Warning: CONFIG format incorrect (should be email, password lines)")
    
    return config_list

def checkin(account):
    url = account.get('url')
    email = account.get('email')
    password = account.get('password')
    
    if not url or not email or not password:
        return f"配置缺失: {account}"
        
    # Ensure URL doesn't end with /
    url = url.rstrip('/')
    
    login_url = f'{url}/auth/login'
    check_url = f'{url}/user/checkin'
    
    session = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Origin': url,
        'Referer': f'{url}/auth/login'
    }
    
    data = {
        'email': email,
        'passwd': password,
        'code': ''
    }
    
    log_prefix = f"[{email} @ {url}]"
    logs = []
    
    try:
        print(f'{log_prefix} Logging in...')
        login_res = session.post(url=login_url, headers=headers, data=data, timeout=30)
        
        try:
            login_json = login_res.json()
            logs.append(f"登录: {login_json.get('msg', 'Unknown')}")
        except:
            logs.append(f"登录响应解析失败: {login_res.text[:100]}")
            return f"{log_prefix} " + " | ".join(logs)

        # Checkin
        print(f'{log_prefix} Checking in...')
        check_res = session.post(url=check_url, headers=headers, timeout=30)
        
        try:
            check_json = check_res.json()
            msg = check_json.get('msg', 'Unknown')
            ret = check_json.get('ret', 0)
            # unescape unicode if needed, but json parser does it
            logs.append(f"签到: {msg}")
        except:
             logs.append(f"签到响应解析失败: {check_res.text[:100]}")
             
    except Exception as e:
        logs.append(f"异常: {str(e)}")
        # traceback.print_exc()
        
    return f"{log_prefix} " + " | ".join(logs)

def send_wecom(webhook_url, content):
    if not webhook_url:
        return
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    
    try:
        res = requests.post(webhook_url, json=data, timeout=10)
        print(f"WeCom notification result: {res.text}")
    except Exception as e:
        print(f"WeCom notification failed: {e}")

def send_serverchan(sckey, content):
    if not sckey:
        return
        
    push_url = f'https://sctapi.ftqq.com/{sckey}.send'
    data = {
        'title': '机场签到通知',
        'desp': content
    }
    
    try:
        requests.post(push_url, data=data, timeout=10)
        print("ServerChan notification sent")
    except Exception as e:
        print(f"ServerChan notification failed: {e}")

def main():
    accounts = load_config()
    if not accounts:
        print("No accounts found in configuration.")
        return

    print(f"Found {len(accounts)} accounts to check in.")
    
    results = []
    for account in accounts:
        res = checkin(account)
        print(res)
        results.append(res)
        # Avoid hitting rate limits if any
        time.sleep(1)
        
    final_content = "机场签到汇总:\n" + "\n".join(results)
    
    # Notifications
    wecom_webhook = os.environ.get('WECOM_WEBHOOK')
    sckey = os.environ.get('SCKEY')
    
    if wecom_webhook:
        print("Sending WeCom notification...")
        send_wecom(wecom_webhook, final_content)
    
    if sckey:
        print("Sending ServerChan notification...")
        send_serverchan(sckey, final_content)

if __name__ == '__main__':
    main()
