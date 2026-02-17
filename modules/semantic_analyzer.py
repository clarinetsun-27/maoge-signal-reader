#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义分析器模块
使用AI理解猫哥图文的含义，提取结构化信息
"""

import os
import json
import logging
from typing import Dict, Optional
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """语义分析器"""
    
    def __init__(self, model="gpt-4.1-mini"):
        """
        初始化语义分析器
        
        Args:
            model: 使用的AI模型
        """
        try:
            # 使用智增增API
            self.client = OpenAI(
                api_key=os.environ.get("ZZZAPI"),
                base_url="https://api.zhizengzeng.com/v1"
            )
            self.model = model
            logger.info(f"语义分析器初始化成功，使用模型: {model}")
        except Exception as e:
            logger.error(f"语义分析器初始化失败: {e}")
            raise
    
    def analyze_content(self, text: str, image_path: Optional[str] = None) -> Dict:
        """
        分析猫哥图文内容，提取结构化信息
        
        Args:
            text: 提取的文字内容
            image_path: 图片路径（可选，用于多模态分析）
            
        Returns:
            结构化的分析结果
        """
        try:
            logger.info("开始分析内容...")
            
            prompt = self._build_prompt(text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            logger.info("内容分析完成")
            return result
            
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return self._get_empty_result()
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的投资信号分析师，专门解读"猫哥"发布的投资图文内容。

猫哥是一位资深投资顾问，他的分析特点：
1. 基于黄金波动率、黄金铜比等量化指标
2. 将市场划分为买入期、持有期、减仓期三个周期
3. 提供激进、稳健、保守三种策略
4. 用"笑脸"表示买入或卖出信号的强度
5. 关注宽基ETF、黄金、铜等标的

你的任务是准确提取猫哥图文中的关键信息，并输出结构化的JSON数据。"""
    
    def _build_prompt(self, text: str) -> str:
        """构建分析提示词"""
        return f"""请分析以下猫哥发布的投资图文内容，提取关键信息。

原文内容：
{text}

请以JSON格式输出以下信息：
{{
    "date": "发布日期（YYYY-MM-DD格式）",
    "market_cycle": "市场周期判断（买入期/持有期/减仓期/未明确）",
    "key_indicators": {{
        "gold_volatility": "黄金波动率数值（如果提到，否则为null）",
        "gold_copper_ratio": "黄金铜比值（如果提到，否则为null）",
        "price_changes": ["涨跌幅数据列表"]
    }},
    "trend_judgment": "趋势判断（看涨/看跌/震荡/未明确）",
    "risk_assessment": {{
        "risk_level": "风险等级（高/中/低/未明确）",
        "expected_space": "预期涨跌空间（如果提到）",
        "probability": "概率判断（如果提到）"
    }},
    "operation_suggestions": [
        {{
            "strategy": "策略类型（激进/稳健/保守）",
            "action": "操作建议（建仓/加仓/减仓/清仓/观望）",
            "position": "仓位建议（如果提到）",
            "timing": "时机建议（如果提到）"
        }}
    ],
    "mentioned_targets": ["提到的标的代码或名称列表"],
    "time_window": "时间窗口（如果提到，如'未来1-2周'）",
    "key_points": ["核心要点列表，每个要点一句话"],
    "sentiment": "整体情绪（乐观/谨慎/悲观/中性）",
    "confidence": "信号强度（强/中/弱），基于用词和语气判断"
}}

注意：
1. 如果某项信息未提到，请填写"未明确"或null
2. 尽可能提取所有数值信息
3. 操作建议可能有多个，针对不同策略
4. 核心要点要简洁明了，每个要点不超过30字
5. 保持客观，不要添加原文没有的内容"""
    
    def _get_empty_result(self) -> Dict:
        """获取空结果"""
        return {
            "date": None,
            "market_cycle": "未明确",
            "key_indicators": {
                "gold_volatility": None,
                "gold_copper_ratio": None,
                "price_changes": []
            },
            "trend_judgment": "未明确",
            "risk_assessment": {
                "risk_level": "未明确",
                "expected_space": None,
                "probability": None
            },
            "operation_suggestions": [],
            "mentioned_targets": [],
            "time_window": None,
            "key_points": [],
            "sentiment": "中性",
            "confidence": "弱"
        }
    
    def extract_smile_hints(self, text: str) -> Dict:
        """
        提取笑脸相关的暗示
        
        Args:
            text: 文字内容
            
        Returns:
            笑脸暗示信息
        """
        hints = {
            'has_smile': False,
            'smile_type': None,  # 'buy' or 'sell'
            'smile_count': 0,
            'keywords': []
        }
        
        # 买入笑脸关键词
        buy_keywords = ['买入', '建仓', '加仓', '机会', '低位', '超跌', '安全']
        # 卖出笑脸关键词
        sell_keywords = ['卖出', '减仓', '清仓', '风险', '高位', '超买', '警戒']
        
        buy_count = sum(1 for kw in buy_keywords if kw in text)
        sell_count = sum(1 for kw in sell_keywords if kw in text)
        
        if buy_count > sell_count and buy_count >= 2:
            hints['has_smile'] = True
            hints['smile_type'] = 'buy'
            hints['smile_count'] = min(buy_count // 2, 2)
            hints['keywords'] = [kw for kw in buy_keywords if kw in text]
        elif sell_count > buy_count and sell_count >= 2:
            hints['has_smile'] = True
            hints['smile_type'] = 'sell'
            hints['smile_count'] = min(sell_count // 2, 2)
            hints['keywords'] = [kw for kw in sell_keywords if kw in text]
        
        return hints


if __name__ == '__main__':
    # 测试代码
    test_text = """
    今日市场分析（2026-02-17）
    
    黄金波动率：22.5（低于安全线25）
    市场周期：买入期
    
    当前市场处于底部区域，风险较低。
    建议激进投资者可以适当建仓，稳健投资者观望。
    关注标的：黄金ETF(518880)、沪深300(510300)
    
    预计未来1-2周有5-8%的上涨空间。
    """
    
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze_content(test_text)
    
    print("=" * 50)
    print("分析结果:")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 50)
    
    smile_hints = analyzer.extract_smile_hints(test_text)
    print("笑脸暗示:")
    print(json.dumps(smile_hints, ensure_ascii=False, indent=2))
