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
                print(f"  sudo mv /tmp/{self.storage_file} /root/maoge_advisor/")
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
