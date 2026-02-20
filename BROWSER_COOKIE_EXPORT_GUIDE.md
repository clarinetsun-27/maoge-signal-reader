# 浏览器 Cookie 导出指南

## 📋 概述

本指南帮助您从常规浏览器中导出小鹅通的登录 Cookie，然后转换为系统可用的凭证文件。

---

## 🌐 支持的浏览器

- ✅ Google Chrome
- ✅ Microsoft Edge
- ✅ Firefox
- ✅ Brave
- ✅ Opera

---

## 📥 方法一：使用浏览器扩展（最简单）⭐

### Chrome/Edge 用户

#### 步骤1: 安装 Cookie 导出扩展

推荐使用 **"EditThisCookie"** 或 **"Cookie-Editor"**

**EditThisCookie 安装**：
1. 打开 Chrome 网上应用店：https://chrome.google.com/webstore
2. 搜索 "EditThisCookie"
3. 点击"添加至 Chrome"

**Cookie-Editor 安装**（更现代）：
1. 访问：https://chrome.google.com/webstore
2. 搜索 "Cookie-Editor"
3. 点击"添加至 Chrome"

---

#### 步骤2: 登录小鹅通

1. 打开浏览器
2. 访问：https://appqpljfemv4802.h5.xiaoeknow.com/
3. 使用微信扫码或验证码登录
4. 确认登录成功（能看到课程内容）

---

#### 步骤3: 导出 Cookies

**使用 EditThisCookie**：
1. 点击浏览器工具栏中的 EditThisCookie 图标
2. 点击"导出"按钮（Export）
3. Cookies 已复制到剪贴板

**使用 Cookie-Editor**：
1. 点击浏览器工具栏中的 Cookie-Editor 图标
2. 点击"导出"按钮
3. 选择"JSON"格式
4. 点击"复制到剪贴板"

---

#### 步骤4: 保存为文件

1. 打开记事本（Windows）或文本编辑器（macOS）
2. 粘贴复制的 Cookies
3. 保存为 `cookies_export.json`
4. 保存位置：桌面或项目目录

---

### Firefox 用户

#### 步骤1: 安装扩展

1. 访问 Firefox Add-ons：https://addons.mozilla.org/
2. 搜索 "Cookie Quick Manager"
3. 点击"添加到 Firefox"

#### 步骤2-4: 同上

---

## 📥 方法二：使用浏览器开发者工具

### Chrome/Edge

#### 步骤1: 登录小鹅通

1. 访问：https://appqpljfemv4802.h5.xiaoeknow.com/
2. 完成登录

#### 步骤2: 打开开发者工具

按 `F12` 或 `Ctrl+Shift+I`（Windows）/ `Cmd+Option+I`（macOS）

#### 步骤3: 导出 Cookies

1. 点击顶部的 **"Application"** 标签
2. 左侧展开 **"Storage"** → **"Cookies"**
3. 点击 `https://appqpljfemv4802.h5.xiaoeknow.com`
4. 在 Cookies 列表中，按 `Ctrl+A` 全选
5. 右键点击 → **"Copy"** → **"Copy all as JSON"**

如果没有"Copy all as JSON"选项：

**手动复制方法**：
1. 在 Console 标签中，粘贴以下代码：

```javascript
// 获取所有 Cookies 并导出为 JSON
const cookies = document.cookie.split(';').map(c => {
    const [name, value] = c.trim().split('=');
    return {
        name: name,
        value: value,
        domain: window.location.hostname,
        path: '/',
        secure: window.location.protocol === 'https:',
        httpOnly: false,
        sameSite: 'Lax'
    };
});
console.log(JSON.stringify(cookies, null, 2));
copy(JSON.stringify(cookies, null, 2));
```

2. 按 `Enter` 执行
3. Cookies 已复制到剪贴板

#### 步骤4: 保存为文件

1. 打开记事本
2. 粘贴
3. 保存为 `cookies_export.json`

---

### Firefox

#### 步骤1-2: 同上

#### 步骤3: 导出 Cookies

1. 按 `F12` 打开开发者工具
2. 点击 **"Storage"** 标签
3. 左侧展开 **"Cookies"**
4. 点击对应的域名
5. 右键点击任意 Cookie → **"Select All"**
6. 右键 → **"Copy"**

或使用控制台方法（同 Chrome）。

---

## 🔄 方法三：使用转换工具（推荐）

我已经为您准备了一个自动转换工具。

