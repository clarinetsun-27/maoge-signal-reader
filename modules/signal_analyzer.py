#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信号分析器模块
基于解析的内容，提取投资信号并预测笑脸
"""

import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalAnalyzer:
    """信号分析器"""
    
    def __init__(self, config_path=None):
        """
        初始化信号分析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        logger.info("信号分析器初始化成功")
    
    def _load_config(self, config_path):
        """加载配置"""
        default_config = {
            'weights': {
                'market_cycle': 3,
                'trend_judgment': 2,
                'risk_level': 1,
                'operation_suggestion': 1,
                'confidence': 1
            },
            'thresholds': {
                'buy_smile_threshold': 4,
                'sell_smile_threshold': 4,
                'strong_signal_threshold': 6
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config.get('prediction_config', {}))
            except Exception as e:
                logger.warning(f"加载配置文件失败，使用默认配置: {e}")
        
        return default_config
    
    def analyze(self, structured_data: Dict) -> Dict:
        """
        分析信号
        
        Args:
            structured_data: 语义分析的结构化数据
            
        Returns:
            信号分析结果
        """
        try:
            logger.info("开始分析信号...")
            
            signals = {
                'buy_signals': [],
                'sell_signals': [],
                'hold_signals': [],
                'smile_prediction': self.predict_smile(structured_data),
                'signal_strength': 0,
                'recommendation': None
            }
            
            # 提取买入信号
            signals['buy_signals'] = self._extract_buy_signals(structured_data)
            
            # 提取卖出信号
            signals['sell_signals'] = self._extract_sell_signals(structured_data)
            
            # 提取持有信号
            signals['hold_signals'] = self._extract_hold_signals(structured_data)
            
            # 计算信号强度
            signals['signal_strength'] = self._calculate_signal_strength(signals)
            
            # 生成操作建议
            signals['recommendation'] = self._generate_recommendation(signals)
            
            logger.info(f"信号分析完成，买入信号{len(signals['buy_signals'])}个，"
                       f"卖出信号{len(signals['sell_signals'])}个")
            
            return signals
            
        except Exception as e:
            logger.error(f"信号分析失败: {e}")
            return self._get_empty_signals()
    
    def _extract_buy_signals(self, data: Dict) -> List[Dict]:
        """提取买入信号"""
        signals = []
        
        # 市场周期信号
        if data.get('market_cycle') == '买入期':
            signals.append({
                'type': 'market_cycle',
                'strength': 'strong',
                'weight': 3,
                'reason': '猫哥判断当前为买入期'
            })
        
        # 趋势判断信号
        if data.get('trend_judgment') == '看涨':
            signals.append({
                'type': 'trend',
                'strength': 'medium',
                'weight': 2,
                'reason': '趋势判断为看涨'
            })
        
        # 风险评估信号
        risk = data.get('risk_assessment', {})
        if risk.get('risk_level') == '低':
            signals.append({
                'type': 'risk',
                'strength': 'medium',
                'weight': 1,
                'reason': '风险等级为低'
            })
        
        # 波动率信号
        indicators = data.get('key_indicators', {})
        if indicators.get('gold_volatility'):
            try:
                volatility = float(indicators['gold_volatility'])
                if volatility < 25:
                    signals.append({
                        'type': 'volatility',
                        'strength': 'strong',
                        'weight': 3,
                        'reason': f'黄金波动率{volatility}低于安全线25'
                    })
                elif 25 <= volatility < 30:
                    signals.append({
                        'type': 'volatility',
                        'strength': 'medium',
                        'weight': 2,
                        'reason': f'黄金波动率{volatility}处于安全区'
                    })
            except ValueError:
                pass
        
        # 操作建议信号
        for suggestion in data.get('operation_suggestions', []):
            action = suggestion.get('action', '')
            if '建仓' in action or '加仓' in action:
                signals.append({
                    'type': 'operation',
                    'strength': 'medium',
                    'weight': 1,
                    'strategy': suggestion.get('strategy'),
                    'reason': f"{suggestion.get('strategy')}策略: {action}"
                })
        
        # 情绪信号
        if data.get('sentiment') == '乐观':
            signals.append({
                'type': 'sentiment',
                'strength': 'weak',
                'weight': 0.5,
                'reason': '整体情绪乐观'
            })
        
        return signals
    
    def _extract_sell_signals(self, data: Dict) -> List[Dict]:
        """提取卖出信号"""
        signals = []
        
        # 市场周期信号
        if data.get('market_cycle') == '减仓期':
            signals.append({
                'type': 'market_cycle',
                'strength': 'strong',
                'weight': 3,
                'reason': '猫哥判断当前为减仓期'
            })
        
        # 趋势判断信号
        if data.get('trend_judgment') == '看跌':
            signals.append({
                'type': 'trend',
                'strength': 'medium',
                'weight': 2,
                'reason': '趋势判断为看跌'
            })
        
        # 风险评估信号
        risk = data.get('risk_assessment', {})
        if risk.get('risk_level') == '高':
            signals.append({
                'type': 'risk',
                'strength': 'medium',
                'weight': 1,
                'reason': '风险等级为高'
            })
        
        # 波动率信号
        indicators = data.get('key_indicators', {})
        if indicators.get('gold_volatility'):
            try:
                volatility = float(indicators['gold_volatility'])
                if volatility > 37:
                    signals.append({
                        'type': 'volatility',
                        'strength': 'strong',
                        'weight': 3,
                        'reason': f'黄金波动率{volatility}超过警戒线37'
                    })
                elif 32 < volatility <= 37:
                    signals.append({
                        'type': 'volatility',
                        'strength': 'medium',
                        'weight': 2,
                        'reason': f'黄金波动率{volatility}处于警戒区'
                    })
            except ValueError:
                pass
        
        # 操作建议信号
        for suggestion in data.get('operation_suggestions', []):
            action = suggestion.get('action', '')
            if '减仓' in action or '清仓' in action:
                signals.append({
                    'type': 'operation',
                    'strength': 'medium',
                    'weight': 1,
                    'strategy': suggestion.get('strategy'),
                    'reason': f"{suggestion.get('strategy')}策略: {action}"
                })
        
        # 情绪信号
        if data.get('sentiment') == '悲观':
            signals.append({
                'type': 'sentiment',
                'strength': 'weak',
                'weight': 0.5,
                'reason': '整体情绪悲观'
            })
        
        return signals
    
    def _extract_hold_signals(self, data: Dict) -> List[Dict]:
        """提取持有信号"""
        signals = []
        
        # 市场周期信号
        if data.get('market_cycle') == '持有期':
            signals.append({
                'type': 'market_cycle',
                'strength': 'medium',
                'weight': 2,
                'reason': '猫哥判断当前为持有期'
            })
        
        # 趋势判断信号
        if data.get('trend_judgment') == '震荡':
            signals.append({
                'type': 'trend',
                'strength': 'medium',
                'weight': 1,
                'reason': '趋势判断为震荡'
            })
        
        # 操作建议信号
        for suggestion in data.get('operation_suggestions', []):
            action = suggestion.get('action', '')
            if '观望' in action or '持有' in action:
                signals.append({
                    'type': 'operation',
                    'strength': 'medium',
                    'weight': 1,
                    'strategy': suggestion.get('strategy'),
                    'reason': f"{suggestion.get('strategy')}策略: {action}"
                })
        
        return signals
    
    def predict_smile(self, data: Dict) -> Dict:
        """
        预测猫哥是否会给出笑脸
        
        Args:
            data: 结构化数据
            
        Returns:
            预测结果
        """
        buy_score = 0
        sell_score = 0
        
        weights = self.config['weights']
        
        # 市场周期权重
        if data.get('market_cycle') == '买入期':
            buy_score += weights['market_cycle']
        elif data.get('market_cycle') == '减仓期':
            sell_score += weights['market_cycle']
        
        # 趋势判断权重
        if data.get('trend_judgment') == '看涨':
            buy_score += weights['trend_judgment']
        elif data.get('trend_judgment') == '看跌':
            sell_score += weights['trend_judgment']
        
        # 风险等级权重
        risk = data.get('risk_assessment', {}).get('risk_level')
        if risk == '低':
            buy_score += weights['risk_level']
        elif risk == '高':
            sell_score += weights['risk_level']
        
        # 操作建议权重
        for suggestion in data.get('operation_suggestions', []):
            action = suggestion.get('action', '')
            if '建仓' in action or '加仓' in action:
                buy_score += weights['operation_suggestion']
            elif '减仓' in action or '清仓' in action:
                sell_score += weights['operation_suggestion']
        
        # 信号强度权重
        if data.get('confidence') == '强':
            if buy_score > sell_score:
                buy_score += weights['confidence']
            elif sell_score > buy_score:
                sell_score += weights['confidence']
        
        # 生成预测
        prediction = {
            'buy_score': buy_score,
            'sell_score': sell_score,
            'prediction': None,
            'confidence': 0,
            'smile_count': 0,
            'reasoning': []
        }
        
        thresholds = self.config['thresholds']
        
        if buy_score > sell_score and buy_score >= thresholds['buy_smile_threshold']:
            prediction['prediction'] = 'buy_smile'
            prediction['confidence'] = min(buy_score / thresholds['strong_signal_threshold'], 1.0)
            prediction['smile_count'] = self._estimate_smile_count(buy_score)
            prediction['reasoning'].append(f"买入信号得分{buy_score}分，超过阈值{thresholds['buy_smile_threshold']}")
        elif sell_score > buy_score and sell_score >= thresholds['sell_smile_threshold']:
            prediction['prediction'] = 'sell_smile'
            prediction['confidence'] = min(sell_score / thresholds['strong_signal_threshold'], 1.0)
            prediction['smile_count'] = self._estimate_smile_count(sell_score)
            prediction['reasoning'].append(f"卖出信号得分{sell_score}分，超过阈值{thresholds['sell_smile_threshold']}")
        else:
            prediction['prediction'] = 'no_smile'
            prediction['confidence'] = 0.5
            prediction['reasoning'].append(f"买入得分{buy_score}，卖出得分{sell_score}，均未达到阈值")
        
        return prediction
    
    def _estimate_smile_count(self, score: float) -> float:
        """估算笑脸数量"""
        if score >= 7:
            return 2.0  # 两个笑脸
        elif score >= 5.5:
            return 1.5  # 一个半笑脸
        elif score >= 4:
            return 1.0  # 一个笑脸
        else:
            return 0.5  # 半个笑脸
    
    def _calculate_signal_strength(self, signals: Dict) -> float:
        """计算信号强度"""
        buy_strength = sum(s.get('weight', 1) for s in signals['buy_signals'])
        sell_strength = sum(s.get('weight', 1) for s in signals['sell_signals'])
        
        return max(buy_strength, sell_strength)
    
    def _generate_recommendation(self, signals: Dict) -> Dict:
        """生成操作建议"""
        buy_count = len(signals['buy_signals'])
        sell_count = len(signals['sell_signals'])
        hold_count = len(signals['hold_signals'])
        
        if buy_count > sell_count and buy_count > hold_count:
            action = '建仓/加仓'
            reason = f"检测到{buy_count}个买入信号"
        elif sell_count > buy_count and sell_count > hold_count:
            action = '减仓/清仓'
            reason = f"检测到{sell_count}个卖出信号"
        else:
            action = '观望/持有'
            reason = f"信号不明确（买入{buy_count}，卖出{sell_count}，持有{hold_count}）"
        
        return {
            'action': action,
            'reason': reason,
            'confidence': signals['smile_prediction']['confidence']
        }
    
    def _get_empty_signals(self) -> Dict:
        """获取空信号"""
        return {
            'buy_signals': [],
            'sell_signals': [],
            'hold_signals': [],
            'smile_prediction': {
                'prediction': 'no_smile',
                'confidence': 0,
                'smile_count': 0
            },
            'signal_strength': 0,
            'recommendation': {
                'action': '观望',
                'reason': '无法分析信号',
                'confidence': 0
            }
        }


if __name__ == '__main__':
    # 测试代码
    test_data = {
        "date": "2026-02-17",
        "market_cycle": "买入期",
        "key_indicators": {
            "gold_volatility": "22.5"
        },
        "trend_judgment": "看涨",
        "risk_assessment": {
            "risk_level": "低"
        },
        "operation_suggestions": [
            {
                "strategy": "激进",
                "action": "适当建仓"
            }
        ],
        "confidence": "强"
    }
    
    analyzer = SignalAnalyzer()
    signals = analyzer.analyze(test_data)
    
    print("=" * 50)
    print("信号分析结果:")
    print("=" * 50)
    print(json.dumps(signals, ensure_ascii=False, indent=2))
