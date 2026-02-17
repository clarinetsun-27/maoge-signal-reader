#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习优化器模块
记录预测结果，与真实笑脸比对，优化预测模型
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningOptimizer:
    """学习优化器"""
    
    def __init__(self, db_path='/home/ubuntu/maoge_signal_reader/data/maoge_content.db'):
        """
        初始化学习优化器
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        self.model = None
        logger.info("学习优化器初始化成功")
    
    def _create_tables(self):
        """创建数据表"""
        # 预测历史表
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                prediction TEXT,
                confidence REAL,
                smile_count REAL,
                buy_score REAL,
                sell_score REAL,
                predicted_at TIMESTAMP,
                actual_result TEXT,
                actual_smile_count REAL,
                verified_at TIMESTAMP,
                is_correct INTEGER,
                FOREIGN KEY (content_id) REFERENCES maoge_content(id)
            )
        ''')
        
        # 模型性能表
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT,
                total_predictions INTEGER,
                correct_predictions INTEGER,
                accuracy REAL,
                avg_confidence REAL,
                evaluated_at TIMESTAMP
            )
        ''')
        
        # 错误案例表
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS error_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                error_type TEXT,
                analysis TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES prediction_history(id)
            )
        ''')
        
        self.conn.commit()
    
    def record_prediction(self, content_id: int, prediction: Dict) -> int:
        """
        记录预测结果
        
        Args:
            content_id: 内容ID
            prediction: 预测结果
            
        Returns:
            预测记录ID
        """
        try:
            cursor = self.conn.execute('''
                INSERT INTO prediction_history (
                    content_id, prediction, confidence, smile_count,
                    buy_score, sell_score, predicted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                content_id,
                prediction['prediction'],
                prediction['confidence'],
                prediction.get('smile_count', 0),
                prediction.get('buy_score', 0),
                prediction.get('sell_score', 0),
                datetime.now()
            ))
            
            self.conn.commit()
            prediction_id = cursor.lastrowid
            
            logger.info(f"记录预测结果: ID={prediction_id}, "
                       f"预测={prediction['prediction']}, "
                       f"置信度={prediction['confidence']:.2f}")
            
            return prediction_id
            
        except Exception as e:
            logger.error(f"记录预测结果失败: {e}")
            return -1
    
    def record_actual_result(self, content_id: int, actual_smile: str, 
                           smile_count: float = 0) -> bool:
        """
        记录真实笑脸结果
        
        Args:
            content_id: 内容ID
            actual_smile: 真实笑脸类型 (buy_smile/sell_smile/no_smile)
            smile_count: 笑脸数量
            
        Returns:
            是否成功
        """
        try:
            # 获取预测结果
            cursor = self.conn.execute('''
                SELECT id, prediction FROM prediction_history
                WHERE content_id = ? AND actual_result IS NULL
                ORDER BY predicted_at DESC LIMIT 1
            ''', (content_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"未找到内容ID={content_id}的预测记录")
                return False
            
            prediction_id, predicted = row
            
            # 判断是否正确
            is_correct = 1 if predicted == actual_smile else 0
            
            # 更新记录
            self.conn.execute('''
                UPDATE prediction_history
                SET actual_result = ?, actual_smile_count = ?, 
                    verified_at = ?, is_correct = ?
                WHERE id = ?
            ''', (actual_smile, smile_count, datetime.now(), is_correct, prediction_id))
            
            self.conn.commit()
            
            logger.info(f"记录真实结果: 预测={predicted}, 实际={actual_smile}, "
                       f"{'✓正确' if is_correct else '✗错误'}")
            
            # 如果预测错误，分析原因
            if not is_correct:
                self._analyze_error(prediction_id, predicted, actual_smile)
            
            # 触发模型优化
            self.optimize_model()
            
            return True
            
        except Exception as e:
            logger.error(f"记录真实结果失败: {e}")
            return False
    
    def _analyze_error(self, prediction_id: int, predicted: str, actual: str):
        """分析预测错误的原因"""
        try:
            # 获取预测详情
            cursor = self.conn.execute('''
                SELECT ph.*, mc.structured_data
                FROM prediction_history ph
                JOIN maoge_content mc ON ph.content_id = mc.id
                WHERE ph.id = ?
            ''', (prediction_id,))
            
            row = cursor.fetchone()
            if not row:
                return
            
            # 解析数据
            data = json.loads(row[13])  # structured_data字段
            
            # 分析错误类型
            error_type = self._classify_error(predicted, actual, data)
            
            # 生成分析报告
            analysis = self._generate_error_analysis(predicted, actual, data)
            
            # 保存错误案例
            self.conn.execute('''
                INSERT INTO error_cases (prediction_id, error_type, analysis, created_at)
                VALUES (?, ?, ?, ?)
            ''', (prediction_id, error_type, analysis, datetime.now()))
            
            self.conn.commit()
            
            logger.info(f"错误案例已记录: 类型={error_type}")
            
        except Exception as e:
            logger.error(f"分析错误失败: {e}")
    
    def _classify_error(self, predicted: str, actual: str, data: Dict) -> str:
        """分类错误类型"""
        if predicted == 'no_smile' and actual != 'no_smile':
            return 'false_negative'  # 漏报
        elif predicted != 'no_smile' and actual == 'no_smile':
            return 'false_positive'  # 误报
        elif predicted == 'buy_smile' and actual == 'sell_smile':
            return 'direction_error'  # 方向错误
        elif predicted == 'sell_smile' and actual == 'buy_smile':
            return 'direction_error'  # 方向错误
        else:
            return 'unknown'
    
    def _generate_error_analysis(self, predicted: str, actual: str, data: Dict) -> str:
        """生成错误分析报告"""
        analysis = []
        
        analysis.append(f"预测: {predicted}, 实际: {actual}")
        analysis.append(f"市场周期: {data.get('market_cycle')}")
        analysis.append(f"趋势判断: {data.get('trend_judgment')}")
        analysis.append(f"风险等级: {data.get('risk_assessment', {}).get('risk_level')}")
        analysis.append(f"信号强度: {data.get('confidence')}")
        
        # 分析可能的原因
        if predicted == 'no_smile' and actual != 'no_smile':
            analysis.append("可能原因: 阈值设置过高，或未能识别隐含信号")
        elif predicted != 'no_smile' and actual == 'no_smile':
            analysis.append("可能原因: 过度解读，或信号权重设置不当")
        elif predicted != actual:
            analysis.append("可能原因: 市场周期判断错误，或指标权重需要调整")
        
        return '\n'.join(analysis)
    
    def optimize_model(self):
        """优化预测模型"""
        try:
            # 获取所有已验证的预测记录
            cursor = self.conn.execute('''
                SELECT COUNT(*) FROM prediction_history
                WHERE actual_result IS NOT NULL
            ''')
            
            total_count = cursor.fetchone()[0]
            
            if total_count < 10:
                logger.info(f"样本数量不足({total_count}/10)，暂不优化模型")
                return
            
            # 计算准确率
            cursor = self.conn.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(is_correct) as correct,
                    AVG(confidence) as avg_confidence
                FROM prediction_history
                WHERE actual_result IS NOT NULL
            ''')
            
            row = cursor.fetchone()
            total, correct, avg_confidence = row
            accuracy = correct / total if total > 0 else 0
            
            logger.info(f"当前模型性能: 准确率={accuracy:.2%} ({correct}/{total}), "
                       f"平均置信度={avg_confidence:.2f}")
            
            # 保存性能记录
            self.conn.execute('''
                INSERT INTO model_performance (
                    model_version, total_predictions, correct_predictions,
                    accuracy, avg_confidence, evaluated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', ('v1.0', total, correct, accuracy, avg_confidence, datetime.now()))
            
            self.conn.commit()
            
            # 分析错误模式
            self._analyze_error_patterns()
            
            # 如果样本足够，训练机器学习模型
            if total >= 50:
                logger.info("样本数量充足，开始训练机器学习模型...")
                self._train_ml_model()
            
        except Exception as e:
            logger.error(f"优化模型失败: {e}")
    
    def _analyze_error_patterns(self):
        """分析错误模式"""
        try:
            # 统计各类错误的数量
            cursor = self.conn.execute('''
                SELECT error_type, COUNT(*) as count
                FROM error_cases
                GROUP BY error_type
                ORDER BY count DESC
            ''')
            
            error_stats = cursor.fetchall()
            
            if error_stats:
                logger.info("错误类型统计:")
                for error_type, count in error_stats:
                    logger.info(f"  {error_type}: {count}次")
            
            # 分析最近的错误案例
            cursor = self.conn.execute('''
                SELECT error_type, analysis
                FROM error_cases
                ORDER BY created_at DESC
                LIMIT 5
            ''')
            
            recent_errors = cursor.fetchall()
            
            if recent_errors:
                logger.info("最近的错误案例:")
                for i, (error_type, analysis) in enumerate(recent_errors, 1):
                    logger.info(f"\n案例{i} ({error_type}):")
                    logger.info(analysis)
            
        except Exception as e:
            logger.error(f"分析错误模式失败: {e}")
    
    def _train_ml_model(self):
        """训练机器学习模型"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report
            
            # 获取训练数据
            cursor = self.conn.execute('''
                SELECT ph.*, mc.structured_data
                FROM prediction_history ph
                JOIN maoge_content mc ON ph.content_id = mc.id
                WHERE ph.actual_result IS NOT NULL
            ''')
            
            records = cursor.fetchall()
            
            if len(records) < 50:
                logger.warning("训练数据不足")
                return
            
            # 准备特征和标签
            X = []
            y = []
            
            for record in records:
                data = json.loads(record[13])  # structured_data
                features = self._extract_features(data)
                label = record[8]  # actual_result
                
                X.append(features)
                y.append(label)
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # 评估模型
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            logger.info(f"机器学习模型训练完成:")
            logger.info(f"  训练集准确率: {train_score:.2%}")
            logger.info(f"  测试集准确率: {test_score:.2%}")
            
            # 输出分类报告
            y_pred = model.predict(X_test)
            report = classification_report(y_test, y_pred)
            logger.info(f"\n分类报告:\n{report}")
            
            # 保存模型
            self.model = model
            self._save_model()
            
        except ImportError:
            logger.warning("scikit-learn未安装，无法训练机器学习模型")
        except Exception as e:
            logger.error(f"训练机器学习模型失败: {e}")
    
    def _extract_features(self, data: Dict) -> List[float]:
        """从结构化数据中提取特征向量"""
        features = []
        
        # 市场周期特征 (one-hot编码)
        cycle = data.get('market_cycle', '未明确')
        features.append(1 if cycle == '买入期' else 0)
        features.append(1 if cycle == '持有期' else 0)
        features.append(1 if cycle == '减仓期' else 0)
        
        # 趋势判断特征 (one-hot编码)
        trend = data.get('trend_judgment', '未明确')
        features.append(1 if trend == '看涨' else 0)
        features.append(1 if trend == '看跌' else 0)
        features.append(1 if trend == '震荡' else 0)
        
        # 风险等级特征 (one-hot编码)
        risk = data.get('risk_assessment', {}).get('risk_level', '未明确')
        features.append(1 if risk == '低' else 0)
        features.append(1 if risk == '中' else 0)
        features.append(1 if risk == '高' else 0)
        
        # 信号强度特征 (one-hot编码)
        confidence = data.get('confidence', '弱')
        features.append(1 if confidence == '强' else 0)
        features.append(1 if confidence == '中' else 0)
        features.append(1 if confidence == '弱' else 0)
        
        # 情绪特征 (one-hot编码)
        sentiment = data.get('sentiment', '中性')
        features.append(1 if sentiment == '乐观' else 0)
        features.append(1 if sentiment == '悲观' else 0)
        
        # 操作建议特征
        suggestions = data.get('operation_suggestions', [])
        has_buy = any('建仓' in s.get('action', '') or '加仓' in s.get('action', '') 
                     for s in suggestions)
        has_sell = any('减仓' in s.get('action', '') or '清仓' in s.get('action', '') 
                      for s in suggestions)
        features.append(1 if has_buy else 0)
        features.append(1 if has_sell else 0)
        
        # 波动率特征
        indicators = data.get('key_indicators', {})
        volatility = indicators.get('gold_volatility')
        if volatility:
            try:
                vol_value = float(volatility)
                features.append(vol_value / 100)  # 归一化
            except ValueError:
                features.append(0)
        else:
            features.append(0)
        
        return features
    
    def _save_model(self):
        """保存模型"""
        if self.model is None:
            return
        
        try:
            model_path = '/home/ubuntu/maoge_signal_reader/data/prediction_model.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"模型已保存到: {model_path}")
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
    
    def load_model(self) -> bool:
        """加载模型"""
        try:
            model_path = '/home/ubuntu/maoge_signal_reader/data/prediction_model.pkl'
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("模型加载成功")
            return True
        except FileNotFoundError:
            logger.info("未找到已保存的模型")
            return False
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        try:
            stats = {}
            
            # 总预测数
            cursor = self.conn.execute('''
                SELECT COUNT(*) FROM prediction_history
            ''')
            stats['total_predictions'] = cursor.fetchone()[0]
            
            # 已验证数
            cursor = self.conn.execute('''
                SELECT COUNT(*) FROM prediction_history
                WHERE actual_result IS NOT NULL
            ''')
            stats['verified_predictions'] = cursor.fetchone()[0]
            
            # 准确率
            cursor = self.conn.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(is_correct) as correct
                FROM prediction_history
                WHERE actual_result IS NOT NULL
            ''')
            row = cursor.fetchone()
            if row[0] > 0:
                stats['accuracy'] = row[1] / row[0]
            else:
                stats['accuracy'] = 0
            
            # 各类预测的准确率
            for pred_type in ['buy_smile', 'sell_smile', 'no_smile']:
                cursor = self.conn.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(is_correct) as correct
                    FROM prediction_history
                    WHERE prediction = ? AND actual_result IS NOT NULL
                ''', (pred_type,))
                row = cursor.fetchone()
                if row[0] > 0:
                    stats[f'{pred_type}_accuracy'] = row[1] / row[0]
                else:
                    stats[f'{pred_type}_accuracy'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    # 测试代码
    optimizer = LearningOptimizer()
    
    # 测试记录预测
    test_prediction = {
        'prediction': 'buy_smile',
        'confidence': 0.85,
        'smile_count': 1.5,
        'buy_score': 6,
        'sell_score': 1
    }
    
    pred_id = optimizer.record_prediction(1, test_prediction)
    print(f"记录预测: ID={pred_id}")
    
    # 获取统计信息
    stats = optimizer.get_statistics()
    print("\n统计信息:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    optimizer.close()
