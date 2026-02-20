#!/usr/bin/env python3
"""
小鹅通监控系统集成测试
"""

import os
import sys
import json
from pathlib import Path

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("测试1: 模块导入...")
    try:
        from xiaoe_monitor import XiaoeMonitor
        print("✅ xiaoe_monitor 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_directories():
    """测试目录结构"""
    print("\n测试2: 目录结构...")
    
    required_dirs = [
        "/root/maoge_advisor",
        "/root/maoge_advisor/modules",
        "/root/maoge_advisor/maoge_images",
        "/root/maoge_advisor/logs"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path} 存在")
        else:
            print(f"❌ {dir_path} 不存在")
            all_ok = False
    
    return all_ok

def test_dependencies():
    """测试依赖包"""
    print("\n测试3: 依赖包...")
    
    required_packages = [
        "playwright",
        "requests",
        "openai"
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_ok = False
    
    return all_ok

def test_monitor_creation():
    """测试监控器创建"""
    print("\n测试4: 监控器创建...")
    try:
        from xiaoe_monitor import XiaoeMonitor
        
        monitor = XiaoeMonitor(
            shop_url="https://test.xiaoeknow.com/",
            check_interval=3600
        )
        
        print("✅ 监控器创建成功")
        print(f"   - 店铺URL: {monitor.shop_url}")
        print(f"   - 检查间隔: {monitor.check_interval}秒")
        print(f"   - 数据目录: {monitor.data_dir}")
        print(f"   - 图片目录: {monitor.image_dir}")
        
        return True
    except Exception as e:
        print(f"❌ 监控器创建失败: {e}")
        return False

def test_content_history():
    """测试内容历史记录"""
    print("\n测试5: 内容历史记录...")
    try:
        from xiaoe_monitor import XiaoeMonitor
        
        monitor = XiaoeMonitor(
            shop_url="https://test.xiaoeknow.com/",
            check_interval=3600
        )
        
        # 测试保存
        monitor.content_history["images"]["test_id"] = {
            "title": "测试图文",
            "time": "2026-02-17",
            "file": "/test/path.png"
        }
        monitor._save_content_history()
        
        # 测试加载
        loaded_history = monitor._load_content_history()
        
        if "test_id" in loaded_history["images"]:
            print("✅ 内容历史记录读写正常")
            return True
        else:
            print("❌ 内容历史记录读写失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_playwright():
    """测试Playwright"""
    print("\n测试6: Playwright浏览器...")
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.baidu.com")
            title = page.title()
            browser.close()
            
            if "百度" in title:
                print(f"✅ Playwright工作正常 (页面标题: {title})")
                return True
            else:
                print(f"❌ Playwright异常 (页面标题: {title})")
                return False
                
    except Exception as e:
        print(f"❌ Playwright测试失败: {e}")
        print("   提示: 运行 'playwright install chromium' 安装浏览器")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("小鹅通监控系统集成测试")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_directories,
        test_dependencies,
        test_monitor_creation,
        test_content_history,
        test_playwright
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有测试通过！系统已准备就绪。")
        return 0
    else:
        print(f"\n❌ {total - passed} 个测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
