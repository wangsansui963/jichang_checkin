# 通用机场签到😍<br/>
> 只要机场网站 **Powered by SSPANEL**，就可以进行签到。要确认是否是 **Powered by SSPANEL**，在机场首页滑倒最底端就可以看到。

## 作用
> 每天进行签到，获取额外的流量奖励

## 推送方式
支持以下推送方式：
1. **企业微信 Webhook** (推荐): 配置 `WECOM_WEBHOOK` 环境变量。
2. **Server酱**: 配置 `SCKEY` 环境变量。

## 部署配置

### 方法一：多机场多账号配置 (推荐)
在 `Settings` -> `Secrets and variables` -> `Actions` 新建以下 Secrets：

| 参数 | 内容 | 说明 |
| --- | --- | --- |
| `AIRPORT_CONFIG` | JSON 格式的账号列表 | 见下方示例 |
| `WECOM_WEBHOOK` | 企业微信群机器人 Webhook 地址 | 可选，用于推送通知 |
| `SCKEY` | Server酱 Key | 可选，用于推送通知 |

**AIRPORT_CONFIG 示例:**
```json
[
  {
    "url": "https://airport1.com",
    "email": "user1@example.com",
    "password": "password1"
  },
  {
    "url": "https://airport2.com",
    "email": "user2@example.com",
    "password": "password2"
  }
]
```

### 方法二：单机场配置 (旧版兼容)
| 参数 | 内容 | 说明 |
| --- | --- | --- |
| `URL` | 机场官网地址 | 例如 https://example.com |
| `CONFIG` | 账号密码列表 | 一行账号一行密码 |
| `SCKEY` | Server酱 Key | 可选 |
| `WECOM_WEBHOOK`| 企业微信 Webhook | 可选 |

**注意**: `URL` 尾部不要加 `/`。

## 部署步骤
1. Fork 此仓库。
2. 配置上述 Secrets。
3. 在 Actions 中启用 Workflow。
