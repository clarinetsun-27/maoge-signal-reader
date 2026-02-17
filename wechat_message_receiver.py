#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信消息接收服务
接收企业微信发送的图片消息，自动下载并分析

支持两种方式：
1. 企业微信应用回调（需要配置应用）
2. 企业微信群机器人（简化方案，推荐）
"""

import os
import sys
import json
import logging
import hashlib
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from maoge_image_handler import MaogeImageHandler, send_wechat_message, MaogeConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('wechat_message_receiver')

# Flask应用
app = Flask(__name__)

# 初始化处理器
handler = MaogeImageHandler()


# ==================== 企业微信消息接收 ====================

@app.route('/wechat/callback', methods=['GET', 'POST'])
def wechat_callback():
    """
    企业微信消息回调接口
    
    GET: 验证URL有效性
    POST: 接收消息
    """
    if request.method == 'GET':
        # 验证URL
        return verify_url(request)
    else:
        # 接收消息
        return receive_message(request)


def verify_url(request):
    """验证URL有效性"""
    try:
        msg_signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        # 这里需要使用企业微信的加密库进行验证
        # 简化处理：直接返回echostr
        logger.info(f"URL验证请求: timestamp={timestamp}, nonce={nonce}")
        
        return echostr
        
    except Exception as e:
        logger.error(f"URL验证失败: {e}", exc_info=True)
        return 'error', 400


def receive_message(request):
    """接收企业微信消息"""
    try:
        # 获取消息内容
        data = request.data
        logger.info(f"收到企业微信消息: {data[:200]}")
        
        # 解析XML消息（企业微信使用XML格式）
        import xml.etree.ElementTree as ET
        root = ET.fromstring(data)
        
        msg_type = root.find('MsgType').text
        
        if msg_type == 'image':
            # 图片消息
            media_id = root.find('MediaId').text
            pic_url = root.find('PicUrl').text
            
            logger.info(f"收到图片消息: MediaId={media_id}, PicUrl={pic_url}")
            
            # 下载并处理图片
            process_image_message(media_id, pic_url)
            
            return 'success'
        else:
            logger.info(f"忽略非图片消息: {msg_type}")
            return 'success'
            
    except Exception as e:
        logger.error(f"处理消息失败: {e}", exc_info=True)
        return 'error', 500


def process_image_message(media_id, pic_url):
    """处理图片消息"""
    try:
        # 下载图片
        logger.info(f"下载图片: {pic_url}")
        response = requests.get(pic_url, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"下载图片失败: HTTP {response.status_code}")
            send_wechat_message(f"⚠️ 图片下载失败\n\nHTTP {response.status_code}")
            return
        
        # 保存图片
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{media_id}.jpg"
        image_path = os.path.join(MaogeConfig.IMAGE_STORAGE_PATH, filename)
        
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"图片已保存: {image_path}")
        
        # 处理图片
        result = handler.process_image(image_path, source='wechat_message')
        
        if result['success']:
            # 发送分析结果
            send_wechat_message(result['message'])
            logger.info(f"分析完成，结果已推送")
        else:
            error_msg = f"⚠️ 图片分析失败\n\n错误: {result.get('error', '未知错误')}"
            send_wechat_message(error_msg)
            logger.error(f"分析失败: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"处理图片消息异常: {e}", exc_info=True)
        send_wechat_message(f"⚠️ 处理图片异常\n\n{str(e)}")


# ==================== 简化方案：HTTP上传接口 ====================

@app.route('/upload/image', methods=['POST'])
def upload_image():
    """
    简化的图片上传接口
    可以通过企业微信群机器人或其他方式调用
    """
    try:
        # 方式1: multipart/form-data 文件上传
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'success': False, 'error': '文件名为空'}), 400
            
            # 保存文件
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_filename = f"{timestamp}_{filename}"
            save_path = os.path.join(MaogeConfig.IMAGE_STORAGE_PATH, save_filename)
            
            file.save(save_path)
            logger.info(f"文件已保存: {save_path}")
        
        # 方式2: JSON格式，包含图片URL
        elif request.is_json:
            data = request.get_json()
            image_url = data.get('image_url')
            
            if not image_url:
                return jsonify({'success': False, 'error': '缺少image_url参数'}), 400
            
            # 下载图片
            logger.info(f"下载图片: {image_url}")
            response = requests.get(image_url, timeout=30)
            
            if response.status_code != 200:
                return jsonify({'success': False, 'error': f'下载失败: HTTP {response.status_code}'}), 400
            
            # 保存图片
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_uploaded.jpg"
            save_path = os.path.join(MaogeConfig.IMAGE_STORAGE_PATH, filename)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图片已保存: {save_path}")
        
        else:
            return jsonify({'success': False, 'error': '不支持的请求格式'}), 400
        
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
def feedback():
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
😊 实际笑脸: {actual_smile}
🔢 实际数量: {actual_count or '未指定'}

系统将根据反馈优化模型。"""
            
            send_wechat_message(feedback_msg)
            
            return jsonify({'success': True, 'message': '反馈已保存'})
        else:
            return jsonify({'success': False, 'error': '保存反馈失败'}), 500
            
    except Exception as e:
        logger.error(f"反馈处理异常: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'wechat_message_receiver',
        'timestamp': datetime.now().isoformat()
    })


# ==================== 主函数 ====================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='企业微信消息接收服务')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8888, help='监听端口')
    
    args = parser.parse_args()
    
    # 初始化配置
    MaogeConfig.init_paths()
    
    # 发送启动通知
    startup_msg = f"""🌐 企业微信消息接收服务已启动

🔗 上传接口: http://服务器IP:{args.port}/upload/image
📝 反馈接口: http://服务器IP:{args.port}/feedback
⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 使用方法:
1. 在企业微信发送图片（需配置应用回调）
2. 或通过HTTP接口上传图片
3. 系统自动分析并推送结果

系统已准备就绪，等待图文上传..."""
    
    send_wechat_message(startup_msg)
    
    logger.info(f"企业微信消息接收服务启动: http://{args.host}:{args.port}")
    
    # 启动Flask服务
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
