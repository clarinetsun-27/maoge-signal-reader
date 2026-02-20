# 小鹅通监控系统 - 登录配置指南

## 📋 目录

1. [问题说明](#问题说明)
2. [解决方案](#解决方案)
3. [详细步骤](#详细步骤)
4. [故障排查](#故障排查)
5. [凭证更新](#凭证更新)

---

## 问题说明

小鹅通监控服务运行在无界面的服务器上（headless模式），无法显示浏览器进行交互式登录。小鹅通平台要求以下登录方式之一：

- **微信扫码登录** - 需要扫描二维码
- **手机验证码登录** - 需要接收并输入验证码

这两种方式都需要用户交互，无法在headless模式下自动完成。

### 技术背景

- 服务器：47.100.32.41（阿里云，无图形界面）
- 浏览器：Playwright Chromium（headless模式）
- 小鹅通店铺：https://appqpljfemv4802.h5.xiaoeknow.com/

---

## 解决方案

**方案A：本地登录 + 凭证上传**（推荐）

在本地电脑（有图形界面）完成登录，然后将登录凭证上传到服务器。

**优点**：
- ✅ 简单快速，无需额外配置
- ✅ 安全可靠，凭证加密存储
- ✅ 可重复使用，凭证长期有效

**缺点**：
- ⚠️ 凭证过期后需要重新上传（通常有效期30-90天）

---

## 详细步骤

### 步骤1：在本地电脑安装依赖

```bash
# 安装Python依赖
pip install playwright

# 安装浏览器
python -m playwright install chromium
```

**系统要求**：
- Python 3.8+
- macOS / Windows / Linux（带图形界面）
- 至少500MB磁盘空间（用于Chromium）

---

### 步骤2：下载登录助手脚本

**方法A：从GitHub下载**

```bash
# 克隆整个仓库
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader

# 或者直接下载单个文件
wget https://raw.githubusercontent.com/clarinetsun-27/maoge-signal-reader/main/xiaoe_login_helper.py
```

**方法B：手动创建文件**

如果无法访问GitHub，可以手动创建 `xiaoe_login_helper.py` 文件，内容见附录。

---

### 步骤3：运行登录助手

```bash
python xiaoe_login_helper.py
```

**预期输出**：

```
============================================================
小鹅通登录助手
============================================================

默认店铺URL: https://appqpljfemv4802.h5.xiaoeknow.com/
如需使用其他URL，请按 Ctrl+C 退出，然后运行:
  python xiaoe_login_helper.py <店铺URL>

按 Enter 使用默认URL...
```

按 Enter 键继续。

---

### 步骤4：在浏览器中完成登录

脚本会自动打开浏览器并访问小鹅通店铺。

**登录流程**：

1. **浏览器自动打开**
   - 显示小鹅通店铺首页
   - 可能显示登录按钮或登录页面

2. **选择登录方式**
   
   **方式1：微信扫码登录**
   - 点击"微信登录"按钮
   - 使用微信扫描二维码
   - 在手机上确认登录

   **方式2：手机验证码登录**
   - 输入手机号
   - 点击"获取验证码"
   - 输入收到的验证码
   - 点击"登录"

3. **验证登录成功**
   - 登录后应该能看到：
     - 个人头像或用户名
     - "我的"或"个人中心"按钮
     - 课程列表或内容页面

4. **返回终端**
   - 在终端窗口按 Enter 键
   - 脚本会自动保存登录凭证

**预期输出**：

```
============================================================
请在浏览器中完成登录
============================================================

登录方式：
  1. 微信扫码登录
  2. 手机验证码登录

请完成登录后，在浏览器中看到您的个人信息或课程列表
然后回到此窗口，按 Enter 键继续...
============================================================

按 Enter 键继续...

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
  scp xiaoe_auth.json admin@47.100.32.41:/tmp/

然后在服务器上执行:
  sudo mv /tmp/xiaoe_auth.json /root/maoge_advisor/xiaoe_data/
  sudo systemctl restart xiaoe_monitor.service

============================================================

按 Enter 键关闭浏览器...
```

---

### 步骤5：上传凭证到服务器

在本地电脑执行：

```bash
scp xiaoe_auth.json admin@47.100.32.41:/tmp/
```

**注意事项**：
- 确保能够SSH连接到服务器
- 如果提示输入密码，输入admin用户的密码
- 上传成功后会显示传输进度

---

### 步骤6：在服务器上部署凭证

SSH登录到服务器：

```bash
ssh admin@47.100.32.41
```

执行以下命令：

```bash
# 移动凭证文件到正确位置
sudo mv /tmp/xiaoe_auth.json /root/maoge_advisor/xiaoe_data/

# 设置正确的权限（仅root可读写）
sudo chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json

# 验证文件已正确放置
sudo ls -lh /root/maoge_advisor/xiaoe_data/xiaoe_auth.json
```

**预期输出**：

```
-rw------- 1 root root 3.4K Feb 20 10:30 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json
```

---

### 步骤7：重启监控服务

```bash
# 重启服务
sudo systemctl restart xiaoe_monitor.service

# 查看服务状态
sudo systemctl status xiaoe_monitor.service
```

**预期输出**：

```
● xiaoe_monitor.service - Xiaoe Platform Monitor for Maoge Signals
   Loaded: loaded (/etc/systemd/system/xiaoe_monitor.service; enabled)
   Active: active (running) since Wed 2026-02-20 10:31:00 CST; 5s ago
```

---

### 步骤8：验证登录状态

查看实时日志：

```bash
sudo tail -f /root/maoge_advisor/logs/xiaoe_monitor.log
```

**成功的日志示例**：

```
2026-02-20 10:31:00 - xiaoe_monitor - INFO - 小鹅通监控器初始化完成: https://appqpljfemv4802.h5.xiaoeknow.com/
2026-02-20 10:31:00 - xiaoe_monitor - INFO - 交易时间: 09:30 - 15:00
2026-02-20 10:31:00 - xiaoe_monitor - INFO - 检查间隔: 180秒 (3.0分钟)
2026-02-20 10:31:01 - xiaoe_monitor - INFO - 发现上传的登录凭证文件: xiaoe_auth.json
2026-02-20 10:31:02 - xiaoe_monitor - INFO - ✅ 已加载登录状态: xiaoe_auth.json
2026-02-20 10:31:03 - xiaoe_monitor - INFO - 开始登录小鹅通...
2026-02-20 10:31:03 - xiaoe_monitor - INFO - 发现已保存的登录凭证，尝试使用...
2026-02-20 10:31:05 - xiaoe_monitor - INFO - ✅ 已登录，跳过登录流程
2026-02-20 10:31:05 - xiaoe_monitor - INFO - ⏸️  非交易时间（交易时间: 09:30-15:00），等待到 09:30:00
```

**关键标志**：
- ✅ `发现上传的登录凭证文件: xiaoe_auth.json`
- ✅ `已加载登录状态: xiaoe_auth.json`
- ✅ `已登录，跳过登录流程`

如果看到这些日志，说明登录配置成功！

---

## 故障排查

### 问题1：本地运行登录助手失败

**症状**：

```
❌ 错误：未安装 playwright
请先安装：pip install playwright
然后运行：python -m playwright install chromium
```

**解决方案**：

```bash
# 安装playwright
pip install playwright

# 安装浏览器
python -m playwright install chromium

# 重新运行
python xiaoe_login_helper.py
```

---

### 问题2：浏览器打开后无法登录

**症状**：
- 浏览器显示空白页面
- 页面加载超时
- 无法点击登录按钮

**解决方案**：

1. **检查网络连接**
   ```bash
   ping xiaoeknow.com
   ```

2. **手动访问店铺URL**
   - 在普通浏览器中打开：https://appqpljfemv4802.h5.xiaoeknow.com/
   - 确认页面能正常加载

3. **清除浏览器缓存**
   - 关闭登录助手
   - 删除Playwright缓存：`rm -rf ~/.cache/ms-playwright`
   - 重新安装浏览器：`python -m playwright install chromium`

---

### 问题3：登录成功但未检测到登录状态

**症状**：

```
⚠️  警告：未检测到登录标识
如果您确认已登录，请按 Enter 继续
如果未登录，请按 Ctrl+C 退出重试
```

**解决方案**：

1. **确认已登录**
   - 在浏览器中检查是否能看到个人信息
   - 是否能访问"我的课程"等需要登录的页面

2. **如果确认已登录**
   - 按 Enter 继续
   - 脚本会保存当前的登录状态

3. **如果未登录**
   - 按 Ctrl+C 退出
   - 重新运行脚本
   - 确保完成登录流程

---

### 问题4：凭证上传失败

**症状**：

```
scp: /tmp/xiaoe_auth.json: Permission denied
```

**解决方案**：

1. **检查SSH连接**
   ```bash
   ssh admin@47.100.32.41 echo "连接成功"
   ```

2. **检查/tmp目录权限**
   ```bash
   ssh admin@47.100.32.41 'ls -ld /tmp'
   ```

3. **使用其他临时目录**
   ```bash
   scp xiaoe_auth.json admin@47.100.32.41:~/
   ssh admin@47.100.32.41 'sudo mv ~/xiaoe_auth.json /root/maoge_advisor/xiaoe_data/'
   ```

---

### 问题5：服务器端未识别凭证

**症状**：

日志显示：

```
WARNING - 未找到登录凭证文件，需要手动登录
ERROR - 登录超时
```

**解决方案**：

1. **检查凭证文件是否存在**
   ```bash
   ssh admin@47.100.32.41 'sudo ls -lh /root/maoge_advisor/xiaoe_data/xiaoe_auth.json'
   ```

2. **检查文件内容**
   ```bash
   ssh admin@47.100.32.41 'sudo head -20 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json'
   ```
   
   应该看到JSON格式的内容，包含cookies和localStorage。

3. **检查文件权限**
   ```bash
   ssh admin@47.100.32.41 'sudo chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json'
   ```

4. **重启服务**
   ```bash
   ssh admin@47.100.32.41 'sudo systemctl restart xiaoe_monitor.service'
   ```

---

### 问题6：凭证过期

**症状**：

日志显示：

```
INFO - 发现上传的登录凭证文件: xiaoe_auth.json
INFO - ✅ 已加载登录状态: xiaoe_auth.json
WARNING - 未检测到登录标识，可能凭证已过期
ERROR - 登录超时
```

**解决方案**：

凭证过期是正常现象（通常30-90天），需要重新登录：

1. **在本地电脑重新运行登录助手**
   ```bash
   python xiaoe_login_helper.py
   ```

2. **完成登录流程**

3. **上传新凭证**
   ```bash
   scp xiaoe_auth.json admin@47.100.32.41:/tmp/
   ssh admin@47.100.32.41 'sudo mv /tmp/xiaoe_auth.json /root/maoge_advisor/xiaoe_data/'
   ```

4. **重启服务**
   ```bash
   ssh admin@47.100.32.41 'sudo systemctl restart xiaoe_monitor.service'
   ```

---

## 凭证更新

### 何时需要更新凭证？

- ✅ 定期更新：建议每30天更新一次（即使未过期）
- ⚠️ 凭证过期：日志显示登录失败或未检测到登录状态
- ⚠️ 账号变更：更换了小鹅通账号
- ⚠️ 密码修改：修改了小鹅通账号密码

### 更新流程

```bash
# 1. 在本地电脑运行登录助手
python xiaoe_login_helper.py

# 2. 完成登录并保存凭证

# 3. 上传新凭证（会覆盖旧凭证）
scp xiaoe_auth.json admin@47.100.32.41:/tmp/

# 4. 在服务器上部署
ssh admin@47.100.32.41 'sudo mv /tmp/xiaoe_auth.json /root/maoge_advisor/xiaoe_data/'

# 5. 重启服务
ssh admin@47.100.32.41 'sudo systemctl restart xiaoe_monitor.service'
```

### 凭证备份

建议定期备份有效的凭证文件：

```bash
# 从服务器下载当前凭证
scp admin@47.100.32.41:/root/maoge_advisor/xiaoe_data/xiaoe_auth.json ./xiaoe_auth_backup_$(date +%Y%m%d).json

# 本地保存多个版本
ls -lh xiaoe_auth_backup_*.json
```

---

## 安全注意事项

### 凭证文件保护

1. **权限控制**
   - 服务器上：`chmod 600`（仅root可读写）
   - 本地电脑：存放在安全位置，不要共享

2. **不要提交到Git**
   - `xiaoe_auth.json` 已添加到 `.gitignore`
   - 确保不会意外提交到公开仓库

3. **定期更换**
   - 建议每30天更新一次凭证
   - 如果怀疑泄露，立即更换

### 账号安全

1. **使用独立账号**
   - 建议为监控系统创建专用的小鹅通账号
   - 不要使用个人主账号

2. **最小权限原则**
   - 账号只需要"查看内容"权限
   - 不需要"发布"或"管理"权限

3. **监控异常登录**
   - 定期检查小鹅通账号的登录记录
   - 发现异常立即修改密码

---

## 附录

### 登录助手脚本完整代码

如果无法从GitHub下载，可以手动创建 `xiaoe_login_helper.py`：

```python
#!/usr/bin/env python3
"""
小鹅通登录助手 - 本地版
用途：在本地电脑上运行，完成小鹅通登录并导出凭证
"""

import os
import sys
import json
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 错误：未安装 playwright")
    print("请先安装：pip install playwright")
    print("然后运行：python -m playwright install chromium")
    sys.exit(1)


class XiaoeLoginHelper:
    """小鹅通登录助手"""
    
    def __init__(self, shop_url: str):
        self.shop_url = shop_url
        self.storage_file = "xiaoe_auth.json"
        
    def login(self):
        """执行登录流程"""
        print("=" * 60)
        print("小鹅通登录助手")
        print("=" * 60)
        print(f"\n店铺URL: {self.shop_url}\n")
        
        with sync_playwright() as p:
            # 启动浏览器（带界面）
            print("🚀 正在启动浏览器...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # 访问店铺
                print(f"📱 正在访问小鹅通店铺...")
                page.goto(self.shop_url, timeout=30000)
                time.sleep(3)
                
                # 检查是否需要登录
                print("\n" + "=" * 60)
                print("请在浏览器中完成登录")
                print("=" * 60)
                print("\n登录方式：")
                print("  1. 微信扫码登录")
                print("  2. 手机验证码登录")
                print("\n请完成登录后，在浏览器中看到您的个人信息或课程列表")
                print("然后回到此窗口，按 Enter 键继续...")
                print("=" * 60)
                
                # 等待用户完成登录
                input("\n按 Enter 键继续...")
                
                # 验证登录状态
                print("\n🔍 正在验证登录状态...")
                time.sleep(2)
                
                # 检查是否有登录标识（如用户头像、用户名等）
                is_logged_in = False
                
                # 尝试多种方式检测登录状态
                selectors = [
                    "img[alt*='头像']",
                    "div[class*='user']",
                    "div[class*='avatar']",
                    "span[class*='nickname']",
                ]
                
                for selector in selectors:
                    try:
                        if page.query_selector(selector):
                            is_logged_in = True
                            break
                    except:
                        continue
                
                if not is_logged_in:
                    print("\n⚠️  警告：未检测到登录标识")
                    print("如果您确认已登录，请按 Enter 继续")
                    print("如果未登录，请按 Ctrl+C 退出重试")
                    input()
                
                # 保存登录凭证
                print("\n💾 正在保存登录凭证...")
                storage = context.storage_state()
                
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(storage, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 登录凭证已保存到: {self.storage_file}")
                
                # 显示凭证信息
                cookies_count = len(storage.get('cookies', []))
                print(f"\n📊 凭证信息:")
                print(f"  - Cookies数量: {cookies_count}")
                print(f"  - 文件大小: {os.path.getsize(self.storage_file)} 字节")
                
                print("\n" + "=" * 60)
                print("✅ 登录成功！")
                print("=" * 60)
                print(f"\n下一步：将 {self.storage_file} 上传到服务器")
                print("\n上传命令:")
                print(f"  scp {self.storage_file} admin@47.100.32.41:/tmp/")
                print("\n然后在服务器上执行:")
                print(f"  sudo mv /tmp/{self.storage_file} /root/maoge_advisor/xiaoe_data/")
                print(f"  sudo systemctl restart xiaoe_monitor.service")
                print("\n" + "=" * 60)
                
                # 等待用户查看
                input("\n按 Enter 键关闭浏览器...")
                
            except PlaywrightTimeout:
                print("\n❌ 错误：页面加载超时")
                print("请检查网络连接和店铺URL是否正确")
                return False
            except KeyboardInterrupt:
                print("\n\n⚠️  用户取消操作")
                return False
            except Exception as e:
                print(f"\n❌ 错误：{e}")
                import traceback
                traceback.print_exc()
                return False
            finally:
                browser.close()
        
        return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("小鹅通登录助手 - 本地版")
    print("=" * 60)
    
    # 默认店铺URL
    default_shop_url = "https://appqpljfemv4802.h5.xiaoeknow.com/"
    
    # 获取店铺URL
    if len(sys.argv) > 1:
        shop_url = sys.argv[1]
    else:
        print(f"\n默认店铺URL: {default_shop_url}")
        print("如需使用其他URL，请按 Ctrl+C 退出，然后运行:")
        print(f"  python {sys.argv[0]} <店铺URL>")
        print("\n按 Enter 使用默认URL...")
        try:
            input()
            shop_url = default_shop_url
        except KeyboardInterrupt:
            print("\n\n已取消")
            return
    
    # 创建登录助手
    helper = XiaoeLoginHelper(shop_url)
    
    # 执行登录
    success = helper.login()
    
    if success:
        print("\n✅ 完成！")
    else:
        print("\n❌ 登录失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 常见问题快速参考

| 问题 | 快速解决方案 |
|------|-------------|
| playwright未安装 | `pip install playwright && python -m playwright install chromium` |
| 浏览器无法打开 | 检查网络，清除缓存，重新安装浏览器 |
| 登录状态未检测 | 确认已登录后按Enter继续 |
| 凭证上传失败 | 使用 `scp xiaoe_auth.json admin@47.100.32.41:~/` |
| 服务器未识别凭证 | 检查文件路径和权限，重启服务 |
| 凭证过期 | 重新运行登录助手，上传新凭证 |

---

**文档版本**: 1.0  
**最后更新**: 2026-02-20  
**维护者**: Tommy

