#!/bin/bash
# 部署小鹅通监控更新脚本

set -e

SERVER="admin@47.100.32.41"
REMOTE_DIR="/root/maoge_advisor"

echo "=========================================="
echo "部署小鹅通监控系统更新"
echo "=========================================="

# 1. 备份当前版本
echo ""
echo "[1/5] 备份当前版本..."
ssh $SERVER "sudo cp $REMOTE_DIR/xiaoe_monitor.py $REMOTE_DIR/xiaoe_monitor.py.backup.\$(date +%Y%m%d_%H%M%S) 2>/dev/null || true"

# 2. 上传更新的文件
echo ""
echo "[2/5] 上传更新的文件..."
scp xiaoe_monitor.py $SERVER:/tmp/
scp xiaoe_login_helper.py $SERVER:/tmp/
scp XIAOE_LOGIN_SETUP.md $SERVER:/tmp/

# 3. 部署文件到目标目录
echo ""
echo "[3/5] 部署文件..."
ssh $SERVER "sudo mv /tmp/xiaoe_monitor.py $REMOTE_DIR/"
ssh $SERVER "sudo mv /tmp/xiaoe_login_helper.py $REMOTE_DIR/"
ssh $SERVER "sudo mv /tmp/XIAOE_LOGIN_SETUP.md $REMOTE_DIR/"

# 4. 设置权限
echo ""
echo "[4/5] 设置文件权限..."
ssh $SERVER "sudo chmod 755 $REMOTE_DIR/xiaoe_monitor.py"
ssh $SERVER "sudo chmod 755 $REMOTE_DIR/xiaoe_login_helper.py"
ssh $SERVER "sudo chmod 644 $REMOTE_DIR/XIAOE_LOGIN_SETUP.md"

# 5. 重启服务
echo ""
echo "[5/5] 重启xiaoe_monitor服务..."
ssh $SERVER "sudo systemctl restart xiaoe_monitor.service"

# 等待服务启动
sleep 3

# 检查服务状态
echo ""
echo "=========================================="
echo "服务状态："
echo "=========================================="
ssh $SERVER "sudo systemctl status xiaoe_monitor.service --no-pager -l"

echo ""
echo "=========================================="
echo "最新日志："
echo "=========================================="
ssh $SERVER "sudo tail -20 /root/maoge_advisor/logs/xiaoe_monitor.log"

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 在本地电脑运行: python xiaoe_login_helper.py"
echo "2. 完成登录并保存凭证"
echo "3. 上传凭证: scp xiaoe_auth.json $SERVER:/tmp/"
echo "4. 部署凭证: ssh $SERVER 'sudo mv /tmp/xiaoe_auth.json $REMOTE_DIR/xiaoe_data/'"
echo "5. 重启服务: ssh $SERVER 'sudo systemctl restart xiaoe_monitor.service'"
echo ""

