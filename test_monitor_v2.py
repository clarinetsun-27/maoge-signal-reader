#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小鹅通监控系统测试脚本 V2
使用正确的页面文本提取方法
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.insert(0, '/root/maoge_advisor')

# 导入图文处理器
from maoge_image_handler import MaogeImageHandler

class XiaoeMonitorTest:
    def __init__(self):
        self.QUANZI_URL = "https://quanzi.xiaoe-tech.com/c_6978813bd0343_9o1Xxs5A9981/feed_list?app_id=appitullny29099"
        self.AUTH_FILE = "/root/maoge_advisor/xiaoe_data/xiaoe_auth.json"
        self.LOGS_DIR = "/root/maoge_advisor/logs"
        
        # 初始化图文处理器
        logger.info("📸 初始化猫哥图文处理器...")
        self.image_handler = MaogeImageHandler()
        
    def run_test(self):
        """运行测试"""
        try:
            logger.info("="*60)
            logger.info("🚀 开始测试小鹅通监控系统")
            logger.info("="*60)
            
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                
                # 加载Cookie
                if not self.load_cookies(context):
                    logger.error("❌ Cookie加载失败")
                    browser.close()
                    return False
                
                # 创建页面
                page = context.new_page()
                
                # 访问圈子页面
                logger.info(f"🌐 访问圈子页面: {self.QUANZI_URL}")
                page.goto(self.QUANZI_URL, wait_until='domcontentloaded', timeout=60000)
                logger.info("✅ 页面加载完成，等待内容渲染...")
                time.sleep(5)
                
                # 滚动页面以触发动态内容加载
                logger.info("📜 滚动页面加载动态内容...")
                for i in range(3):
                    page.evaluate("window.scrollBy(0, 1000)")
                    time.sleep(2)
                    logger.info(f"✅ 已滚动 {(i+1)*1000}px")
                
                # 再等待一段时间确保内容加载
                logger.info("⏳ 等待动态内容加载...")
                time.sleep(5)
                
                # 检查是否在圈子页面
                current_url = page.url
                logger.info(f"✅ 已在圈子页面: {current_url}")
                
                # 获取整个页面的文本内容
                logger.info("📖 获取页面文本内容...")
                page_text = page.inner_text('body')
                
                # 保存调试信息
                self.save_debug_info(page, page_text)
                
                # 检查是否包含管理员内容
                if not self.check_admin_content(page_text):
                    logger.warning("⚠️ 未检测到管理员内容")
                    browser.close()
                    return False
                
                # 提取图片
                images = self.extract_images(page)
                if not images:
                    logger.warning("⚠️ 未找到图片")
                    browser.close()
                    return False
                
                logger.info(f"✅ 找到 {len(images)} 张图片")
                
                # 处理图片
                success = self.process_images(images)
                
                browser.close()
                
                if success:
                    logger.info("✅ 测试成功！")
                else:
                    logger.error("❌ 测试失败")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def load_cookies(self, context):
        """加载Cookie"""
        try:
            logger.info(f"🔐 已加载登录凭证文件: {self.AUTH_FILE}")
            
            with open(self.AUTH_FILE, 'r', encoding='utf-8') as f:
                auth_data = json.load(f)
            
            # 支持两种格式
            if 'cookies' in auth_data:
                cookies = auth_data['cookies']
            else:
                cookies = auth_data
            
            # 添加Cookie
            context.add_cookies(cookies)
            logger.info(f"✅ 已加载 {len(cookies)} 个Cookie")
            
            return True
            
        except Exception as e:
            logger.error(f"Cookie加载失败: {e}")
            return False
    
    def save_debug_info(self, page, page_text):
        """保存调试信息"""
        try:
            os.makedirs(self.LOGS_DIR, exist_ok=True)
            
            # 保存截图
            screenshot_path = f"{self.LOGS_DIR}/page_screenshot.png"
            page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"📸 已保存页面截图: {screenshot_path}")
            
            # 保存页面文本
            text_path = f"{self.LOGS_DIR}/page_text.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(page_text)
            logger.info(f"📝 已保存页面文本: {text_path}")
            
        except Exception as e:
            logger.warning(f"保存调试信息失败: {e}")
    
    def check_admin_content(self, page_text):
        """检查是否包含管理员内容"""
        logger.info("🔍 检查页面内容...")
        
        # 输出前500字符用于调试
        logger.info(f"📄 页面文本（前500字符）:\n{page_text[:500]}")
        
        # 检查管理员关键词
        admin_keywords = ['管理员', '丽姐_熊猫助理', '丽姐']
        for keyword in admin_keywords:
            if keyword in page_text:
                logger.info(f"✅ 检测到管理员内容！关键词: {keyword}")
                return True
        
        logger.warning("⚠️ 未检测到管理员内容")
        return False
    
    def extract_images(self, page):
        """提取页面中的所有图片URL"""
        logger.info("🖼️ 提取图片...")
        
        images = []
        try:
            # 查找所有img标签
            img_elements = page.locator('img').all()
            logger.info(f"📊 找到 {len(img_elements)} 个img元素")
            
            for img in img_elements:
                try:
                    src = img.get_attribute('src')
                    if src and ('http' in src or src.startswith('//')):
                        # 处理相对URL
                        if src.startswith('//'):
                            src = 'https:' + src
                        
                        # 过滤掉小图标和广告图片
                        if any(x in src.lower() for x in ['icon', 'logo', 'avatar', 'qrcode']):
                            continue
                        
                        images.append(src)
                        logger.info(f"📷 找到图片: {src[:100]}...")
                        
                except Exception as e:
                    continue
            
            logger.info(f"✅ 共提取 {len(images)} 张有效图片")
            return images
            
        except Exception as e:
            logger.error(f"提取图片失败: {e}")
            return []
    
    def process_images(self, image_urls):
        """处理图片"""
        logger.info(f"🎨 开始处理 {len(image_urls)} 张图片...")
        
        success_count = 0
        
        for i, url in enumerate(image_urls, 1):
            try:
                logger.info(f"📥 下载图片 {i}/{len(image_urls)}: {url[:100]}...")
                
                # 下载图片
                local_path = self.download_image(url, i)
                if not local_path:
                    logger.warning(f"⚠️ 图片 {i} 下载失败")
                    continue
                
                logger.info(f"✅ 图片已下载: {local_path}")
                
                # 分析图片
                logger.info(f"🔍 分析图片 {i}...")
                result = self.image_handler.process_image(local_path, source='xiaoe_test')
                
                if result and result.get('success'):
                    logger.info(f"✅ 图片 {i} 分析成功！")
                    logger.info(f"📊 预测结果: {result.get('prediction', {})}")
                    success_count += 1
                else:
                    logger.warning(f"⚠️ 图片 {i} 分析失败: {result.get('error', '未知错误')}")
                
            except Exception as e:
                logger.error(f"❌ 处理图片 {i} 时出错: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"📊 处理完成: {success_count}/{len(image_urls)} 张图片成功")
        return success_count > 0
    
    def download_image(self, url, index):
        """下载图片到本地"""
        try:
            # 创建下载目录
            download_dir = f"{self.LOGS_DIR}/images"
            os.makedirs(download_dir, exist_ok=True)
            
            # 下载图片
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存图片
            ext = 'png' if 'png' in url.lower() else 'jpg'
            local_path = f"{download_dir}/image_{index}.{ext}"
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return local_path
            
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("🧪 开始测试小鹅通监控系统")
    logger.info("="*60)
    
    test = XiaoeMonitorTest()
    success = test.run_test()
    
    if success:
        logger.info("="*60)
        logger.info("✅ 测试成功！")
        logger.info("="*60)
    else:
        logger.error("="*60)
        logger.error("❌ 测试失败")
        logger.error("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
