#!/bin/bash
# 猫哥图文解读系统部署脚本
# 部署到服务器 47.100.32.41

set -e

SERVER="47.100.32.41"
USER="admin"
REMOTE_DIR="/root/maoge_advisor"
LOCAL_DIR="/home/ubuntu/tommy_advisor"

echo "=========================================="
echo "猫哥图文解读系统部署脚本"
echo "=========================================="
echo ""

# 1. 检查SSH连接
echo "步骤 1/8: 检查服务器连接..."
if ssh -o ConnectTimeout=5 ${USER}@${SERVER} "echo 'SSH连接成功'" > /dev/null 2>&1; then
    echo "✅ 服务器连接正常"
else
    echo "❌ 无法连接到服务器 ${SERVER}"
    echo "请检查:"
    echo "  1. 服务器IP是否正确"
    echo "  2. SSH密钥是否配置"
    echo "  3. 网络连接是否正常"
    exit 1
fi

# 2. 备份现有系统
echo ""
echo "步骤 2/8: 备份现有系统..."
BACKUP_NAME="maoge_advisor_backup_$(date +%Y%m%d_%H%M%S)"
ssh ${USER}@${SERVER} "sudo mkdir -p /root/backups && sudo cp -r ${REMOTE_DIR} /root/backups/${BACKUP_NAME} 2>/dev/null || echo '无现有系统，跳过备份'"
echo "✅ 备份完成: /root/backups/${BACKUP_NAME}"

# 3. 创建目录结构
echo ""
echo "步骤 3/8: 创建目录结构..."
ssh ${USER}@${SERVER} "sudo mkdir -p ${REMOTE_DIR}/modules ${REMOTE_DIR}/maoge_images ${REMOTE_DIR}/logs"
echo "✅ 目录结构创建完成"

# 4. 上传核心模块
echo ""
echo "步骤 4/8: 上传核心模块..."

# 复制modules目录下的所有模块
scp ${LOCAL_DIR}/modules/*.py ${USER}@${SERVER}:/tmp/
ssh ${USER}@${SERVER} "sudo mv /tmp/*.py ${REMOTE_DIR}/modules/"

# 复制主要脚本
SCRIPTS=(
    "maoge_image_handler.py"
    "wechat_image_receiver.py"
    "feedback_manager.py"
)

for script in "${SCRIPTS[@]}"; do
    echo "  上传 ${script}..."
    scp ${LOCAL_DIR}/${script} ${USER}@${SERVER}:/tmp/
    ssh ${USER}@${SERVER} "sudo mv /tmp/${script} ${REMOTE_DIR}/ && sudo chmod +x ${REMOTE_DIR}/${script}"
done

echo "✅ 核心模块上传完成"

# 5. 上传systemd服务配置
echo ""
echo "步骤 5/8: 配置systemd服务..."

SERVICES=(
    "maoge_signal_reader.service"
    "maoge_daily_report.service"
    "maoge_weekly_report.service"
)

for service in "${SERVICES[@]}"; do
    echo "  配置 ${service}..."
    scp ${LOCAL_DIR}/${service} ${USER}@${SERVER}:/tmp/
    ssh ${USER}@${SERVER} "sudo mv /tmp/${service} /etc/systemd/system/"
done

ssh ${USER}@${SERVER} "sudo systemctl daemon-reload"
echo "✅ systemd服务配置完成"

# 6. 安装依赖
echo ""
echo "步骤 6/8: 安装Python依赖..."
ssh ${USER}@${SERVER} "sudo pip3 install -q openai requests watchdog flask schedule sqlite3 pillow || true"
echo "✅ 依赖安装完成"

# 7. 启动服务
echo ""
echo "步骤 7/8: 启动服务..."

for service in "${SERVICES[@]}"; do
    SERVICE_NAME=$(basename ${service})
    echo "  启动 ${SERVICE_NAME}..."
    ssh ${USER}@${SERVER} "sudo systemctl enable ${SERVICE_NAME} && sudo systemctl restart ${SERVICE_NAME}"
    
    # 检查服务状态
    sleep 2
    if ssh ${USER}@${SERVER} "sudo systemctl is-active ${SERVICE_NAME}" > /dev/null 2>&1; then
        echo "  ✅ ${SERVICE_NAME} 运行正常"
    else
        echo "  ⚠️ ${SERVICE_NAME} 启动失败，请检查日志"
    fi
done

echo "✅ 服务启动完成"

# 8. 验证部署
echo ""
echo "步骤 8/8: 验证部署..."

echo "  检查文件..."
ssh ${USER}@${SERVER} "sudo ls -lh ${REMOTE_DIR}/*.py" | head -5

echo ""
echo "  检查服务状态..."
ssh ${USER}@${SERVER} "sudo systemctl status maoge_signal_reader.service --no-pager -l" | head -10

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "服务状态:"
echo "  • 图文解读服务: maoge_signal_reader.service"
echo "  • 每日报告服务: maoge_daily_report.service"
echo "  • 每周报告服务: maoge_weekly_report.service"
echo ""
echo "使用方法:"
echo "  1. 将猫哥图文保存到: ${REMOTE_DIR}/maoge_images/"
echo "  2. 系统自动分析并推送结果到企业微信"
echo "  3. 猫哥发布笑脸后，反馈实际结果"
echo ""
echo "管理命令:"
echo "  查看日志: ssh ${USER}@${SERVER} 'sudo journalctl -u maoge_signal_reader.service -f'"
echo "  重启服务: ssh ${USER}@${SERVER} 'sudo systemctl restart maoge_signal_reader.service'"
echo "  停止服务: ssh ${USER}@${SERVER} 'sudo systemctl stop maoge_signal_reader.service'"
echo ""
echo "数据库位置: ${REMOTE_DIR}/maoge_predictions.db"
echo "图片存储: ${REMOTE_DIR}/maoge_images/"
echo ""
