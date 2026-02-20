# 小鹅通内容自动监控系统使用指南

## 📋 系统概述

这是一个完全自动化的小鹅通内容监控系统，可以：

1. ✅ **自动登录**小鹅通账号
2. ✅ **定时监控**猫哥发布的图文和视频
3. ✅ **自动下载**新发布的图文截图
4. ✅ **自动分析**图文内容并预测笑脸
5. ✅ **自动推送**分析结果到企业微信
6. ✅ **记录视频**信息（标题、时间、链接）

## 🚀 快速部署

### 步骤1: 安装依赖

在服务器上执行：

```bash
# 安装Playwright
sudo pip3 install playwright

# 安装浏览器
sudo playwright install chromium
sudo playwright install-deps chromium

# 或使用系统包管理器
sudo apt-get install -y chromium-browser
```

### 步骤2: 上传文件到服务器

```bash
# 从GitHub更新代码
cd /tmp && rm -rf maoge-signal-reader
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader

# 复制文件
cp xiaoe_monitor.py /root/maoge_advisor/
chmod +x /root/maoge_advisor/xiaoe_monitor.py

# 配置服务
cp services/xiaoe_monitor.service /etc/systemd/system/
```

### 步骤3: 配置小鹅通店铺URL

编辑服务配置文件：

```bash
nano /etc/systemd/system/xiaoe_monitor.service
```

修改 `ExecStart` 行中的店铺URL：

```ini
ExecStart=/usr/bin/python3 /root/maoge_advisor/xiaoe_monitor.py \
  --shop-url "https://你的小鹅通店铺URL/" \
  --interval 3600 \
  --headless
```

### 步骤4: 首次登录（重要）

**首次运行需要手动登录一次**，之后会自动保持登录状态。

```bash
# 以非headless模式运行，方便登录
cd /root/maoge_advisor
python3 xiaoe_monitor.py \
  --shop-url "https://你的小鹅通店铺URL/" \
  --interval 3600
```

在打开的浏览器窗口中：
1. 使用微信扫码登录，或
2. 使用手机号+验证码登录

登录成功后，系统会自动保存登录状态到 `/root/maoge_advisor/xiaoe_data/login_state.json`

按 `Ctrl+C` 停止测试运行。

### 步骤5: 启动服务

```bash
# 重新加载配置
systemctl daemon-reload

# 启动服务
systemctl enable xiaoe_monitor.service
systemctl start xiaoe_monitor.service

# 检查状态
systemctl status xiaoe_monitor.service

# 查看日志
journalctl -u xiaoe_monitor.service -f
```

## 📖 使用方法

### 自动监控模式

系统启动后会自动：

1. **每小时检查一次**小鹅通店铺
2. **发现新图文**时：
   - 自动截图保存
   - 触发图文解读分析
   - 推送分析结果到企业微信
3. **发现新视频**时：
   - 记录视频信息（标题、时间、链接）
   - 保存到数据库

### 手动触发检查

```bash
# 立即检查一次
python3 /root/maoge_advisor/xiaoe_monitor.py \
  --shop-url "https://你的小鹅通店铺URL/" \
  --interval 60
```

### 查看监控历史

```bash
# 查看内容历史记录
cat /root/maoge_advisor/xiaoe_data/content_history.json

# 查看下载的图文
ls -lh /root/maoge_advisor/maoge_images/

# 查看日志
tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

## ⚙️ 配置选项

### 修改检查间隔

编辑服务配置：

```bash
nano /etc/systemd/system/xiaoe_monitor.service
```

修改 `--interval` 参数：

```ini
# 每30分钟检查一次
--interval 1800

# 每2小时检查一次
--interval 7200
```

重启服务：

```bash
systemctl daemon-reload
systemctl restart xiaoe_monitor.service
```

### 修改监控时间段

如果只想在交易日的特定时间段监控，可以使用cron定时任务：

```bash
# 编辑crontab
crontab -e

# 添加以下行（工作日8:00启动，20:00停止）
0 8 * * 1-5 systemctl start xiaoe_monitor.service
0 20 * * 1-5 systemctl stop xiaoe_monitor.service
```

## 📊 工作流程

```
小鹅通发布新内容
    ↓
