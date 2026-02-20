# 本地电脑操作指南 - 小鹅通登录助手

## 📋 目录

1. [系统要求](#系统要求)
2. [macOS 操作指南](#macos-操作指南)
3. [Windows 操作指南](#windows-操作指南)
4. [Linux 操作指南](#linux-操作指南)
5. [常见问题](#常见问题)
6. [视频教程](#视频教程)

---

## 系统要求

### 硬件要求

- **处理器**: 任何现代CPU（Intel/AMD/Apple Silicon）
- **内存**: 至少 2GB 可用内存
- **磁盘空间**: 至少 1GB 可用空间（用于安装浏览器）
- **网络**: 稳定的互联网连接

### 软件要求

- **Python**: 3.8 或更高版本
- **操作系统**: 
  - macOS 10.13 (High Sierra) 或更高
  - Windows 10 或更高
  - Linux (Ubuntu 18.04+, Debian 10+, CentOS 7+, 等)
- **图形界面**: 必须有桌面环境（不能是纯命令行）

---

## macOS 操作指南

### 步骤1: 检查 Python 版本

打开 **终端** (Terminal)：
- 按 `Command + 空格`，输入 "Terminal"，按回车

在终端中输入：

```bash
python3 --version
```

**预期输出**：
```
Python 3.8.x 或更高版本
```

如果显示版本低于 3.8 或提示未找到命令，请先安装 Python：

```bash
# 使用 Homebrew 安装（推荐）
# 如果没有 Homebrew，先安装：
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python3
```

或者从官网下载安装：https://www.python.org/downloads/macos/

---

### 步骤2: 下载项目代码

#### 方法A: 使用 Git（推荐）

```bash
# 检查是否已安装 Git
git --version

# 如果未安装，使用 Homebrew 安装
brew install git

# 克隆项目
cd ~/Desktop  # 或任何你想保存的位置
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
```

#### 方法B: 直接下载 ZIP

1. 访问：https://github.com/clarinetsun-27/maoge-signal-reader
2. 点击绿色的 "Code" 按钮
3. 选择 "Download ZIP"
4. 解压下载的文件
5. 在终端中进入解压后的目录：

```bash
cd ~/Downloads/maoge-signal-reader-master
```

---

### 步骤3: 安装依赖

```bash
# 安装 Playwright
pip3 install playwright

# 安装浏览器（Chromium）
python3 -m playwright install chromium
```

**预期输出**：
```
Downloading Chromium 119.0.6045.9 (playwright build v1091)
...
✔ Chromium 119.0.6045.9 (playwright build v1091) downloaded to /Users/你的用户名/Library/Caches/ms-playwright/chromium-1091
```

**⏱️ 预计时间**: 2-5 分钟（取决于网速）

---

### 步骤4: 运行登录助手

```bash
python3 xiaoe_login_helper.py
```

**预期输出**：

```
============================================================
小鹅通登录助手 - 本地版
============================================================

默认店铺URL: https://appqpljfemv4802.h5.xiaoeknow.com/
如需使用其他URL，请按 Ctrl+C 退出，然后运行:
  python xiaoe_login_helper.py <店铺URL>

按 Enter 使用默认URL...
```

按 **Enter** 键继续。

---

### 步骤5: 在浏览器中完成登录

浏览器会自动打开并显示小鹅通页面。

**登录选项**：

#### 选项1: 微信扫码登录

1. 点击 "微信登录" 按钮
2. 打开手机微信
3. 扫描页面上的二维码
4. 在手机上点击 "确认登录"

#### 选项2: 手机验证码登录

1. 输入手机号
2. 点击 "获取验证码"
3. 输入收到的验证码
4. 点击 "登录"

**验证登录成功**：

登录后，页面应该显示：
- 个人头像或用户名
- "我的" 或 "个人中心" 按钮
- 课程列表

---

### 步骤6: 保存登录凭证

回到终端窗口，按 **Enter** 键。

**预期输出**：

```
🔍 正在验证登录状态...
💾 正在保存登录凭证...
✅ 登录凭证已保存到: xiaoe_auth.json

📊 凭证信息:
  - Cookies数量: 15
  - 文件大小: 3456 字节

============================================================
✅ 登录成功！
============================================================

下一步：将 xiaoe_auth.json 上传到服务器

上传命令:
  scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/

然后在服务器上执行:
  sudo chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json
  sudo systemctl restart xiaoe_monitor.service

============================================================

按 Enter 键关闭浏览器...
```

按 **Enter** 关闭浏览器。

---

### 步骤7: 上传凭证到服务器

```bash
# 上传凭证文件
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/

# 输入服务器密码后，等待上传完成
```

**预期输出**：
```
xiaoe_auth.json                    100% 3456    45.2KB/s   00:00
```

---

### 步骤8: 在服务器上激活凭证

```bash
# SSH 连接到服务器
ssh root@47.100.32.41

# 设置文件权限
chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json

# 重启监控服务
systemctl restart xiaoe_monitor.service

# 查看服务状态
systemctl status xiaoe_monitor.service

# 查看实时日志（确认登录成功）
tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

**成功标志**（在日志中）：
```
✅ 已加载登录状态: xiaoe_auth.json
✅ 已登录，跳过登录流程
```

按 `Ctrl + C` 退出日志查看。

---

## Windows 操作指南

### 步骤1: 检查 Python 版本

打开 **命令提示符** (CMD) 或 **PowerShell**：
- 按 `Windows + R`
- 输入 `cmd` 或 `powershell`
- 按回车

在命令行中输入：

```cmd
python --version
```

或

```cmd
python3 --version
```

**预期输出**：
```
Python 3.8.x 或更高版本
```

如果未安装或版本过低，请从官网下载安装：
- 访问：https://www.python.org/downloads/windows/
- 下载最新的 Python 3.x 安装包
- **重要**: 安装时勾选 "Add Python to PATH"

---

### 步骤2: 下载项目代码

#### 方法A: 使用 Git（推荐）

```cmd
# 检查是否已安装 Git
git --version

# 如果未安装，从官网下载：https://git-scm.com/download/win

# 克隆项目
cd %USERPROFILE%\Desktop
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
```

#### 方法B: 直接下载 ZIP

1. 访问：https://github.com/clarinetsun-27/maoge-signal-reader
2. 点击绿色的 "Code" 按钮
3. 选择 "Download ZIP"
4. 解压到桌面或任意位置
5. 在命令行中进入目录：

```cmd
cd %USERPROFILE%\Downloads\maoge-signal-reader-master
```

---

### 步骤3: 安装依赖

```cmd
# 安装 Playwright
pip install playwright

# 如果上面命令不工作，尝试：
python -m pip install playwright

# 安装浏览器（Chromium）
python -m playwright install chromium
```

**预期输出**：
```
Downloading Chromium 119.0.6045.9 (playwright build v1091)
...
✔ Chromium 119.0.6045.9 downloaded to C:\Users\你的用户名\AppData\Local\ms-playwright\chromium-1091
```

**⏱️ 预计时间**: 2-5 分钟

---

### 步骤4: 运行登录助手

```cmd
python xiaoe_login_helper.py
```

或

```cmd
python3 xiaoe_login_helper.py
```

**预期输出**：

```
============================================================
小鹅通登录助手 - 本地版
============================================================

默认店铺URL: https://appqpljfemv4802.h5.xiaoeknow.com/
...

按 Enter 使用默认URL...
```

按 **Enter** 键继续。

---

### 步骤5: 在浏览器中完成登录

（与 macOS 相同，参见上文）

---

### 步骤6: 保存登录凭证

回到命令行窗口，按 **Enter** 键。

（输出与 macOS 相同）

---

### 步骤7: 上传凭证到服务器

#### 方法A: 使用 SCP（需要安装 Git Bash 或 WSL）

在 **Git Bash** 中：

```bash
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
```

#### 方法B: 使用 WinSCP（图形界面工具）

1. 下载并安装 WinSCP：https://winscp.net/
2. 打开 WinSCP
3. 连接信息：
   - 主机名：47.100.32.41
   - 用户名：root
   - 密码：（您的服务器密码）
4. 连接成功后，将 `xiaoe_auth.json` 拖拽到 `/root/maoge_advisor/xiaoe_data/` 目录

#### 方法C: 使用 PowerShell (Windows 10+)

```powershell
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
```

---

### 步骤8: 在服务器上激活凭证

使用 **PuTTY** 或 **PowerShell SSH** 连接到服务器：

```powershell
ssh root@47.100.32.41
```

然后执行：

```bash
chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json
systemctl restart xiaoe_monitor.service
systemctl status xiaoe_monitor.service
tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

---

## Linux 操作指南

### 步骤1: 检查 Python 版本

打开终端，输入：

```bash
python3 --version
```

**预期输出**：
```
Python 3.8.x 或更高版本
```

如果未安装或版本过低：

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### CentOS/RHEL

```bash
sudo yum install python3 python3-pip
```

#### Fedora

```bash
sudo dnf install python3 python3-pip
```

---

### 步骤2: 下载项目代码

```bash
# 安装 Git（如果未安装）
sudo apt install git  # Ubuntu/Debian
# 或
sudo yum install git  # CentOS/RHEL

# 克隆项目
cd ~/Desktop  # 或任何位置
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
```

---

### 步骤3: 安装依赖

```bash
# 安装 Playwright
pip3 install playwright

# 安装浏览器（Chromium）
python3 -m playwright install chromium

# 如果遇到权限问题，添加 --user
pip3 install --user playwright
python3 -m playwright install chromium
```

**可能需要的系统依赖**（Ubuntu/Debian）：

```bash
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

---

### 步骤4-8: 运行和上传

（与 macOS 相同，参见上文）

---

## 常见问题

### Q1: 提示 "playwright 未安装"

**解决方案**：

```bash
# macOS/Linux
pip3 install playwright
python3 -m playwright install chromium

# Windows
pip install playwright
python -m playwright install chromium
```

---

### Q2: 浏览器无法打开

**可能原因**：
1. 浏览器未安装成功
2. 系统缺少依赖库（Linux）
3. 防火墙阻止

**解决方案**：

```bash
# 重新安装浏览器
python3 -m playwright install chromium

# Linux: 安装系统依赖
python3 -m playwright install-deps chromium
```

---

### Q3: 提示 "Command 'python' not found"

**解决方案**：

使用 `python3` 代替 `python`：

```bash
python3 xiaoe_login_helper.py
```

或创建别名（macOS/Linux）：

```bash
alias python=python3
```

---

### Q4: SCP 上传失败

**可能原因**：
1. SSH 连接问题
2. 权限问题
3. 路径错误

**解决方案**：

```bash
# 测试 SSH 连接
ssh root@47.100.32.41 echo "连接成功"

# 使用完整路径
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/xiaoe_auth.json

# Windows: 使用 WinSCP 图形界面工具
```

---

### Q5: 登录后未检测到登录状态

**解决方案**：

如果您确认已经登录成功（能看到个人信息），直接按 Enter 继续即可。脚本会保存当前状态。

---

### Q6: 凭证文件在哪里？

凭证文件 `xiaoe_auth.json` 保存在运行脚本的当前目录：

```bash
# macOS/Linux
ls -lh xiaoe_auth.json

# Windows
dir xiaoe_auth.json
```

---

### Q7: 如何验证凭证是否有效？

上传凭证并重启服务后，查看日志：

```bash
ssh root@47.100.32.41
tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

成功标志：
```
✅ 已加载登录状态: xiaoe_auth.json
✅ 已登录，跳过登录流程
```

---

### Q8: 凭证多久过期？

通常 30-90 天。过期后重新运行登录助手即可。

---

### Q9: 可以在虚拟机中运行吗？

可以，只要虚拟机有图形界面即可。

---

### Q10: 网络代理问题

如果您使用代理，可能需要配置：

```bash
# macOS/Linux
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# Windows (PowerShell)
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"
```

---

## 视频教程

### macOS 演示

（待录制）

### Windows 演示

（待录制）

### Linux 演示

（待录制）

---

## 快速参考卡

### macOS/Linux 一键命令

```bash
# 完整流程
cd ~/Desktop
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
pip3 install playwright
python3 -m playwright install chromium
python3 xiaoe_login_helper.py
# 完成登录后...
scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/
ssh root@47.100.32.41 'chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json && systemctl restart xiaoe_monitor.service'
```

### Windows 一键命令

```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
pip install playwright
python -m playwright install chromium
python xiaoe_login_helper.py
REM 完成登录后，使用 WinSCP 上传文件
```

---

## 故障排查清单

- [ ] Python 版本 >= 3.8
- [ ] 已安装 playwright: `pip3 show playwright`
- [ ] 已安装浏览器: `python3 -m playwright install chromium`
- [ ] 网络连接正常
- [ ] 防火墙未阻止浏览器
- [ ] 有图形界面（不是纯命令行）
- [ ] 当前目录正确（在 maoge-signal-reader 目录中）
- [ ] 登录成功后看到个人信息
- [ ] xiaoe_auth.json 文件已生成
- [ ] SCP 上传成功
- [ ] 服务器上文件权限正确（600）
- [ ] 服务已重启

---

## 技术支持

如果遇到问题：

1. **查看详细文档**：
   - GitHub: https://github.com/clarinetsun-27/maoge-signal-reader/blob/master/XIAOE_LOGIN_SETUP.md

2. **提交 Issue**：
   - https://github.com/clarinetsun-27/maoge-signal-reader/issues

3. **联系维护者**：
   - 通过 GitHub Issue 或项目说明中的联系方式

---

## 附录：完整错误信息收集

如果需要寻求帮助，请提供以下信息：

```bash
# 系统信息
uname -a  # macOS/Linux
systeminfo  # Windows

# Python 版本
python3 --version

# Playwright 版本
pip3 show playwright

# 错误日志
python3 xiaoe_login_helper.py 2>&1 | tee error.log
```

---

**文档版本**: 1.0  
**最后更新**: 2026-02-20  
**适用平台**: macOS, Windows, Linux  
**维护者**: Tommy
