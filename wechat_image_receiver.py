#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信图文上传接口
接收用户通过企业微信上传的猫哥图文，自动分析并推送结果

实现方式：
1. 方式A：通过企业微信文件上传（需要企业微信应用配置）
2. 方式B：通过简单的HTTP服务接收图片（推荐）
3. 方式C：监控指定目录，自动处理新图片（最简单）

当前实现：方式C（目录监控）+ 方式B（HTTP服务）
"""

import os
import sys
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from maoge_image_handler import MaogeImageHandler, send_wechat_message, MaogeConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('wechat_image_receiver')


# ==================== 方式C：目录监控 ====================

class ImageDirectoryHandler(FileSystemEventHandler):
    """图片目录监控处理器"""
    
    def __init__(self, handler):
        """
        初始化
        
        Args:
            handler: MaogeImageHandler实例
        """
        self.handler = handler
        self.processed_files = set()
        
        # 加载已处理文件列表
        self._load_processed_files()
    
    def _load_processed_files(self):
        """加载已处理文件列表"""
        processed_file = os.path.join(
            os.path.dirname(MaogeConfig.DB_PATH),
            'processed_images.txt'
        )
        
        if os.path.exists(processed_file):
            with open(processed_file, 'r') as f:
                self.processed_files = set(line.strip() for line in f)
            logger.info(f"加载了{len(self.processed_files)}个已处理文件记录")
    
    def _save_processed_file(self, file_path):
        """保存已处理文件记录"""
        processed_file = os.path.join(
            os.path.dirname(MaogeConfig.DB_PATH),
            'processed_images.txt'
        )
        
        with open(processed_file, 'a') as f:
            f.write(file_path + '\n')
        
        self.processed_files.add(file_path)
    
    def _get_file_hash(self, file_path):
        """获取文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # 只处理图片文件
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            return
        
        # 等待文件写入完成
        time.sleep(2)
        
        # 检查是否已处理
        file_hash = self._get_file_hash(file_path)
        if file_hash and file_hash in self.processed_files:
            logger.info(f"文件已处理过，跳过: {file_path}")
            return
        
        logger.info(f"检测到新图片: {file_path}")
        
        try:
            # 处理图片
            result = self.handler.process_image(file_path, source='directory_monitor')
            
            if result['success']:
                # 发送分析结果
                send_wechat_message(result['message'])
                
                # 记录已处理
                if file_hash:
                    self._save_processed_file(file_hash)
                
                logger.info(f"图片处理成功: {file_path}")
            else:
                error_msg = f"⚠️ 图片处理失败\n\n文件: {os.path.basename(file_path)}\n错误: {result.get('error', '未知错误')}"
                send_wechat_message(error_msg)
                logger.error(f"图片处理失败: {file_path}, 错误: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"处理图片异常: {file_path}, {e}", exc_info=True)
            error_msg = f"⚠️ 图片处理异常\n\n文件: {os.path.basename(file_path)}\n异常: {str(e)}"
            send_wechat_message(error_msg)


def start_directory_monitor(watch_dir):
    """
    启动目录监控
    
    Args:
        watch_dir: 监控目录路径
    """
    # 确保目录存在
    Path(watch_dir).mkdir(parents=True, exist_ok=True)
    
    # 初始化处理器
    handler = MaogeImageHandler()
    
    # 创建监控器
    event_handler = ImageDirectoryHandler(handler)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    
    # 启动监控
    observer.start()
    logger.info(f"目录监控已启动: {watch_dir}")
    
    # 发送启动通知
    startup_msg = f"""📁 猫哥图文自动分析服务已启动

📂 监控目录: {watch_dir}
⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 使用方法:
1. 将猫哥图文保存到监控目录
2. 系统自动分析并推送结果
3. 猫哥发布笑脸后反馈实际结果

系统已准备就绪，等待图文上传..."""
    
    send_wechat_message(startup_msg)
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("目录监控已停止")
    
    observer.join()


# ==================== 方式B：HTTP服务 ====================

def start_http_server(port=8888):
    """
    启动HTTP服务接收图片上传
    
    Args:
        port: 服务端口
    """
    from flask import Flask, request, jsonify
    import werkzeug.utils
    
    app = Flask(__name__)
    handler = MaogeImageHandler()
    
    @app.route('/upload', methods=['POST'])
    def upload_image():
        """上传图片接口"""
        try:
            # 检查文件
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': '没有文件'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'success': False, 'error': '文件名为空'}), 400
            
            # 保存文件
            filename = werkzeug.utils.secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_filename = f"{timestamp}_{filename}"
            save_path = os.path.join(MaogeConfig.IMAGE_STORAGE_PATH, save_filename)
            
            file.save(save_path)
            logger.info(f"文件已保存: {save_path}")
            
            # 处理图片
            result = handler.process_image(save_path, source='http_upload')
            
            if result['success']:
                # 发送分析结果
                send_wechat_message(result['message'])
                
                return jsonify({
                    'success': True,
                    'prediction_id': result['prediction_id'],
                    'message': '分析完成，结果已推送到企业微信'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', '未知错误')
                }), 500
                
        except Exception as e:
            logger.error(f"上传处理异常: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/feedback', methods=['POST'])
    def feedback_smile():
        """笑脸反馈接口"""
        try:
            data = request.get_json()
            
            prediction_id = data.get('prediction_id')
            actual_smile = data.get('actual_smile')
            actual_count = data.get('actual_count')
            
            if not prediction_id or not actual_smile:
                return jsonify({'success': False, 'error': '缺少必要参数'}), 400
            
            # 保存反馈
            success = handler.save_feedback(prediction_id, actual_smile, actual_count)
            
            if success:
                # 发送反馈确认
                feedback_msg = f"""✅ 笑脸反馈已记录

📝 预测ID: {prediction_id}
{actual_smile} 实际笑脸: {actual_smile}
🔢 实际数量: {actual_count or '未指定'}

系统将根据反馈优化模型。"""
                
                send_wechat_message(feedback_msg)
                
                return jsonify({'success': True, 'message': '反馈已保存'})
            else:
                return jsonify({'success': False, 'error': '保存反馈失败'}), 500
                
        except Exception as e:
            logger.error(f"反馈处理异常: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/stats', methods=['GET'])
    def get_stats():
        """获取性能统计"""
        try:
            days = int(request.args.get('days', 7))
            stats = handler.get_performance_stats(days=days)
            
            if stats:
                return jsonify({'success': True, 'stats': stats})
            else:
                return jsonify({'success': False, 'error': '无法获取统计数据'}), 500
                
        except Exception as e:
            logger.error(f"统计查询异常: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({'status': 'ok', 'service': 'maoge_image_receiver'})
    
    # 启动服务
    logger.info(f"HTTP服务启动: http://0.0.0.0:{port}")
    
    # 发送启动通知
    startup_msg = f"""🌐 猫哥图文上传服务已启动

🔗 上传接口: http://服务器IP:{port}/upload
📝 反馈接口: http://服务器IP:{port}/feedback
📊 统计接口: http://服务器IP:{port}/stats
⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 使用方法:
1. POST图片到/upload接口
2. 系统自动分析并推送结果
3. POST反馈到/feedback接口

系统已准备就绪，等待图文上传..."""
    
    send_wechat_message(startup_msg)
    
    app.run(host='0.0.0.0', port=port, debug=False)


# ==================== 主函数 ====================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='企业微信图文上传接口')
    parser.add_argument('--mode', choices=['directory', 'http', 'both'], default='directory',
                       help='运行模式: directory(目录监控), http(HTTP服务), both(两者都启动)')
    parser.add_argument('--watch-dir', default='/root/maoge_advisor/maoge_images',
                       help='监控目录路径')
    parser.add_argument('--port', type=int, default=8888,
                       help='HTTP服务端口')
    
    args = parser.parse_args()
    
    # 初始化配置
    MaogeConfig.init_paths()
    
    if args.mode == 'directory':
        # 只启动目录监控
        start_directory_monitor(args.watch_dir)
        
    elif args.mode == 'http':
        # 只启动HTTP服务
        start_http_server(args.port)
        
    elif args.mode == 'both':
        # 同时启动两个服务（需要多进程）
        import multiprocessing
        
        p1 = multiprocessing.Process(target=start_directory_monitor, args=(args.watch_dir,))
        p2 = multiprocessing.Process(target=start_http_server, args=(args.port,))
        
        p1.start()
        p2.start()
        
        try:
            p1.join()
            p2.join()
        except KeyboardInterrupt:
            p1.terminate()
            p2.terminate()
            logger.info("服务已停止")


if __name__ == "__main__":
    main()
