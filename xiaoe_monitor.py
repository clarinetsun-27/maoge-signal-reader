#!/usr/bin/env python3
"""
小鹅通内容自动监控系统
功能：
1. 自动登录小鹅通圈子
2. 监控猫哥发布的图文和视频
3. 自动下载新内容
4. 触发图文解读分析
5. 推送结果到企业微信

修复说明：
- 将监控URL从H5店铺改为圈子地址
- 圈子URL: https://quanzi.xiaoe-tech.com/c_6978813bd0343_9o1Xxs5A9981/feed_list
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import chinese_calendar

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
    
    # 圈子URL常量
    QUANZI_URL = "https://quanzi.xiaoe-tech.com/c_6978813bd0343_9o1Xxs5A9981/feed_list"
    
    def __init__(self, phone=None, check_interval=180):
        """
        初始化监控器
        
        Args:
            phone: 登录手机号（可选，首次需要）
            check_interval: 检查间隔（秒），默认180（3分钟）
        """
        self.shop_url = self.QUANZI_URL  # 使用圈子URL
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
        
        # 交易时间配置
        self.trading_start = "09:30"  # 交易开始时间
        self.trading_end = "15:00"    # 交易结束时间
        
        logger.info(f"小鹅通监控器初始化完成")
        logger.info(f"圈子URL: {self.shop_url}")
        logger.info(f"交易时间: {self.trading_start} - {self.trading_end}")
        logger.info(f"检查间隔: {check_interval}秒 ({check_interval/60}分钟)")
    
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
        登录小鹅通圈子
        
        Args:
            page: Playwright页面对象
        """
        try:
            logger.info("开始登录小鹅通圈子...")
            
            # 检查是否有保存的登录凭证
            auth_file = self.data_dir / "xiaoe_auth.json"
            state_file = self.data_dir / "login_state.json"
            
            if auth_file.exists():
                logger.info(f"✅ 发现上传的登录凭证文件: xiaoe_auth.json")
            elif state_file.exists():
                logger.info(f"✅ 发现服务器端登录凭证文件: login_state.json")
            
            # 访问圈子页面
            logger.info(f"访问圈子页面: {self.shop_url}")
            page.goto(self.shop_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(3)
            
            # 检查是否已登录
            if self._is_logged_in(page):
                logger.info("✅ 已登录，跳过登录流程")
                return True
            
            logger.info("⚠️ 未检测到登录状态")
            
            # 查找登录按钮
            try:
                login_btn = page.locator("text=登录").first
                if login_btn.is_visible(timeout=5000):
                    logger.info("找到登录按钮，点击...")
                    login_btn.click()
                    time.sleep(2)
            except:
                logger.info("未找到登录按钮，可能已在登录页面")
            
            # 等待手动登录（使用微信扫码或手机号验证码）
            logger.info("=" * 50)
            logger.info("⚠️ 需要手动登录")
            logger.info("请在浏览器中完成登录（微信扫码或手机验证码）")
            logger.info("或者使用本地电脑导出Cookie并上传xiaoe_auth.json")
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
                    logger.info(f"✅ 登录状态已保存: {state_file}")
                    
                    return True
                
                time.sleep(2)
            
            logger.error("❌ 登录超时（5分钟）")
            logger.error("请使用本地电脑导出Cookie并上传xiaoe_auth.json")
            return False
            
        except Exception as e:
            logger.error(f"❌ 登录失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _is_logged_in(self, page):
        """检查是否已登录"""
        try:
            # 检查URL是否在登录页面
            current_url = page.url
            if 'login' in current_url.lower():
                logger.info("⚠️ 当前在登录页面，未登录")
                return False
            
            # 检查是否在圈子页面
            if 'quanzi.xiaoe-tech.com' in current_url:
                logger.info(f"✅ 已在圈子页面: {current_url}")
                
                # 尝试检测登录标识（但不强制要求）
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
                
                # 即使没有检测到明确标识，如果Cookie已加载且在圈子页面，也认为已登录
                logger.info("✅ Cookie已加载且在圈子页面，假定已登录")
                return True
            
            logger.info(f"⚠️ 不在圈子页面: {current_url}")
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def get_latest_content(self, page):
        """
        获取圈子最新发布的内容
        
        Returns:
            dict: {"images": [...], "videos": [...]}
        """
        try:
            logger.info("📊 检查圈子最新内容...")
            
            # 刷新页面获取最新内容
            page.reload(wait_until='domcontentloaded', timeout=30000)
            time.sleep(2)
            
            new_content = {"images": [], "videos": []}
            
            # 获取圈子动态列表
            # 注意：这里需要根据实际的圈子页面结构调整选择器
            try:
                # 等待内容加载
                page.wait_for_selector(".feed-item, .post-item, [class*='feed'], [class*='post']", timeout=10000)
                
                # 获取所有动态项
                feed_items = page.locator(".feed-item, .post-item, [class*='feed'], [class*='post']").all()
                
                logger.info(f"找到 {len(feed_items)} 个动态")
                
                for item in feed_items[:10]:  # 只检查最新的10条
                    try:
                        # 提取动态信息
                        content_info = self._extract_feed_info(item)
                        
                        if content_info:
                            content_id = content_info['id']
                            content_type = content_info['type']
                            
                            # 检查是否是新内容
                            if content_type == 'image' and content_id not in self.content_history['images']:
                                new_content['images'].append(content_info)
                                logger.info(f"🆕 发现新图文: {content_info['title']}")
                            elif content_type == 'video' and content_id not in self.content_history['videos']:
                                new_content['videos'].append(content_info)
                                logger.info(f"🆕 发现新视频: {content_info['title']}")
                    
                    except Exception as e:
                        logger.error(f"解析动态项失败: {e}")
                        continue
            
            except PlaywrightTimeout:
                logger.warning("⚠️ 等待内容加载超时")
            except Exception as e:
                logger.error(f"获取动态列表失败: {e}")
            
            return new_content
            
        except Exception as e:
            logger.error(f"获取最新内容失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"images": [], "videos": []}
    
    def _extract_feed_info(self, item):
        """从动态项中提取信息"""
        try:
            # 这里需要根据实际的圈子页面结构调整
            # 提取标题、链接、时间等信息
            
            title = ""
            link = ""
            content_id = ""
            content_type = "image"  # 默认为图文
            
            # 尝试提取标题
            try:
                title_elem = item.locator(".title, .feed-title, [class*='title']").first
                title = title_elem.inner_text().strip()
            except:
                title = "未知标题"
            
            # 尝试提取链接
            try:
                link_elem = item.locator("a").first
                link = link_elem.get_attribute("href")
            except:
                pass
            
            # 生成内容ID（使用标题+时间的hash）
            import hashlib
            content_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()
            
            # 判断内容类型
            item_html = item.inner_html().lower()
            if 'video' in item_html or '视频' in title:
                content_type = "video"
            
            return {
                'id': content_id,
                'title': title,
                'link': link,
                'type': content_type,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"提取动态信息失败: {e}")
            return None
    
    def download_content(self, page, content_info):
        """
        下载内容（图文或视频）
        
        Args:
            page: Playwright页面对象
            content_info: 内容信息字典
        """
        try:
            logger.info(f"📥 下载内容: {content_info['title']}")
            
            # 构建完整URL
            full_url = content_info['link']
            if not full_url.startswith('http'):
                # 圈子的链接可能是相对路径
                base_url = "https://quanzi.xiaoe-tech.com"
                full_url = base_url + full_url if full_url.startswith('/') else f"{base_url}/{full_url}"
            
            # 访问内容页面
            page.goto(full_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(2)
            
            if content_info['type'] == 'image':
                # 下载图文
                self._download_images(page, content_info)
            elif content_info['type'] == 'video':
                # 下载视频
                self._download_video(page, content_info)
            
            # 记录到历史
            history_key = 'images' if content_info['type'] == 'image' else 'videos'
            self.content_history[history_key][content_info['id']] = {
                'title': content_info['title'],
                'downloaded_at': datetime.now().isoformat()
            }
            self._save_content_history()
            
        except Exception as e:
            logger.error(f"下载内容失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _download_images(self, page, content_info):
        """下载图文中的图片"""
        try:
            logger.info("📷 下载图文图片...")
            
            # 等待图片加载
            time.sleep(2)
            
            # 查找所有图片
            images = page.locator("img").all()
            
            saved_images = []
            for idx, img in enumerate(images):
                try:
                    src = img.get_attribute("src")
                    if src and ('http' in src or src.startswith('//')):
                        # 确保URL完整
                        if src.startswith('//'):
                            src = 'https:' + src
                        
                        # 下载图片
                        import requests
                        response = requests.get(src, timeout=30)
                        
                        if response.status_code == 200:
                            # 保存图片
                            filename = f"{content_info['id']}_{idx}.jpg"
                            filepath = self.image_dir / filename
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            saved_images.append(str(filepath))
                            logger.info(f"✅ 图片已保存: {filename}")
                
                except Exception as e:
                    logger.error(f"下载图片失败: {e}")
                    continue
            
            if saved_images:
                logger.info(f"✅ 共下载 {len(saved_images)} 张图片")
                
                # 触发图文分析
                self._analyze_images(content_info, saved_images)
            else:
                logger.warning("⚠️ 未找到可下载的图片")
        
        except Exception as e:
            logger.error(f"下载图文失败: {e}")
    
    def _download_video(self, page, content_info):
        """下载视频"""
        try:
            logger.info("🎬 下载视频...")
            
            # 查找视频元素
            video = page.locator("video").first
            video_src = video.get_attribute("src")
            
            if video_src:
                logger.info(f"视频URL: {video_src}")
                # TODO: 实现视频下载逻辑
                logger.info("⚠️ 视频下载功能待实现")
            else:
                logger.warning("⚠️ 未找到视频源")
        
        except Exception as e:
            logger.error(f"下载视频失败: {e}")
    
    def _analyze_images(self, content_info, image_paths):
        """分析图文内容"""
        try:
            logger.info("🤖 开始分析图文...")
            
            # 调用图文处理器
            result = self.image_handler.process_images(
                image_paths=image_paths,
                title=content_info['title']
            )
            
            if result:
                logger.info("✅ 图文分析完成")
                logger.info(f"分析结果: {result}")
            else:
                logger.warning("⚠️ 图文分析未返回结果")
        
        except Exception as e:
            logger.error(f"分析图文失败: {e}")
    
    def is_trading_time(self):
        """检查是否在交易时间内"""
        now = datetime.now()
        
        # 检查是否是工作日
        if not chinese_calendar.is_workday(now.date()):
            return False
        
        # 检查时间范围
        current_time = now.strftime("%H:%M")
        return self.trading_start <= current_time <= self.trading_end
    
    def monitor_loop(self, headless=True):
        """
        主监控循环
        
        Args:
            headless: 是否使用无头模式
        """
        logger.info("=" * 60)
        logger.info("🚀 小鹅通圈子监控系统启动")
        logger.info(f"圈子URL: {self.shop_url}")
        logger.info(f"检查间隔: {self.check_interval}秒 ({self.check_interval/60}分钟)")
        logger.info("=" * 60)
        
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=headless)
            
            # 创建浏览器上下文，加载登录状态
            context_options = {}
            
            # 优先使用上传的凭证文件
            auth_file = self.data_dir / "xiaoe_auth.json"
            state_file = self.data_dir / "login_state.json"
            
            if auth_file.exists():
                logger.info(f"✅ 已加载登录状态: xiaoe_auth.json")
                with open(auth_file, 'r', encoding='utf-8') as f:
                    context_options['storage_state'] = json.load(f)
            elif state_file.exists():
                logger.info(f"✅ 已加载登录状态: login_state.json")
                with open(state_file, 'r', encoding='utf-8') as f:
                    context_options['storage_state'] = json.load(f)
            
            context = browser.new_context(**context_options)
            page = context.new_page()
            
            # 登录
            if not self.login(page):
                logger.error("❌ 登录失败，监控系统无法启动")
                browser.close()
                return
            
            # 主循环
            while True:
                try:
                    # 检查是否在交易时间
                    if not self.is_trading_time():
                        now = datetime.now()
                        logger.info(f"⏸️  非交易时间，等待到 {self.trading_start}")
                        
                        # 计算下次检查时间
                        next_check = now.replace(
                            hour=int(self.trading_start.split(':')[0]),
                            minute=int(self.trading_start.split(':')[1]),
                            second=0
                        )
                        
                        if next_check <= now:
                            next_check += timedelta(days=1)
                        
                        wait_seconds = (next_check - now).total_seconds()
                        logger.info(f"下次检查时间: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        time.sleep(min(wait_seconds, 3600))  # 最多等待1小时
                        continue
                    
                    # 获取最新内容
                    new_content = self.get_latest_content(page)
                    
                    # 处理新图文
                    for content in new_content['images']:
                        self.download_content(page, content)
                    
                    # 处理新视频
                    for content in new_content['videos']:
                        self.download_content(page, content)
                    
                    # 等待下次检查
                    logger.info(f"⏰ 等待 {self.check_interval} 秒后进行下次检查...")
                    time.sleep(self.check_interval)
                
                except KeyboardInterrupt:
                    logger.info("收到停止信号，正在退出...")
                    break
                except Exception as e:
                    logger.error(f"监控循环出错: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    logger.info(f"等待 {self.check_interval} 秒后重试...")
                    time.sleep(self.check_interval)
            
            browser.close()
            logger.info("监控系统已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='小鹅通圈子内容自动监控系统')
    parser.add_argument('--phone', help='登录手机号（首次登录需要）')
    parser.add_argument('--interval', type=int, default=180, help='检查间隔（秒），默认180（3分钟）')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = XiaoeMonitor(
        phone=args.phone,
        check_interval=args.interval
    )
    
    # 启动监控
    monitor.monitor_loop(headless=args.headless)


if __name__ == "__main__":
    main()
