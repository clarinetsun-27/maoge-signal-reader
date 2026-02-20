#!/usr/bin/env python3
"""
Cookie 转换工具
将浏览器导出的 Cookie 转换为 Playwright 格式
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

def convert_editthiscookie_format(cookies: List[Dict]) -> Dict[str, Any]:
    """
    转换 EditThisCookie 格式到 Playwright 格式
    """
    playwright_cookies = []
    
    for cookie in cookies:
        playwright_cookie = {
            "name": cookie.get("name", ""),
            "value": cookie.get("value", ""),
            "domain": cookie.get("domain", ""),
            "path": cookie.get("path", "/"),
            "httpOnly": cookie.get("httpOnly", False),
            "secure": cookie.get("secure", False),
        }
        
        # 处理过期时间
        if "expirationDate" in cookie:
            playwright_cookie["expires"] = int(cookie["expirationDate"])
        elif "expires" in cookie:
            playwright_cookie["expires"] = int(cookie["expires"])
        
        # 处理 sameSite
        same_site = cookie.get("sameSite", "Lax")
        if same_site == "no_restriction":
            playwright_cookie["sameSite"] = "None"
        elif same_site == "lax":
            playwright_cookie["sameSite"] = "Lax"
        elif same_site == "strict":
            playwright_cookie["sameSite"] = "Strict"
        else:
            playwright_cookie["sameSite"] = same_site.capitalize() if same_site else "Lax"
        
        playwright_cookies.append(playwright_cookie)
    
    return {
        "cookies": playwright_cookies,
        "origins": []
    }

def convert_chrome_devtools_format(cookies: List[Dict]) -> Dict[str, Any]:
    """
    转换 Chrome DevTools 格式到 Playwright 格式
    """
    return convert_editthiscookie_format(cookies)

def convert_simple_format(cookies: List[Dict]) -> Dict[str, Any]:
    """
    转换简单的 name-value 格式到 Playwright 格式
    """
    playwright_cookies = []
    
    for cookie in cookies:
        playwright_cookie = {
            "name": cookie.get("name", ""),
            "value": cookie.get("value", ""),
            "domain": cookie.get("domain", ".xiaoeknow.com"),
            "path": cookie.get("path", "/"),
            "httpOnly": cookie.get("httpOnly", False),
            "secure": cookie.get("secure", True),
            "sameSite": cookie.get("sameSite", "Lax")
        }
        
        if "expires" in cookie:
            playwright_cookie["expires"] = int(cookie["expires"])
        
        playwright_cookies.append(playwright_cookie)
    
    return {
        "cookies": playwright_cookies,
        "origins": []
    }

def detect_format(cookies: Any) -> str:
    """
    检测 Cookie 格式
    """
    if not isinstance(cookies, list) or len(cookies) == 0:
        return "unknown"
    
    first_cookie = cookies[0]
    
    # EditThisCookie 格式特征
    if "storeId" in first_cookie or "expirationDate" in first_cookie:
        return "editthiscookie"
    
    # Chrome DevTools 格式
    if "domain" in first_cookie and "name" in first_cookie:
        return "chrome_devtools"
    
    # 简单格式
    if "name" in first_cookie and "value" in first_cookie:
        return "simple"
    
    return "unknown"

def validate_cookies(playwright_format: Dict[str, Any]) -> bool:
    """
    验证转换后的 Cookie 格式
    """
    if not isinstance(playwright_format, dict):
        print("❌ 错误: 不是有效的字典格式")
        return False
    
    if "cookies" not in playwright_format:
        print("❌ 错误: 缺少 'cookies' 字段")
        return False
    
    cookies = playwright_format["cookies"]
    if not isinstance(cookies, list):
        print("❌ 错误: 'cookies' 不是列表")
        return False
    
    if len(cookies) == 0:
        print("❌ 警告: Cookie 列表为空")
        return False
    
    # 检查必需字段
    required_fields = ["name", "value", "domain", "path"]
    for i, cookie in enumerate(cookies):
        for field in required_fields:
            if field not in cookie:
                print(f"❌ 错误: Cookie #{i+1} 缺少必需字段 '{field}'")
                return False
        
        # 检查域名
        domain = cookie.get("domain", "")
        if "xiaoeknow" not in domain and "xet.citv.cn" not in domain:
            print(f"⚠️  警告: Cookie #{i+1} 的域名可能不正确: {domain}")
    
    print(f"✅ 验证通过: {len(cookies)} 个 Cookies")
    return True

def print_cookie_info(playwright_format: Dict[str, Any]):
    """
    打印 Cookie 信息
    """
    cookies = playwright_format.get("cookies", [])
    
    print("\n" + "=" * 60)
    print("📊 Cookie 信息统计")
    print("=" * 60)
    print(f"Cookie 数量: {len(cookies)}")
    
    # 统计域名
    domains = {}
    for cookie in cookies:
        domain = cookie.get("domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1
    
    print(f"\n域名分布:")
    for domain, count in domains.items():
        print(f"  - {domain}: {count} 个")
    
    # 检查关键 Cookie
    important_cookies = ["session_id", "token", "auth", "user_id", "xe_token"]
    found_important = []
    
    for cookie in cookies:
        name = cookie.get("name", "")
        for important in important_cookies:
            if important.lower() in name.lower():
                found_important.append(name)
    
    if found_important:
        print(f"\n关键 Cookie:")
        for name in found_important:
            print(f"  ✅ {name}")
    else:
        print(f"\n⚠️  未找到明显的认证相关 Cookie")
    
    # 检查过期时间
    now = datetime.now().timestamp()
    expired_count = 0
    valid_count = 0
    
    for cookie in cookies:
        if "expires" in cookie:
            if cookie["expires"] < now:
                expired_count += 1
            else:
                valid_count += 1
    
    print(f"\n过期状态:")
    print(f"  - 有效: {valid_count} 个")
    print(f"  - 已过期: {expired_count} 个")
    print(f"  - 会话级: {len(cookies) - valid_count - expired_count} 个")
    
    print("=" * 60 + "\n")

def main():
    """
    主函数
    """
    print("=" * 60)
    print("🍪 Cookie 转换工具")
    print("=" * 60)
    print()
    
    # 检查参数
    if len(sys.argv) < 2:
        print("用法: python cookie_converter.py <cookies_file> [--verify]")
        print()
        print("示例:")
        print("  python cookie_converter.py cookies_export.json")
        print("  python cookie_converter.py cookies_export.json --verify")
        print()
        sys.exit(1)
    
    input_file = sys.argv[1]
    verify_only = "--verify" in sys.argv
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误: 文件不存在: {input_file}")
        sys.exit(1)
    
    # 读取文件
    print(f"📂 读取文件: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # 尝试解析 JSON
            try:
                cookies = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析错误: {e}")
                print("\n尝试修复常见问题...")
                
                # 尝试移除 BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                    cookies = json.loads(content)
                else:
                    raise
    
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        sys.exit(1)
    
    print(f"✅ 成功读取 {len(cookies) if isinstance(cookies, list) else '?'} 条数据")
    
    # 检测格式
    format_type = detect_format(cookies)
    print(f"🔍 检测到格式: {format_type}")
    
    # 转换格式
    print("🔄 转换格式...")
    
    if format_type == "editthiscookie":
        playwright_format = convert_editthiscookie_format(cookies)
    elif format_type == "chrome_devtools":
        playwright_format = convert_chrome_devtools_format(cookies)
    elif format_type == "simple":
        playwright_format = convert_simple_format(cookies)
    else:
        print("❌ 错误: 无法识别的 Cookie 格式")
        print("\n支持的格式:")
        print("  - EditThisCookie 扩展导出")
        print("  - Cookie-Editor 扩展导出")
        print("  - Chrome DevTools 导出")
        print("\n请参考 BROWSER_COOKIE_EXPORT_GUIDE.md 获取详细说明")
        sys.exit(1)
    
    print("✅ 格式转换完成")
    
    # 验证
    print("\n🔍 验证 Cookie...")
    if not validate_cookies(playwright_format):
        print("\n❌ Cookie 验证失败，但仍会保存文件")
        print("请检查导出的 Cookie 是否正确")
    
    # 打印信息
    print_cookie_info(playwright_format)
    
    # 如果只是验证，到此结束
    if verify_only:
        print("✅ 验证完成")
        sys.exit(0)
    
    # 保存文件
    output_file = "xiaoe_auth.json"
    print(f"💾 保存到: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(playwright_format, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(output_file)
        print(f"✅ 保存成功 ({file_size} 字节)")
    
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        sys.exit(1)
    
    # 打印后续步骤
    print("\n" + "=" * 60)
    print("✅ 转换完成！")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 上传到服务器:")
    print("     scp xiaoe_auth.json root@47.100.32.41:/root/maoge_advisor/xiaoe_data/")
    print()
    print("  2. 在服务器上激活:")
    print("     ssh root@47.100.32.41")
    print("     chmod 600 /root/maoge_advisor/xiaoe_data/xiaoe_auth.json")
    print("     systemctl restart xiaoe_monitor.service")
    print()
    print("  3. 验证:")
    print("     tail -f /root/maoge_advisor/logs/xiaoe_monitor.log")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
