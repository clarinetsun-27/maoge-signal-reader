#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
笑脸反馈和性能评估管理器
提供完整的反馈收集、性能评估和周报生成功能

功能：
1. 笑脸反馈收集（企业微信交互）
2. 每日性能统计
3. 每周性能评估报告
4. 模型优化建议
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from maoge_image_handler import MaogeImageHandler, send_wechat_message, MaogeConfig

# 配置日志
logger = logging.getLogger('feedback_manager')


# ==================== 反馈管理器 ====================

class FeedbackManager:
    """反馈和性能评估管理器"""
    
    def __init__(self, db_path=None):
        """
        初始化
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path or MaogeConfig.DB_PATH
        self.handler = MaogeImageHandler()
        
        logger.info(f"反馈管理器初始化完成，数据库: {self.db_path}")
    
    def collect_feedback_interactive(self):
        """
        交互式收集反馈
        从企业微信或命令行收集笑脸反馈
        """
        # 获取待反馈的预测
        pending = self._get_pending_feedbacks()
        
        if not pending:
            msg = "✅ 暂无待反馈的预测记录"
            print(msg)
            send_wechat_message(msg)
            return
        
        # 格式化待反馈列表
        msg = f"📋 待反馈预测列表 ({len(pending)}条)\n\n"
        
        for i, record in enumerate(pending[:10], 1):  # 最多显示10条
            msg += f"{i}. ID:{record['id']} | {record['date']} | 预测:{record['predicted_smile']}\n"
        
        if len(pending) > 10:
            msg += f"\n...还有{len(pending)-10}条待反馈\n"
        
        msg += "\n💡 请使用以下格式反馈:\n"
        msg += "ID:实际笑脸:数量\n"
        msg += "例如: 1:buy_smile:2"
        
        print(msg)
        send_wechat_message(msg)
        
        return pending
    
    def _get_pending_feedbacks(self, days=30):
        """
        获取待反馈的预测记录
        
        Args:
            days: 查询最近多少天
        
        Returns:
            list: 待反馈记录列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询待反馈记录
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT id, date, predicted_smile, confidence, predicted_count
                FROM predictions
                WHERE actual_smile IS NULL
                AND date >= ?
                ORDER BY date DESC
            """, (since_date,))
            
            records = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return records
            
        except Exception as e:
            logger.error(f"查询待反馈记录异常: {e}", exc_info=True)
            return []
    
    def batch_feedback(self, feedbacks):
        """
        批量反馈
        
        Args:
            feedbacks: 反馈列表，格式 [(id, actual_smile, actual_count), ...]
        
        Returns:
            dict: 反馈结果统计
        """
        success_count = 0
        fail_count = 0
        
        for prediction_id, actual_smile, actual_count in feedbacks:
            try:
                success = self.handler.save_feedback(
                    prediction_id=prediction_id,
                    actual_smile=actual_smile,
                    actual_count=actual_count
                )
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"保存反馈异常: ID={prediction_id}, {e}")
                fail_count += 1
        
        # 发送反馈结果
        msg = f"""📝 批量反馈完成

✅ 成功: {success_count}条
❌ 失败: {fail_count}条

