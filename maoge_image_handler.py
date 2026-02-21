#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫哥图文解读处理器
集成到Tommy投资顾问系统v22.4

功能：
1. 接收企业微信上传的猫哥图文
2. 自动分析图文内容
3. 预测笑脸并推送结果
4. 记录反馈并优化模型
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

# 添加modules目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from ocr_extractor import OCRExtractor
from semantic_analyzer import SemanticAnalyzer
from signal_analyzer import SignalAnalyzer
from learning_optimizer import LearningOptimizer

# 配置日志
logger = logging.getLogger('maoge_image_handler')

# ==================== 配置 ====================

class MaogeConfig:
    """猫哥图文解读配置"""
    
    # 数据库路径
    DB_PATH = '/root/maoge_advisor/maoge_predictions.db'
    
    # 图文存储路径
    IMAGE_STORAGE_PATH = '/root/maoge_advisor/maoge_images'
    
    # 企业微信Webhook
    WECHAT_WEBHOOK = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=24b66ce0-84ed-46d4-ae37-89a4e71cc7fa'
    
    # 笑脸反馈接口（企业微信交互）
    FEEDBACK_ENABLED = True
    
    @classmethod
    def init_paths(cls):
        """初始化路径"""
        # 尝试多个可能的路径
        possible_bases = [
            '/root/maoge_advisor',
            '/home/ubuntu/maoge_advisor',
            '/home/ubuntu/tommy_advisor',
            '.'
        ]
        
        for base in possible_bases:
            try:
                Path(base).mkdir(parents=True, exist_ok=True)
                cls.DB_PATH = os.path.join(base, 'maoge_predictions.db')
                cls.IMAGE_STORAGE_PATH = os.path.join(base, 'maoge_images')
                Path(cls.IMAGE_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
                logger.info(f"数据路径初始化成功: {base}")
                return True
            except:
                continue
        
        logger.warning("无法初始化数据路径，使用当前目录")
        cls.DB_PATH = './maoge_predictions.db'
        cls.IMAGE_STORAGE_PATH = './maoge_images'
        Path(cls.IMAGE_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        return False


# ==================== 图文处理器 ====================

class MaogeImageHandler:
    """猫哥图文处理器"""
    
    def __init__(self):
        """初始化处理器"""
        # 初始化路径
        MaogeConfig.init_paths()
        
        # 初始化组件
        self.ocr = OCRExtractor()
        self.semantic = SemanticAnalyzer()
        self.signal = SignalAnalyzer()
        self.optimizer = LearningOptimizer(MaogeConfig.DB_PATH)
        
        logger.info("猫哥图文处理器初始化完成")
    
    def process_image(self, image_path, source='manual'):
        """
        处理单张图文
        
        Args:
            image_path: 图片路径
            source: 来源（manual/wechat）
        
        Returns:
            dict: 处理结果
        """
        try:
            logger.info(f"开始处理图文: {image_path}")
            
            # 1. OCR提取文字
            logger.info("步骤1: 提取文字...")
            text_content = self.ocr.extract_text(image_path)
            
            if not text_content or len(text_content) < 50:
                logger.warning(f"文字提取失败或内容过短，实际内容: {repr(text_content)}")
                return {
                    'success': False,
                    'error': f'文字提取失败或内容过短: {repr(text_content)}'
                }
            
            logger.info(f"文字提取成功，共{len(text_content)}字")
            
            # 2. 语义分析
            logger.info("步骤2: 语义分析...")
            analysis = self.semantic.analyze(text_content)
            
            if not analysis:
                logger.warning("语义分析失败")
                return {
                    'success': False,
                    'error': '语义分析失败'
                }
            
            logger.info("语义分析完成")
            
            # 3. 信号分析和笑脸预测
            logger.info("步骤3: 信号分析和笑脸预测...")
            prediction = self.signal.analyze_and_predict(analysis)
            
            if not prediction:
                logger.warning("信号分析失败")
                return {
                    'success': False,
                    'error': '信号分析失败'
                }
            
            logger.info(f"预测完成: {prediction['prediction']}, 置信度: {prediction['confidence']:.1%}")
            
            # 4. 保存预测记录
            prediction_id = self.optimizer.save_prediction(
                date=analysis.get('date', datetime.now().strftime('%Y-%m-%d')),
                image_path=image_path,
                text_content=text_content,
                analysis_result=json.dumps(analysis, ensure_ascii=False),
                predicted_smile=prediction['prediction'],
                confidence=prediction['confidence'],
                predicted_count=prediction.get('predicted_count', 1.0)
            )
            
            logger.info(f"预测记录已保存，ID: {prediction_id}")
            
            # 5. 生成推送消息
            message = self._format_analysis_message(
                analysis, 
                prediction, 
                image_path,
                prediction_id
            )
            
            # 6. 返回结果
            return {
                'success': True,
                'prediction_id': prediction_id,
                'analysis': analysis,
                'prediction': prediction,
                'message': message,
                'text_length': len(text_content)
            }
            
        except Exception as e:
            logger.error(f"处理图文异常: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_analysis_message(self, analysis, prediction, image_path, prediction_id):
        """格式化分析结果消息"""
        
        # 笑脸emoji映射
        smile_emoji = {
            'buy_smile': '😊',
            'sell_smile': '😢',
            'hold': '😐',
            'unknown': '❓'
        }
        
        emoji = smile_emoji.get(prediction['prediction'], '❓')
        
        # 置信度条
        confidence = prediction['confidence']
        conf_bar = '█' * int(confidence * 10) + '░' * (10 - int(confidence * 10))
        
        # 构建消息
        message = f"""📊 猫哥图文分析结果

📅 日期: {analysis.get('date', '未知')}
🔄 市场周期: {analysis.get('market_cycle', '未知')}
📈 趋势判断: {analysis.get('trend', '未知')}
⚠️ 风险等级: {analysis.get('risk_level', '未知')}

{emoji} 笑脸预测: {prediction['prediction']}
📊 置信度: {confidence:.1%} {conf_bar}
🔢 预计数量: {prediction.get('predicted_count', 1.0):.1f}个

💡 核心要点:"""
        
        # 添加核心要点（最多5条）
        key_points = analysis.get('key_points', [])
        for i, point in enumerate(key_points[:5], 1):
            message += f"\n{i}. {point}"
        
        # 添加操作建议
        suggestions = analysis.get('suggestions', {})
        if suggestions:
            message += "\n\n📋 操作建议:"
            for strategy_type, suggestion in suggestions.items():
                message += f"\n• {strategy_type}: {suggestion.get('action', '未知')}"
        
        # 添加反馈提示
        message += f"\n\n💬 预测ID: {prediction_id}"
        message += "\n📝 请在猫哥发布笑脸后反馈实际结果"
        
        return message
    
    def save_feedback(self, prediction_id, actual_smile, actual_count=None):
        """
        保存笑脸反馈
        
        Args:
            prediction_id: 预测ID
            actual_smile: 实际笑脸类型
            actual_count: 实际笑脸数量
        
        Returns:
            bool: 是否成功
        """
        try:
            success = self.optimizer.save_feedback(
                prediction_id=prediction_id,
                actual_smile=actual_smile,
                actual_count=actual_count
            )
            
            if success:
                logger.info(f"反馈已保存: ID={prediction_id}, 实际={actual_smile}")
                
                # 触发模型优化
                self.optimizer.optimize_model()
                
            return success
            
        except Exception as e:
            logger.error(f"保存反馈异常: {e}", exc_info=True)
            return False
    
    def get_performance_stats(self, days=7):
        """
        获取性能统计
        
        Args:
            days: 统计天数
        
        Returns:
            dict: 性能统计
        """
        try:
            stats = self.optimizer.get_performance_stats(days=days)
            return stats
        except Exception as e:
            logger.error(f"获取性能统计异常: {e}", exc_info=True)
            return None


# ==================== 企业微信交互 ====================

def send_wechat_message(message):
    """发送企业微信消息"""
    import requests
    
    try:
        url = MaogeConfig.WECHAT_WEBHOOK
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('errcode') == 0:
                logger.info("企业微信消息发送成功")
                return True
            else:
                logger.error(f"企业微信消息发送失败: {result}")
                return False
        else:
            logger.error(f"企业微信消息发送失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"发送企业微信消息异常: {e}", exc_info=True)
        return False


# ==================== 命令行接口 ====================

def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='猫哥图文解读处理器')
    parser.add_argument('image_path', help='图片路径')
    parser.add_argument('--feedback', help='反馈笑脸 (格式: prediction_id:actual_smile:count)')
    parser.add_argument('--stats', action='store_true', help='显示性能统计')
    
    args = parser.parse_args()
    
    # 初始化处理器
    handler = MaogeImageHandler()
    
    # 处理反馈
    if args.feedback:
        parts = args.feedback.split(':')
        if len(parts) >= 2:
            prediction_id = int(parts[0])
            actual_smile = parts[1]
            actual_count = float(parts[2]) if len(parts) > 2 else None
            
            success = handler.save_feedback(prediction_id, actual_smile, actual_count)
            print(f"反馈保存{'成功' if success else '失败'}")
        else:
            print("反馈格式错误，应为: prediction_id:actual_smile:count")
        return
    
    # 显示统计
    if args.stats:
        stats = handler.get_performance_stats()
        if stats:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print("无法获取统计数据")
        return
    
    # 处理图文
    if os.path.exists(args.image_path):
        result = handler.process_image(args.image_path)
        
        if result['success']:
            print("=" * 60)
            print("分析成功！")
            print("=" * 60)
            print(result['message'])
            print("=" * 60)
            
            # 发送到企业微信
            send_wechat_message(result['message'])
        else:
            print(f"分析失败: {result.get('error', '未知错误')}")
    else:
        print(f"图片不存在: {args.image_path}")


if __name__ == "__main__":
    main()