### 步骤1: 导出 Cookies

使用上述任意方法导出 Cookies，保存为 `cookies_export.json`

### 步骤2: 运行转换工具

```bash
# 进入项目目录
cd maoge-signal-reader

# 运行转换工具
python cookie_converter.py cookies_export.json
```

工具会自动：
- ✅ 读取导出的 Cookies
- ✅ 转换为 Playwright 格式
- ✅ 生成 `xiaoe_auth.json`
- ✅ 验证格式正确性

### 步骤3: 上传到服务器

```bash
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
```

---

## 📋 Cookie 格式说明

### EditThisCookie 格式

```json
[
  {
    "domain": ".xiaoeknow.com",
    "expirationDate": 1740000000,
    "hostOnly": false,
    "httpOnly": false,
    "name": "session_id",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "abc123...",
    "id": 1
  }
]
```

### Cookie-Editor 格式

```json
[
  {
    "domain": ".xiaoeknow.com",
    "expirationDate": 1740000000,
    "hostOnly": false,
    "httpOnly": false,
    "name": "session_id",
    "path": "/",
    "sameSite": "lax",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "abc123..."
  }
]
```

### Playwright 格式（目标格式）

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123...",
      "domain": ".xiaoeknow.com",
      "path": "/",
      "expires": 1740000000,
      "httpOnly": false,
      "secure": true,
      "sameSite": "Lax"
    }
  ],
  "origins": []
}
```

---

## ✅ 验证 Cookies 有效性

### 方法1: 使用在线工具

1. 访问：https://reqbin.com/
2. 输入小鹅通 URL
3. 添加 Cookie 头
4. 发送请求，检查是否返回登录状态

### 方法2: 使用转换工具验证

```bash
python cookie_converter.py cookies_export.json --verify
```

---

## 🔧 故障排查

### 问题1: 导出的 Cookies 为空

**原因**: 未登录或 Cookies 已过期

**解决方案**:
1. 确保已成功登录小鹅通
2. 刷新页面
3. 重新导出

---

### 问题2: 导出的格式不正确

**原因**: 浏览器扩展版本问题

**解决方案**:
1. 使用开发者工具手动导出
2. 或使用转换工具自动修复格式

---

### 问题3: 上传后服务器无法使用

**原因**: Cookie 格式不兼容

**解决方案**:
1. 使用 `cookie_converter.py` 转换
2. 确保生成的是 Playwright 格式

---

## 📚 推荐工作流程

### 完整流程（推荐）⭐

```
1. 安装浏览器扩展（Cookie-Editor）
   ↓
2. 在常规浏览器中登录小鹅通
   ↓
3. 使用扩展导出 Cookies（JSON格式）
   ↓
4. 保存为 cookies_export.json
   ↓
5. 运行转换工具: python cookie_converter.py cookies_export.json
   ↓
6. 生成 xiaoe_auth.json
   ↓
7. 上传到服务器: scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
   ↓
8. 激活凭证: ssh root@47.100.32.41 'systemctl restart xiaoe_monitor.service'
   ↓
9. 验证成功: tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

---

## 🔐 安全提示

- ⚠️ **Cookie 包含敏感信息**，不要分享给他人
- ⚠️ **不要上传到公共位置**（如 GitHub）
- ⚠️ **定期更新 Cookie**（建议每月一次）
- ⚠️ **使用后删除本地的 cookies_export.json**

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 [常见问题](#故障排查)
2. 查看转换工具的错误提示
3. 提交 GitHub Issue

---

## 🎯 快速参考

### Chrome/Edge 快速命令

```javascript
// 在 Console 中执行，一键导出 Cookies
copy(JSON.stringify(document.cookie.split(';').map(c => {
    const [name, value] = c.trim().split('=');
    return {name, value, domain: location.hostname, path: '/', secure: location.protocol === 'https:', httpOnly: false, sameSite: 'Lax'};
}), null, 2));
```

### 完整命令行流程

```bash
# 1. 转换 Cookies
python cookie_converter.py cookies_export.json

# 2. 上传到服务器
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/

# 3. 激活凭证
ssh root@47.100.32.41 'chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json && systemctl restart xiaoe_monitor.service'

# 4. 验证
ssh root@47.100.32.41 'tail -20 /root/maoge_advisor/logs/xiaoe_monitor.log'
```

---

**文档版本**: 1.0  
**最后更新**: 2026-02-20  
**维护者**: Tommy
