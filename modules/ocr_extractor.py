"""
OCR文字提取模块
使用智增增API的GPT-4.1-mini模型进行图像理解和文字提取
"""

import os
import base64
import logging
from typing import Tuple, List, Dict
from openai import OpenAI

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRExtractor:
    """OCR文字提取器（基于智增增API）"""
    
    def __init__(self, use_gpu: bool = False):
        """
        初始化OCR提取器
        
        Args:
            use_gpu: 保留参数以兼容旧代码，实际不使用
        """
        try:
            # 初始化智增增API客户端
            self.client = OpenAI(
                api_key=os.environ.get("ZZZAPI"),
                base_url="https://api.zhizengzeng.com/v1"
            )
            self.model = "gpt-4.1-mini"  # 使用支持视觉的模型
            logger.info("OCR提取器初始化成功（使用智增增API）")
        except Exception as e:
            logger.error(f"OCR提取器初始化失败: {e}")
            raise
    
    def extract_text(self, image_path: str) -> Tuple[str, List[Dict]]:
        """
        从图片中提取文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            (提取的文字, 文字块列表)
        """
        try:
            logger.info(f"开始提取图片文字: {image_path}")
            
            # 读取图片并转为base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # 调用API提取文字
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请提取这张图片中的所有文字内容，保持原有的格式和顺序。只输出文字内容，不要添加任何解释或说明。"
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
                max_tokens=3000,
                temperature=0.1  # 降低温度以获得更准确的提取
            )
            
            # 获取提取的文字
            extracted_text = response.choices[0].message.content.strip()
            
            # 构造文字块列表（简化版，因为API不返回位置信息）
            text_blocks = [
                {
                    "text": line,
                    "confidence": 0.95,  # API提取的置信度通常很高
                    "position": None  # API不提供位置信息
                }
                for line in extracted_text.split('\n') if line.strip()
            ]
            
            logger.info(f"文字提取完成，共{len(text_blocks)}个文字块")
            
            return extracted_text, text_blocks
            
        except Exception as e:
            logger.error(f"文字提取失败: {e}")
            raise
    
    def extract_with_layout(self, image_path: str) -> Dict:
        """
        提取文字并保留布局信息（使用AI理解）
        
        Args:
            image_path: 图片路径
            
        Returns:
            包含文字和布局信息的字典
        """
        try:
            logger.info(f"开始提取图片文字和布局: {image_path}")
            
            # 读取图片并转为base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # 调用API提取文字和布局
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """请分析这张图片的内容和布局，提取以下信息：
1. 标题（如果有）
2. 正文内容
3. 关键数据（数字、百分比等）
4. 特殊标记（如笑脸、箭头等）

请以JSON格式输出，格式如下：
{
    "title": "标题",
    "content": "正文内容",
    "key_data": ["数据1", "数据2"],
    "special_marks": ["标记1", "标记2"]
}"""
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
                max_tokens=3000,
                temperature=0.1
            )
            
            # 获取结构化信息
            import json
            result_text = response.choices[0].message.content.strip()
            
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
                
                layout_info = json.loads(result_text)
            except:
                # 如果解析失败，返回原始文本
                layout_info = {
                    "title": "",
                    "content": result_text,
                    "key_data": [],
                    "special_marks": []
                }
            
            logger.info(f"文字和布局提取完成")
            
            return layout_info
            
        except Exception as e:
            logger.error(f"文字和布局提取失败: {e}")
            raise


if __name__ == "__main__":
    # 测试代码
    import json
    extractor = OCRExtractor()
    
    # 测试基础提取
    test_image = "/home/ubuntu/maoge_content/2月2日-13日图文/020201.png"
    text, blocks = extractor.extract_text(test_image)
    
    print("提取的文字：")
    print("=" * 60)
    print(text)
    print("=" * 60)
    print(f"\n共{len(blocks)}个文字块")
    
    # 测试布局提取
    layout = extractor.extract_with_layout(test_image)
    print("\n布局信息：")
    print(json.dumps(layout, ensure_ascii=False, indent=2))
