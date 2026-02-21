#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用视觉模型分析小鹅通圈子内容
"""

import os
import sys
import json
import base64
import logging
from openai import OpenAI

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def analyze_image_with_vision(image_path):
    """使用视觉模型分析图片"""
    try:
        logger.info(f"📸 分析图片: {image_path}")
        
        # 读取图片并转为base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # 初始化OpenAI客户端
        client = OpenAI()
        
        # 构造提示词
        prompt = """请分析这张小鹅通圈子的图文内容，提取以下信息：

1. **发布者信息**：作者名称、是否是管理员
2. **发布时间**：日期和时间
3. **文字内容**：完整的文字描述（即使文字无法被选中复制，也请尽力识别）
4. **配图分析**：
   - 是否包含K线图或价格走势图
   - 如果有，请描述图表显示的内容（标的名称、价格、趋势等）
5. **投资建议**：
   - 是否隐含投资建议（买入/卖出/持有）
   - 涉及的标的（股票代码或ETF）
   - 建议的理由

请以JSON格式返回结果，包含以下字段：
{
  "author": "作者名称",
  "is_admin": true/false,
  "publish_time": "发布时间",
  "text_content": "完整文字内容",
  "has_chart": true/false,
  "chart_description": "图表描述",
  "investment_advice": {
    "action": "buy/sell/hold/none",
    "target": "标的代码或名称",
    "reasoning": "理由"
  }
}"""
        
        # 调用视觉模型
        logger.info("🤖 调用视觉模型...")
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # 使用支持视觉的模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        # 获取结果
        result_text = response.choices[0].message.content.strip()
        logger.info(f"✅ 模型返回结果:\n{result_text}")
        
        # 尝试解析JSON
        try:
            # 提取JSON部分（可能包含在markdown代码块中）
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            
            result = json.loads(result_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            logger.warning(f"原始文本: {result_text}")
            return {"raw_response": result_text}
        
    except Exception as e:
        logger.error(f"❌ 分析失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def main():
    """主函数"""
    if len(sys.argv) < 2:
        logger.error("请提供图片路径")
        logger.info("用法: python3 test_vision_analysis.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        logger.error(f"文件不存在: {image_path}")
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("🚀 开始使用视觉模型分析图片")
    logger.info("="*60)
    
    result = analyze_image_with_vision(image_path)
    
    if result:
        logger.info("="*60)
        logger.info("✅ 分析成功！")
        logger.info("="*60)
        logger.info(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        logger.error("="*60)
        logger.error("❌ 分析失败")
        logger.error("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
