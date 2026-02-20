# 🚀 快速开始指南

## 📌 5分钟完成小鹅通登录配置

本指南帮助您快速完成小鹅通监控系统的登录配置。

---

## ✅ 前置条件

- ✅ 系统已部署到服务器 47.100.32.41
- ✅ 您有一台带图形界面的电脑（macOS/Windows/Linux）
- ✅ 您有小鹅通账号（可以登录 https://appqpljfemv4802.h5.xiaoeknow.com/）

---

## 📋 操作步骤

### 第一步：在本地电脑下载代码

**macOS/Linux:**

```bash
cd ~/Desktop
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
```

**Windows:**

```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
```

**没有 Git？** [点击下载 ZIP](https://github.com/clarinetsun-27/maoge-signal-reader/archive/refs/heads/master.zip)，解压后进入目录。

---

### 第二步：安装依赖

**macOS/Linux:**

```bash
pip3 install playwright
python3 -m playwright install chromium
```

**Windows:**

```cmd
pip install playwright
python -m playwright install chromium
```

⏱️ **预计时间**: 2-5 分钟

---

### 第三步：运行登录助手

**macOS/Linux:**

```bash
python3 xiaoe_login_helper.py
```

**Windows:**

```cmd
python xiaoe_login_helper.py
```

---

### 第四步：在浏览器中登录

浏览器会自动打开小鹅通页面，选择以下任一方式登录：

**方式1: 微信扫码**
- 点击"微信登录"
- 用手机微信扫码
- 在手机上确认登录

**方式2: 手机验证码**
- 输入手机号
- 获取验证码
- 输入验证码登录

登录成功后，回到终端按 **Enter** 键。

---

### 第五步：上传凭证到服务器

**macOS/Linux:**

```bash
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
```

**Windows (Git Bash):**

```bash
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
```

**Windows (图形界面):**

使用 [WinSCP](https://winscp.net/) 上传文件到服务器的 `/root/maoge_advisor/xiaoe_data/` 目录。

---

### 第六步：激活凭证

SSH 连接到服务器：

```bash
ssh root@47.100.32.41
```

执行以下命令：

```bash
# 设置权限
chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json

# 重启服务
systemctl restart xiaoe_monitor.service

# 查看状态
systemctl status xiaoe_monitor.service

# 查看日志（确认登录成功）
tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

---

## ✅ 成功标志

在日志中看到以下内容表示配置成功：

```
✅ 已加载登录状态: xiaoe_auth.json
✅ 已登录，跳过登录流程
⏸️  非交易时间，等待到 09:30:00
```

按 `Ctrl + C` 退出日志查看。

---

## 🎯 系统现在会自动运行

配置完成后，系统将：

- 📅 **交易日** (周一至周五，排除节假日)
- ⏰ **交易时间** (09:30-15:00)
- 🔄 **每3分钟** 自动检查小鹅通平台
- 📥 **自动下载** 猫哥发布的新图文
- 🤖 **自动分析** 并预测笑脸信号
- 📲 **自动推送** 结果到企业微信

---

## ❓ 遇到问题？

### 问题1: Python 未安装或版本过低

**macOS:**
```bash
brew install python3
```

**Windows:**
下载安装：https://www.python.org/downloads/

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3 python3-pip
```

---

### 问题2: playwright 安装失败

```bash
# 使用国内镜像
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple playwright
python3 -m playwright install chromium
```

---

### 问题3: 浏览器无法打开

**Linux 用户**需要安装系统依赖：

```bash
python3 -m playwright install-deps chromium
```

---

### 问题4: SCP 上传失败

**Windows 用户**推荐使用图形界面工具：
- [WinSCP](https://winscp.net/) - 免费的 SFTP/SCP 客户端
- [FileZilla](https://filezilla-project.org/) - 免费的 FTP/SFTP 客户端

---

### 问题5: 凭证过期

凭证通常有效期 30-90 天，过期后重新运行登录助手即可：

```bash
python3 xiaoe_login_helper.py
# 完成登录后重新上传
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
ssh root@47.100.32.41 'systemctl restart xiaoe_monitor.service'
```

---

## 📚 详细文档

- **本地操作详细指南**: [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)
- **登录配置完整文档**: [XIAOE_LOGIN_SETUP.md](XIAOE_LOGIN_SETUP.md)
- **系统部署指南**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🆘 需要帮助？

1. 查看 [常见问题](LOCAL_SETUP_GUIDE.md#常见问题)
2. 查看 [故障排查](XIAOE_LOGIN_SETUP.md#故障排查)
3. 提交 [GitHub Issue](https://github.com/clarinetsun-27/maoge-signal-reader/issues)

---

## 📊 系统监控

### 查看服务状态

```bash
ssh root@47.100.32.41
systemctl status xiaoe_monitor.service
```

### 查看实时日志

```bash
ssh root@47.100.32.41
tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

### 查看今天的分析记录

```bash
ssh root@47.100.32.41
ls -lh /root/maoge_advisor/maoge_images/
```

---

## 🔄 定期维护

### 建议每月更新凭证

即使凭证未过期，建议每月更新一次以确保稳定性：

```bash
# 在本地电脑
python3 xiaoe_login_helper.py
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
ssh root@47.100.32.41 'systemctl restart xiaoe_monitor.service'
```

---

**祝使用顺利！** 🎉

如有任何问题，欢迎随时联系。
