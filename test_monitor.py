#!/usr/bin/env python3
"""
小鹅通监控系统测试脚本
用于测试是否能检测到02-13 15:10猫哥发布的内容
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))

from maoge_image_handler import MaogeImageHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/maoge_advisor/logs/test_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XiaoeMonitorTest:
    """小鹅通内容监控器测试版"""
    
    QUANZI_URL = "https://quanzi.xiaoe-tech.com/c_6978813bd0343_9o1Xxs5A9981/feed_list"
    
    def __init__(self):
        self.data_dir = Path("/root/maoge_advisor/xiaoe_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.auth_file = self.data_dir / "xiaoe_auth.json"
        self.state_file = self.data_dir / "monitor_state.json"
        self.image_handler = MaogeImageHandler()
        
    def load_auth(self, context):
        """加载登录凭证"""
        if self.auth_file.exists():
            logger.info(f"🔐 已加载登录凭证文件: {self.auth_file.name}")
            with open(self.auth_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 支持两种格式：直接数组或包含cookies键的对象
                if isinstance(data, dict) and 'cookies' in data:
                    cookies = data['cookies']
                elif isinstance(data, list):
                    cookies = data
                else:
                    logger.error("❌ Cookie文件格式不正确")
                    return False
                
                context.add_cookies(cookies)
                logger.info(f"✅ 已加载 {len(cookies)} 个Cookie")
                return True
        else:
            logger.warning(f"⚠️ 未找到登录凭证文件: {self.auth_file}")
            return False
    
    def _is_logged_in(self, page):
        """检查是否已登录"""
        try:
            current_url = page.url
            if 'login' in current_url.lower():
                logger.info("⚠️ 当前在登录页面，未登录")
                return False
            
            if 'quanzi.xiaoe-tech.com' in current_url:
                logger.info(f"✅ 已在圈子页面: {current_url}")
                
                user_indicators = [
                    "text=发布",
                    "text=我的",
                    "text=个人中心",
                    "text=关注",
                    "text=消息",
                    "[class*='user']",
                    "[class*='avatar']",
                    "[class*='profile']"
                ]
                
                for indicator in user_indicators:
                    try:
                        element = page.locator(indicator).first
                        if element.is_visible(timeout=2000):
                            logger.info(f"✅ 检测到登录标识: {indicator}")
                            return True
                    except:
                        continue
                
                logger.info("✅ Cookie已加载且在圈子页面，假定已登录")
                return True
            
            logger.info(f"⚠️ 不在圈子页面: {current_url}")
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def get_latest_content(self, page):
        """获取圈子最新发布的内容"""
        try:
            logger.info("📊 检查圈子最新内容...")
            
            # 等待内容加载
            time.sleep(3)
            
            # 查找所有动态卡片
            content_items = page.locator('[class*="feed"], [class*="post"], [class*="item"]').all()
            logger.info(f"找到 {len(content_items)} 个内容项")
            
            # 尝试获取第一个内容的信息
            if len(content_items) > 0:
                first_item = content_items[0]
                
                # 获取作者信息
                author_elements = first_item.locator('[class*="author"], [class*="user"], [class*="name"]').all()
                author_name = None
                for elem in author_elements:
                    try:
                        text = elem.inner_text(timeout=1000)
                        if text and len(text) < 20:
                            author_name = text
                            break
                    except:
                        continue
                
                # 获取时间信息
                time_elements = first_item.locator('[class*="time"], [class*="date"]').all()
                publish_time = None
                for elem in time_elements:
                    try:
                        text = elem.inner_text(timeout=1000)
                        if text:
                            publish_time = text
                            break
                    except:
                        continue
                
                # 获取内容文本
                content_text = None
                try:
                    content_text = first_item.inner_text(timeout=2000)
                except:
                    pass
                
                # 查找图片
                images = first_item.locator('img').all()
                image_urls = []
                for img in images:
                    try:
                        src = img.get_attribute('src')
                        if src and ('http' in src or src.startswith('//')):
                            if src.startswith('//'):
                                src = 'https:' + src
                            image_urls.append(src)
                    except:
                        continue
                
                content_info = {
                    'author': author_name or '未知',
                    'time': publish_time or '未知',
                    'text': content_text[:200] if content_text else '无文本',
                    'images': image_urls,
                    'image_count': len(image_urls)
                }
                
                logger.info(f"📝 最新内容信息:")
                logger.info(f"   作者: {content_info['author']}")
                logger.info(f"   时间: {content_info['time']}")
                logger.info(f"   图片数量: {content_info['image_count']}")
                logger.info(f"   文本预览: {content_info['text'][:100]}...")
                
                return content_info
            else:
                logger.warning("⚠️ 未找到任何内容项")
                return None
                
        except Exception as e:
            logger.error(f"获取最新内容失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def check_if_maoge_content(self, content_info):
        """检查是否是猫哥的内容"""
        if not content_info:
            return False
        
        author = content_info.get('author', '').lower()
        
        # 检查作者名称
        maoge_keywords = ['猫哥', 'maoge', '猫', '哥']
        for keyword in maoge_keywords:
            if keyword in author:
                logger.info(f"✅ 检测到猫哥内容！作者: {content_info['author']}")
                return True
        
        logger.info(f"⚠️ 不是猫哥的内容，作者: {content_info['author']}")
        return False
    
    def process_content(self, content_info):
        """处理检测到的内容"""
        try:
            logger.info("🔄 开始处理内容...")
            
            # 检查是否有图片
            if content_info['image_count'] == 0:
                logger.info("⚠️ 内容中没有图片，跳过处理")
                return False
            
            # 下载并分析图片
            logger.info(f"📥 准备下载 {content_info['image_count']} 张图片...")
            
            for idx, image_url in enumerate(content_info['images']):
                logger.info(f"📥 下载图片 {idx+1}/{content_info['image_count']}: {image_url}")
                
                # 使用图片处理器分析
                result = self.image_handler.process_image_url(image_url)
                
                if result:
                    logger.info(f"✅ 图片 {idx+1} 分析完成")
                    logger.info(f"   信号: {result.get('signal', '未知')}")
                    logger.info(f"   置信度: {result.get('confidence', '未知')}")
                else:
                    logger.warning(f"⚠️ 图片 {idx+1} 分析失败")
            
            return True
            
        except Exception as e:
            logger.error(f"处理内容失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def run_test(self):
        """运行测试"""
        logger.info("=" * 60)
        logger.info("🧪 开始测试小鹅通监控系统")
        logger.info("=" * 60)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # 加载登录凭证
            if not self.load_auth(context):
                logger.error("❌ 无法加载登录凭证，测试终止")
                browser.close()
                return False
            
            page = context.new_page()
            
            try:
                # 访问圈子页面
                logger.info(f"🌐 访问圈子页面: {self.QUANZI_URL}")
                # 使用domcontentloaded更快，增加超时时间
                page.goto(self.QUANZI_URL, wait_until='domcontentloaded', timeout=60000)
                logger.info("✅ 页面加载完成，等待内容渲染...")
                time.sleep(5)  # 等待JavaScript渲染
                
                # 检查登录状态
                if not self._is_logged_in(page):
                    logger.error("❌ 登录状态检查失败")
                    browser.close()
                    return False
                
                # 获取最新内容
                content_info = self.get_latest_content(page)
                
                if not content_info:
                    logger.error("❌ 无法获取最新内容")
                    browser.close()
                    return False
                
                # 检查是否是猫哥的内容
                if not self.check_if_maoge_content(content_info):
                    logger.warning("⚠️ 最新内容不是猫哥发布的")
                    logger.info("💡 提示：可能需要手动检查页面或调整检测逻辑")
                    browser.close()
                    return False
                
                # 处理内容
                success = self.process_content(content_info)
                
                if success:
                    logger.info("✅ 测试完成！内容已成功处理")
                else:
                    logger.warning("⚠️ 内容处理过程中出现问题")
                
                browser.close()
                return success
                
            except Exception as e:
                logger.error(f"测试过程中出错: {e}")
                import traceback
                logger.error(traceback.format_exc())
                browser.close()
                return False


if __name__ == "__main__":
    tester = XiaoeMonitorTest()
    success = tester.run_test()
    
    if success:
        logger.info("🎉 测试成功！")
        sys.exit(0)
    else:
        logger.error("❌ 测试失败")
        sys.exit(1)