系统已根据反馈优化模型。"""
        
        send_wechat_message(msg)
        
        return {
            'success': success_count,
            'fail': fail_count,
            'total': success_count + fail_count
        }
    
    def generate_daily_report(self, date=None):
        """
        生成每日性能报告
        
        Args:
            date: 日期（YYYY-MM-DD），默认为昨天
        
        Returns:
            str: 报告内容
        """
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询当天的预测和反馈
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN actual_smile IS NOT NULL THEN 1 ELSE 0 END) as feedback_count,
                    SUM(CASE WHEN predicted_smile = actual_smile THEN 1 ELSE 0 END) as correct_count,
                    AVG(confidence) as avg_confidence
                FROM predictions
                WHERE date = ?
            """, (date,))
            
            stats = dict(cursor.fetchone())
            
            conn.close()
            
            # 计算准确率
            if stats['feedback_count'] and stats['feedback_count'] > 0:
                accuracy = stats['correct_count'] / stats['feedback_count'] * 100
            else:
                accuracy = 0
            
            # 生成报告
            report = f"""📊 每日性能报告 - {date}

📈 预测统计:
• 总预测数: {stats['total']}
• 已反馈数: {stats['feedback_count']}
• 预测正确: {stats['correct_count']}
• 平均置信度: {stats['avg_confidence']:.1%}

🎯 准确率: {accuracy:.1f}%

"""
            
            if stats['feedback_count'] == 0:
                report += "⚠️ 今日暂无反馈数据\n"
            elif accuracy >= 80:
                report += "🎉 表现优秀！\n"
            elif accuracy >= 60:
                report += "👍 表现良好\n"
            else:
                report += "⚠️ 需要改进\n"
            
            return report
            
        except Exception as e:
            logger.error(f"生成每日报告异常: {e}", exc_info=True)
            return f"生成每日报告失败: {e}"
    
    def generate_weekly_report(self, end_date=None):
        """
        生成每周性能评估报告
        
        Args:
            end_date: 结束日期（YYYY-MM-DD），默认为昨天
        
        Returns:
            str: 报告内容
        """
        if not end_date:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=6)).strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询本周的预测和反馈
            cursor.execute("""
                SELECT 
                    date,
                    predicted_smile,
                    actual_smile,
                    confidence,
                    predicted_count,
                    actual_count
                FROM predictions
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            """, (start_date, end_date))
            
            records = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            # 统计分析
            total = len(records)
            feedback_records = [r for r in records if r['actual_smile'] is not None]
            feedback_count = len(feedback_records)
            
            if feedback_count > 0:
                correct_count = sum(1 for r in feedback_records if r['predicted_smile'] == r['actual_smile'])
                accuracy = correct_count / feedback_count * 100
                avg_confidence = sum(r['confidence'] for r in records) / total
                
                # 按类型统计
                type_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
                for r in feedback_records:
                    predicted = r['predicted_smile']
                    type_stats[predicted]['total'] += 1
                    if r['predicted_smile'] == r['actual_smile']:
                        type_stats[predicted]['correct'] += 1
                
            else:
                correct_count = 0
                accuracy = 0
                avg_confidence = 0
                type_stats = {}
            
            # 生成报告
            report = f"""📊 每周性能评估报告
📅 {start_date} 至 {end_date}

━━━━━━━━━━━━━━━━━━━━━━

📈 总体统计:
• 总预测数: {total}
• 已反馈数: {feedback_count}
• 预测正确: {correct_count}
• 反馈率: {feedback_count/total*100 if total > 0 else 0:.1f}%

🎯 准确率: {accuracy:.1f}%
📊 平均置信度: {avg_confidence:.1%}

━━━━━━━━━━━━━━━━━━━━━━

📋 分类统计:
"""
            
            for smile_type, stats in type_stats.items():
                type_accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
                report += f"\n{smile_type}:\n"
                report += f"  预测: {stats['total']}次\n"
                report += f"  正确: {stats['correct']}次\n"
                report += f"  准确率: {type_accuracy:.1f}%\n"
            
            report += "\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # 评估和建议
            if feedback_count == 0:
                report += "⚠️ 本周暂无反馈数据，请及时反馈以优化模型。\n"
            elif accuracy >= 80:
                report += "🎉 本周表现优秀！继续保持！\n"
                report += "💡 建议: 继续积累数据，提升置信度\n"
            elif accuracy >= 60:
                report += "👍 本周表现良好，有提升空间\n"
                report += "💡 建议: 分析错误案例，优化特征提取\n"
            else:
                report += "⚠️ 本周表现需要改进\n"
                report += "💡 建议:\n"
                report += "  1. 检查OCR和语义分析质量\n"
                report += "  2. 增加训练样本数量\n"
                report += "  3. 调整模型参数\n"
            
            # 进度评估
            report += f"\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            report += "🎯 目标进度:\n"
            
            if accuracy >= 85:
                report += "✅ 已达到长期目标（85%+）\n"
            elif accuracy >= 80:
                report += "✅ 已达到中期目标（80%）\n"
                report += "📈 距离长期目标还差 {:.1f}%\n".format(85 - accuracy)
            elif accuracy >= 70:
                report += "✅ 已达到短期目标（70%）\n"
                report += "📈 距离中期目标还差 {:.1f}%\n".format(80 - accuracy)
            else:
                report += "📈 距离短期目标还差 {:.1f}%\n".format(70 - accuracy)
            
            return report
            
        except Exception as e:
            logger.error(f"生成周报异常: {e}", exc_info=True)
            return f"生成周报失败: {e}"
    
    def send_daily_report(self, date=None):
        """发送每日报告到企业微信"""
        report = self.generate_daily_report(date)
        send_wechat_message(report)
        logger.info(f"每日报告已发送: {date}")
        return report
    
    def send_weekly_report(self, end_date=None):
        """发送周报到企业微信"""
        report = self.generate_weekly_report(end_date)
        send_wechat_message(report)
        logger.info(f"周报已发送: {end_date}")
        return report


# ==================== 定时任务 ====================

def schedule_daily_report():
    """定时发送每日报告（每天早上9点）"""
    import schedule
    import time
    
    manager = FeedbackManager()
    
    def job():
        logger.info("执行每日报告任务...")
        manager.send_daily_report()
    
    # 每天9:00执行
    schedule.every().day.at("09:00").do(job)
    
    logger.info("每日报告定时任务已启动（每天9:00）")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


def schedule_weekly_report():
    """定时发送周报（每周一早上9点）"""
    import schedule
    import time
    
    manager = FeedbackManager()
    
    def job():
        logger.info("执行周报任务...")
        manager.send_weekly_report()
    
    # 每周一9:00执行
    schedule.every().monday.at("09:00").do(job)
    
    logger.info("周报定时任务已启动（每周一9:00）")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


# ==================== 命令行接口 ====================

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='笑脸反馈和性能评估管理器')
    parser.add_argument('--action', choices=['pending', 'daily', 'weekly', 'schedule-daily', 'schedule-weekly'],
                       required=True, help='操作类型')
    parser.add_argument('--date', help='日期（YYYY-MM-DD）')
    
    args = parser.parse_args()
    
    manager = FeedbackManager()
    
    if args.action == 'pending':
        # 显示待反馈列表
        manager.collect_feedback_interactive()
        
    elif args.action == 'daily':
        # 生成并发送每日报告
        manager.send_daily_report(args.date)
        
    elif args.action == 'weekly':
        # 生成并发送周报
        manager.send_weekly_report(args.date)
        
    elif args.action == 'schedule-daily':
        # 启动每日报告定时任务
        schedule_daily_report()
        
    elif args.action == 'schedule-weekly':
        # 启动周报定时任务
        schedule_weekly_report()


if __name__ == "__main__":
    main()
