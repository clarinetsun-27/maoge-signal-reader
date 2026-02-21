#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单张图片测试脚本
用于调试编码问题
"""

import os
import sys
import logging

# 设置环境变量强制使用UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'

# 配置日志 - 使用UTF-8编码
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.insert(0, '/root/maoge_advisor')

# 导入图文处理器
from maoge_image_handler import MaogeImageHandler

def test_single_image(image_path):
    """测试单张图片"""
    try:
        logger.info("="*60)
        logger.info(f"测试图片: {image_path}")
        logger.info("="*60)
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"文件不存在: {image_path}")
            return False
        
        logger.info(f"文件大小: {os.path.getsize(image_path)} bytes")
        
        # 初始化处理器
        logger.info("初始化图文处理器...")
        handler = MaogeImageHandler()
        
        # 处理图片
        logger.info("开始处理图片...")
        result = handler.process_image(image_path, source='test')
        
        # 输出结果
        logger.info("="*60)
        logger.info("处理结果:")
        logger.info("="*60)
        
        if result and result.get('success'):
            logger.info("✅ 处理成功！")
            
            # 安全地输出结果
            if 'prediction' in result:
                pred = result['prediction']
                logger.info(f"预测结果:")
                logger.info(f"  - 操作: {pred.get('action', 'N/A')}")
                logger.info(f"  - 标的: {pred.get('target', 'N/A')}")
                logger.info(f"  - 置信度: {pred.get('confidence', 'N/A')}")
                logger.info(f"  - 理由: {pred.get('reasoning', 'N/A')[:100]}...")
            
            return True
        else:
            logger.error(f"❌ 处理失败: {result.get('error', '未知错误')}")
            return False
            
    except UnicodeEncodeError as e:
        logger.error(f"编码错误: {e}")
        logger.error(f"错误位置: {e.object[max(0, e.start-20):e.end+20]}")
        return False
    except Exception as e:
        logger.error(f"处理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """主函数"""
    # 测试第一张图片
    image_path = "/root/maoge_advisor/logs/images/image_1.png"
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    success = test_single_image(image_path)
    
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
