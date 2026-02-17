# 猫哥图文解读系统 (Maoge Signal Reader)

自动解读猫哥投资信号图文，预测笑脸，并通过持续学习不断优化准确率。

## 🎯 功能特性

- **自动OCR提取**: 使用智增增API提取图文中的文字内容
- **语义分析**: 深度理解猫哥的投资逻辑和市场判断
- **信号识别**: 自动识别买入/卖出信号
- **笑脸预测**: 预测猫哥将发布的笑脸类型和数量
- **持续学习**: 根据反馈不断优化模型
- **企业微信集成**: 自动推送分析结果和性能报告

## 📊 性能指标

- OCR准确率: 95%+
- 语义理解: 90%+
- 信号识别: 85%+
- 处理速度: 5秒/图
- API成本: $0.01/图

## 🎯 准确率目标

- **短期** (2-3个月): 70%
- **中期** (6-9个月): 80%
- **长期** (12-18个月): 85%+

## 🏗️ 系统架构

```
猫哥图文解读系统
├── modules/               # 核心模块
│   ├── ocr_extractor.py          # OCR文字提取
│   ├── semantic_analyzer.py      # 语义分析
│   ├── signal_analyzer.py        # 信号分析
│   └── learning_optimizer.py     # 学习优化
├── maoge_image_handler.py        # 图文处理器
├── wechat_image_receiver.py      # 企业微信接口
├── feedback_manager.py           # 反馈管理器
└── services/                     # systemd服务配置
    ├── maoge_signal_reader.service
    ├── maoge_daily_report.service
    └── maoge_weekly_report.service
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install openai requests watchdog flask schedule pillow
```

### 2. 配置环境变量

```bash
export OPENAI_API_KEY="your-api-key"
```

### 3. 部署到服务器

```bash
./deploy_to_server.sh
```

### 4. 启动服务

```bash
sudo systemctl start maoge_signal_reader.service
sudo systemctl start maoge_daily_report.service
sudo systemctl start maoge_weekly_report.service
```

## 📖 使用方法

### 方式1: 目录监控（推荐）

将猫哥图文保存到监控目录：
```bash
/root/maoge_advisor/maoge_images/
```

系统自动分析并推送结果到企业微信。

### 方式2: HTTP接口

```bash
curl -X POST http://服务器IP:8888/upload \
  -F "file=@maoge_image.png"
```

### 方式3: 命令行

```bash
python3 maoge_image_handler.py /path/to/image.png
```

## 📝 反馈笑脸

### 通过HTTP接口

```bash
curl -X POST http://服务器IP:8888/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": 1,
    "actual_smile": "buy_smile",
    "actual_count": 2
  }'
```

### 通过命令行

```bash
python3 maoge_image_handler.py \
  --feedback "1:buy_smile:2"
```

## 📊 性能报告

### 每日报告

```bash
python3 feedback_manager.py --action daily
```

### 每周报告

```bash
python3 feedback_manager.py --action weekly
```

## 🔧 管理命令

### 查看服务状态

```bash
sudo systemctl status maoge_signal_reader.service
```

### 查看日志

```bash
sudo journalctl -u maoge_signal_reader.service -f
```

### 重启服务

```bash
sudo systemctl restart maoge_signal_reader.service
```

## 📁 数据存储

- **数据库**: `/root/maoge_advisor/maoge_predictions.db`
- **图片存储**: `/root/maoge_advisor/maoge_images/`
- **日志**: `journalctl -u maoge_signal_reader.service`

## 🔐 安全说明

- 所有API密钥通过环境变量配置
- 数据库仅root用户可访问
- 企业微信Webhook需要配置白名单

## 📄 许可证

MIT License

## 👥 作者

Tommy Investment Advisor Team

## 🙏 致谢

感谢猫哥提供优质的投资分析内容！