监控系统检测到更新（每小时）
    ↓
自动下载图文截图
    ↓
保存到 /root/maoge_advisor/maoge_images/
    ↓
触发图文解读系统
    ↓
OCR提取文字 → 语义分析 → 预测笑脸
    ↓
推送分析结果到企业微信 ✅
    ↓
记录到数据库
```

## 🔧 管理命令

### 查看服务状态

```bash
systemctl status xiaoe_monitor.service
```

### 启动/停止/重启服务

```bash
systemctl start xiaoe_monitor.service
systemctl stop xiaoe_monitor.service
systemctl restart xiaoe_monitor.service
```

### 查看实时日志

```bash
# 系统日志
journalctl -u xiaoe_monitor.service -f

# 应用日志
tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

### 查看内容历史

```bash
# 格式化输出JSON
cat /root/maoge_advisor/xiaoe_data/content_history.json | python3 -m json.tool
```

## 🐛 故障排查

### 问题1: 登录失败

**症状**：日志显示"登录超时"

**解决方案**：
1. 停止服务
2. 手动运行一次（非headless模式）
3. 在浏览器中完成登录
4. 重新启动服务

```bash
systemctl stop xiaoe_monitor.service
cd /root/maoge_advisor
python3 xiaoe_monitor.py --shop-url "https://你的店铺URL/" --interval 3600
# 完成登录后按Ctrl+C
systemctl start xiaoe_monitor.service
```

### 问题2: 找不到新内容

**症状**：日志显示"发现新图文: 0个"

**可能原因**：
1. 页面结构变化，选择器失效
2. 店铺URL不正确
3. 内容不在课程列表中

**解决方案**：
1. 检查店铺URL是否正确
2. 手动访问店铺，查看内容位置
3. 根据实际页面结构调整代码中的选择器

### 问题3: Playwright安装失败

**症状**：提示"chromium not found"

**解决方案**：

```bash
# 重新安装Playwright
sudo pip3 install --upgrade playwright

# 安装浏览器
sudo playwright install chromium
sudo playwright install-deps chromium

# 或使用系统包
sudo apt-get update
sudo apt-get install -y chromium-browser
```

### 问题4: 服务无法启动

**症状**：`systemctl status` 显示 failed

**解决方案**：

```bash
# 查看详细错误
journalctl -u xiaoe_monitor.service -n 50

# 检查Python路径
which python3

# 检查文件权限
ls -lh /root/maoge_advisor/xiaoe_monitor.py

# 手动测试运行
cd /root/maoge_advisor
python3 xiaoe_monitor.py --shop-url "https://店铺URL/" --interval 60
```

## 📈 性能优化

### 减少资源占用

1. **使用headless模式**（默认已启用）
2. **增加检查间隔**（减少请求频率）
3. **限制并发下载**（避免同时下载多个内容）

### 提高响应速度

1. **减少检查间隔**（如30分钟检查一次）
2. **使用SSD存储**（加快文件读写）
3. **优化网络连接**（使用更快的DNS）

## 🔒 安全建议

1. **定期更新依赖**：
   ```bash
   sudo pip3 install --upgrade playwright requests openai
   ```

2. **备份登录状态**：
   ```bash
   cp /root/maoge_advisor/xiaoe_data/login_state.json /root/backups/
   ```

3. **监控日志大小**：
   ```bash
   # 设置日志轮转
   sudo nano /etc/logrotate.d/xiaoe_monitor
   ```

4. **限制访问权限**：
   ```bash
   chmod 600 /root/maoge_advisor/xiaoe_data/login_state.json
   ```

## 📞 技术支持

如遇到问题，请：

1. 查看日志文件
2. 检查网络连接
3. 验证店铺URL
4. 确认登录状态

## 🎯 未来改进

- [ ] 支持多店铺监控
- [ ] 支持视频下载
- [ ] 支持音频提取
- [ ] 支持评论监控
- [ ] 支持Webhook通知
- [ ] 支持自定义过滤规则

## 📝 更新日志

### v1.0.0 (2026-02-17)
- ✅ 初始版本发布
- ✅ 支持图文自动下载
- ✅ 支持视频信息记录
- ✅ 集成图文解读系统
- ✅ 支持企业微信推送
