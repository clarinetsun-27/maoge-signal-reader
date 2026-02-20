#!/bin/bash
#
# 小鹅通监控系统更新脚本
# 用途：更新到每3分钟检查一次，仅在交易时间运行
#

set -e

echo "=========================================="
echo "小鹅通监控系统更新脚本"
echo "更新内容：每3分钟检查，仅交易时间运行"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用root用户运行此脚本${NC}"
    echo "使用: sudo bash $0"
    exit 1
fi

echo -e "${YELLOW}步骤1: 停止服务...${NC}"
systemctl stop xiaoe_monitor.service 2>/dev/null || echo "服务未运行"
echo -e "${GREEN}✅ 服务已停止${NC}"

echo -e "${YELLOW}步骤2: 安装新依赖...${NC}"
pip3 install chinese_calendar -q && echo -e "${GREEN}✅ chinese_calendar 安装成功${NC}" || echo -e "${YELLOW}⚠️  chinese_calendar 安装失败，将使用简单周末判断${NC}"

echo -e "${YELLOW}步骤3: 下载最新代码...${NC}"
cd /tmp
rm -rf maoge-signal-reader
git config --global http.version HTTP/1.1
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader
echo -e "${GREEN}✅ 代码下载完成${NC}"

echo -e "${YELLOW}步骤4: 备份旧文件...${NC}"
mkdir -p /root/backups
if [ -f "/root/maoge_advisor/xiaoe_monitor.py" ]; then
    cp /root/maoge_advisor/xiaoe_monitor.py /root/backups/xiaoe_monitor.py.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ 已备份旧文件${NC}"
else
    echo -e "${YELLOW}⚠️  未找到旧文件，跳过备份${NC}"
fi

echo -e "${YELLOW}步骤5: 复制新文件...${NC}"
cp xiaoe_monitor.py /root/maoge_advisor/
cp services/xiaoe_monitor.service /etc/systemd/system/
chmod +x /root/maoge_advisor/xiaoe_monitor.py
echo -e "${GREEN}✅ 文件复制完成${NC}"

echo -e "${YELLOW}步骤6: 重新加载服务配置...${NC}"
systemctl daemon-reload
echo -e "${GREEN}✅ 配置重新加载完成${NC}"

echo -e "${YELLOW}步骤7: 启动服务...${NC}"
systemctl start xiaoe_monitor.service
sleep 2
echo -e "${GREEN}✅ 服务已启动${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 更新完成！${NC}"
echo "=========================================="
echo ""
echo "📊 更新内容："
echo "  - 检查频率：每小时 → 每3分钟"
echo "  - 运行时间：24小时 → 仅交易日 09:30-15:00"
echo "  - 新增功能：自动识别节假日"
echo ""
echo "🔍 验证服务状态："
echo ""

# 验证服务状态
if systemctl is-active --quiet xiaoe_monitor.service; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
    echo ""
    echo "查看实时日志："
    echo "  journalctl -u xiaoe_monitor.service -f"
    echo ""
    echo "查看服务状态："
    echo "  systemctl status xiaoe_monitor.service"
    echo ""
    echo "预期日志输出："
    echo "  - 交易时间内：✅ 交易时间内，开始监控"
    echo "  - 非交易时间：⏸️  非交易时间，等待到 09:30:00"
    echo "  - 非交易日：⏸️  非交易日，等待到下一个工作日"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo ""
    echo "查看错误日志："
    echo "  journalctl -u xiaoe_monitor.service -n 50"
    echo ""
    echo "手动测试运行："
    echo "  cd /root/maoge_advisor"
    echo "  python3 xiaoe_monitor.py --shop-url \"https://店铺URL/\" --interval 180"
    exit 1
fi

echo ""
echo "=========================================="
