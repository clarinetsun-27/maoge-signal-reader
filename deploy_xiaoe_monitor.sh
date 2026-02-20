#!/bin/bash
#
# 小鹅通监控系统部署脚本
# 用途：在服务器上一键部署小鹅通内容自动监控系统
#

set -e

echo "=========================================="
echo "小鹅通监控系统部署脚本"
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

echo -e "${YELLOW}步骤1: 安装依赖...${NC}"

# 安装Playwright
echo "安装Playwright..."
pip3 install playwright requests -q

# 安装Chromium浏览器
echo "安装Chromium浏览器..."
playwright install chromium
playwright install-deps chromium

echo -e "${GREEN}✅ 依赖安装完成${NC}"

echo -e "${YELLOW}步骤2: 从GitHub下载代码...${NC}"

# 下载代码
cd /tmp
rm -rf maoge-signal-reader
git clone https://github.com/clarinetsun-27/maoge-signal-reader.git
cd maoge-signal-reader

echo -e "${GREEN}✅ 代码下载完成${NC}"

echo -e "${YELLOW}步骤3: 复制文件到安装目录...${NC}"

# 复制文件
cp xiaoe_monitor.py /root/maoge_advisor/
chmod +x /root/maoge_advisor/xiaoe_monitor.py

# 创建数据目录
mkdir -p /root/maoge_advisor/xiaoe_data
mkdir -p /root/maoge_advisor/logs

echo -e "${GREEN}✅ 文件复制完成${NC}"

echo -e "${YELLOW}步骤4: 配置systemd服务...${NC}"

# 复制服务配置
cp services/xiaoe_monitor.service /etc/systemd/system/
systemctl daemon-reload

echo -e "${GREEN}✅ 服务配置完成${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}⚠️  重要提示：${NC}"
echo ""
echo "1. 首次使用需要手动登录小鹅通："
echo ""
echo "   cd /root/maoge_advisor"
echo "   python3 xiaoe_monitor.py --shop-url \"https://你的小鹅通店铺URL/\" --interval 3600"
echo ""
echo "   在打开的浏览器中完成登录（微信扫码或手机验证码）"
echo "   登录成功后按 Ctrl+C 退出"
echo ""
echo "2. 修改服务配置中的店铺URL："
echo ""
echo "   nano /etc/systemd/system/xiaoe_monitor.service"
echo ""
echo "   修改 ExecStart 行中的 --shop-url 参数"
echo ""
echo "3. 启动服务："
echo ""
echo "   systemctl start xiaoe_monitor.service"
echo "   systemctl enable xiaoe_monitor.service"
echo ""
echo "4. 查看服务状态："
echo ""
echo "   systemctl status xiaoe_monitor.service"
echo "   journalctl -u xiaoe_monitor.service -f"
echo ""
echo "=========================================="
