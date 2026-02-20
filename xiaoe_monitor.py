#!/usr/bin/env python3
"""
小鹅通内容自动监控系统
功能：
1. 自动登录小鹅通
2. 监控猫哥发布的图文和视频
3. 自动下载新内容
4. 触发图文解读分析
5. 推送结果到企业微信
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
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
        logging.FileHandler('/root/maoge_advisor/logs/xiaoe_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XiaoeMonitor:
    """小鹅通内容监控器"""
    
    def __init__(self, shop_url, phone=None, check_interval=3600):
        """
        初始化监控器
        
        Args:
            shop_url: 小鹅通店铺URL
            phone: 登录手机号（可选，首次需要）
            check_interval: 检查间隔（秒），默认3600（1小时）
        """
        self.shop_url = shop_url
        self.phone = phone
        self.check_interval = check_interval
        
        # 数据目录
        self.data_dir = Path("/root/maoge_advisor/xiaoe_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 图片保存目录
        self.image_dir = Path("/root/maoge_advisor/maoge_images")
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态文件
        self.state_file = self.data_dir / "monitor_state.json"
        self.content_db = self.data_dir / "content_history.json"
        
        # 加载历史记录
        self.content_history = self._load_content_history()
        
        # 图文处理器
        self.image_handler = MaogeImageHandler()
        
        logger.info(f"小鹅通监控器初始化完成: {shop_url}")
    
    def _load_content_history(self):
        """加载内容历史记录"""
        if self.content_db.exists():
            try:
                with open(self.content_db, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载内容历史失败: {e}")
                return {"images": {}, "videos": {}}
        return {"images": {}, "videos": {}}
    
    def _save_content_history(self):
        """保存内容历史记录"""
        try:
            with open(self.content_db, 'w', encoding='utf-8') as f:
                json.dump(self.content_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存内容历史失败: {e}")
    
    def login(self, page):
        """
        登录小鹅通
        
        Args:
            page: Playwright页面对象
        """
        try:
            logger.info("开始登录小鹅通...")
            
            # 访问店铺首页
            page.goto(self.shop_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # 检查是否已登录
            if self._is_logged_in(page):
                logger.info("已登录，跳过登录流程")
                return True
            
            # 查找登录按钮
            try:
                login_btn = page.locator("text=登录").first
                if login_btn.is_visible():
                    login_btn.click()
                    time.sleep(2)
            except:
                logger.info("未找到登录按钮，可能已在登录页面")
            
            # 等待手动登录（使用微信扫码或手机号验证码）
            logger.info("=" * 50)
            logger.info("请在浏览器中完成登录（微信扫码或手机验证码）")
            logger.info("等待登录完成...")
            logger.info("=" * 50)
            
            # 等待登录成功（最多5分钟）
            max_wait = 300  # 5分钟
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                if self._is_logged_in(page):
                    logger.info("✅ 登录成功！")
                    
                    # 保存登录状态
                    storage_state = page.context.storage_state()
                    state_file = self.data_dir / "login_state.json"
                    with open(state_file, 'w', encoding='utf-8') as f:
                        json.dump(storage_state, f)
                    
                    return True
                
                time.sleep(2)
            
            logger.error("登录超时")
            return False
            
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False
    
    def _is_logged_in(self, page):
        """检查是否已登录"""
        try:
            # 检查页面是否有用户信息或"我的"等元素
            # 这里需要根据实际页面结构调整
            user_indicators = [
                "text=我的",
                "text=个人中心",
                "[class*='user']",
                "[class*='avatar']"
            ]
            
            for indicator in user_indicators:
                try:
                    if page.locator(indicator).first.is_visible(timeout=2000):
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def get_latest_content(self, page):
        """
        获取最新发布的内容
        
        Returns:
            dict: {"images": [...], "videos": [...]}
        """
        try:
            logger.info("检查最新内容...")
            
            new_content = {"images": [], "videos": []}
            
            # 访问课程列表页面
            # 注意：这里需要根据实际的店铺结构调整URL
            page.goto(f"{self.shop_url}/course_list", wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # 获取所有课程项
            courses = page.locator("[class*='course-item']").all()
            
            for course in courses[:10]:  # 只检查最新的10个
                try:
                    # 提取课程信息
                    title = course.locator("[class*='title']").text_content()
                    
                    # 提取发布时间
                    time_text = course.locator("[class*='time']").text_content()
                    
                    # 检查是否是今天发布的
                    if self._is_today(time_text):
                        # 提取课程链接
                        link = course.locator("a").first.get_attribute("href")
                        
                        # 判断内容类型
                        if "图文" in title or "article" in link:
                            content_id = self._extract_content_id(link)
                            if content_id not in self.content_history["images"]:
                                new_content["images"].append({
                                    "id": content_id,
                                    "title": title,
                                    "link": link,
                                    "time": time_text
                                })
                        elif "视频" in title or "video" in link:
                            content_id = self._extract_content_id(link)
                            if content_id not in self.content_history["videos"]:
                                new_content["videos"].append({
                                    "id": content_id,
                                    "title": title,
                                    "link": link,
                                    "time": time_text
                                })
                except Exception as e:
                    logger.error(f"解析课程项失败: {e}")
                    continue
            
            logger.info(f"发现新图文: {len(new_content['images'])}个, 新视频: {len(new_content['videos'])}个")
            return new_content
            
        except Exception as e:
            logger.error(f"获取最新内容失败: {e}")
            return {"images": [], "videos": []}
    
    def _is_today(self, time_text):
        """判断是否是今天发布的"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return today in time_text or "今天" in time_text or "小时前" in time_text
        except:
            return False
    
    def _extract_content_id(self, link):
        """从链接中提取内容ID"""
        try:
            # 从URL中提取ID
            import re
            match = re.search(r'/(\w+)$', link)
            if match:
                return match.group(1)
            return link
        except:
            return link
    
    def download_image_content(self, page, content_info):
        """
        下载图文内容
        
        Args:
            page: Playwright页面对象
            content_info: 内容信息字典
        """
        try:
            logger.info(f"下载图文: {content_info['title']}")
            
            # 访问图文页面
            full_url = content_info['link']
            if not full_url.startswith('http'):
                full_url = self.shop_url.rstrip('/') + '/' + content_info['link'].lstrip('/')
            
            page.goto(full_url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # 截图保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"maoge_{timestamp}_{content_info['id']}.png"
            filepath = self.image_dir / filename
            
            # 截取主要内容区域
            try:
                content_area = page.locator("[class*='content']").first
                content_area.screenshot(path=str(filepath))
            except:
                # 如果找不到内容区域，截取整个页面
                page.screenshot(path=str(filepath), full_page=True)
            
            logger.info(f"✅ 图文已保存: {filepath}")
            
            # 记录到历史
            self.content_history["images"][content_info['id']] = {
                "title": content_info['title'],
                "time": content_info['time'],
                "file": str(filepath),
                "downloaded_at": datetime.now().isoformat()
            }
            self._save_content_history()
            
            # 触发图文解读
            self._trigger_analysis(filepath)
            
            return filepath
            
        except Exception as e:
            logger.error(f"下载图文失败: {e}")
            return None
    
    def _trigger_analysis(self, image_path):
        """触发图文解读分析"""
        try:
            logger.info(f"开始分析图文: {image_path}")
            
            # 调用图文处理器
            result = self.image_handler.process_image(str(image_path))
            
            if result:
                logger.info(f"✅ 分析完成，已推送到企业微信")
            else:
                logger.error("分析失败")
                
        except Exception as e:
            logger.error(f"触发分析失败: {e}")
    
    def record_video(self, content_info):
        """
        记录视频信息（不下载视频文件）
        
        Args:
            content_info: 视频信息字典
        """
        try:
            logger.info(f"记录视频: {content_info['title']}")
            
            # 记录到历史
            self.content_history["videos"][content_info['id']] = {
                "title": content_info['title'],
                "time": content_info['time'],
                "link": content_info['link'],
                "recorded_at": datetime.now().isoformat()
            }
            self._save_content_history()
            
            logger.info(f"✅ 视频已记录")
            
        except Exception as e:
            logger.error(f"记录视频失败: {e}")
    
    def monitor_loop(self, headless=True):
        """
        监控循环
        
        Args:
            headless: 是否无头模式
        """
        logger.info("=" * 60)
        logger.info("🚀 小鹅通内容监控系统启动")
        logger.info(f"店铺URL: {self.shop_url}")
        logger.info(f"检查间隔: {self.check_interval}秒 ({self.check_interval/3600}小时)")
        logger.info("=" * 60)
        
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=headless)
            
            # 尝试加载登录状态
            state_file = self.data_dir / "login_state.json"
            if state_file.exists():
                try:
                    context = browser.new_context(storage_state=str(state_file))
                    logger.info("已加载登录状态")
                except:
                    context = browser.new_context()
            else:
                context = browser.new_context()
            
            page = context.new_page()
            
            # 登录
            if not self.login(page):
                logger.error("登录失败，退出监控")
                browser.close()
                return
            
            # 监控循环
            check_count = 0
            while True:
                try:
                    check_count += 1
                    logger.info(f"\n{'='*60}")
                    logger.info(f"第 {check_count} 次检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"{'='*60}")
                    
                    # 获取最新内容
                    new_content = self.get_latest_content(page)
                    
                    # 处理新图文
                    for image_content in new_content["images"]:
                        self.download_image_content(page, image_content)
                        time.sleep(5)  # 避免请求过快
                    
                    # 记录新视频
                    for video_content in new_content["videos"]:
                        self.record_video(video_content)
                    
                    # 等待下次检查
                    logger.info(f"\n下次检查时间: {(datetime.now() + timedelta(seconds=self.check_interval)).strftime('%Y-%m-%d %H:%M:%S')}")
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    logger.info("\n收到停止信号，退出监控")
                    break
                except Exception as e:
                    logger.error(f"监控循环出错: {e}")
                    logger.info(f"等待 {self.check_interval} 秒后重试...")
                    time.sleep(self.check_interval)
            
            browser.close()
            logger.info("监控系统已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='小鹅通内容自动监控系统')
    parser.add_argument('--shop-url', required=True, help='小鹅通店铺URL')
    parser.add_argument('--phone', help='登录手机号（首次登录需要）')
    parser.add_argument('--interval', type=int, default=3600, help='检查间隔（秒），默认3600')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = XiaoeMonitor(
        shop_url=args.shop_url,
        phone=args.phone,
        check_interval=args.interval
    )
    
    # 启动监控
    monitor.monitor_loop(headless=args.headless)


if __name__ == "__main__":
    main()
