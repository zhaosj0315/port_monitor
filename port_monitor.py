import socket
import subprocess
import os
import json
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/Desktop/port_monitor/ports.json")

# 默认监控端口（带备注）
DEFAULT_PORTS = [
    {"port": 8501, "remark": "Streamlit主服务"},
    {"port": 8502, "remark": "API服务"},
    {"port": 8899, "remark": "备用端口"},
    {"port": 9000, "remark": "测试端口"},
    {"port": 10001, "remark": "自定义"}
]

HTML = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>端口服务监控</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Arial', sans-serif;
            background: linear-gradient(120deg, #e0e7ff 0%, #f8fafc 100%);
            margin: 0;
            min-height: 100vh;
        }
        .container {
            width: 98vw;
            max-width: 100vw;
            margin: 24px auto 0 auto;
            background: rgba(255,255,255,0.95);
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(60,60,120,0.06);
            padding: 24px 2vw 24px 2vw;
        }
        h2 {
            text-align: center;
            font-size: 2.4em;
            letter-spacing: 2px;
            color: #3b3b6d;
            margin-bottom: 32px;
        }
        .scan-section {
            margin-bottom: 18px;
            background: #e3e8ff;
            border-radius: 12px;
            padding: 18px 18px 10px 18px;
        }
        .scan-section h3 {
            margin: 0 0 8px 0;
            font-size: 1.2em;
            color: #4b4b7d;
        }
        .scan-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .scan-item {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(60,60,120,0.08);
            padding: 8px 14px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
        }
        .scan-item form { margin: 0; }
        .scan-item input[type="text"] {
            margin-left: 8px;
            padding: 2px 6px;
            border-radius: 6px;
            border: 1px solid #bfcfff;
            font-size: 1em;
            width: 80px;
        }
        .scan-item button {
            margin-left: 8px;
            padding: 4px 10px;
            font-size: 1em;
            border-radius: 6px;
            border: none;
            background: linear-gradient(90deg, #667eea 0%, #5a67d8 100%);
            color: #fff;
            cursor: pointer;
        }
        form[method="post"] input[type="number"], form[method="post"] input[type="text"] {
            font-size: 1.1em;
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid #bfcfff;
            margin-right: 8px;
        }
        form[method="post"] button {
            font-size: 1.1em;
            padding: 8px 18px;
            border-radius: 8px;
            border: none;
            background: linear-gradient(90deg, #667eea 0%, #5a67d8 100%);
            color: #fff;
            cursor: pointer;
            margin-right: 6px;
            transition: background 0.2s;
        }
        form[method="post"] button:hover {
            background: linear-gradient(90deg, #5a67d8 0%, #667eea 100%);
        }
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 24px;
            font-size: 1.15em;
            background: #f4f7ff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(60,60,120,0.06);
        }
        th, td {
            padding: 16px 12px;
            text-align: center;
        }
        th {
            background: #e3e8ff;
            color: #3b3b6d;
            font-weight: 600;
            font-size: 1.1em;
        }
        tr:nth-child(even) { background: #f8fafc; }
        tr:nth-child(odd) { background: #f4f7ff; }
        .open {
            color: #22c55e;
            font-weight: bold;
            font-size: 1.1em;
        }
        .closed {
            color: #ef4444;
            font-weight: bold;
            font-size: 1.1em;
        }
        .remark-form input[type="text"] {
            width: 120px;
            font-size: 1em;
            padding: 4px 8px;
            border-radius: 6px;
            border: 1px solid #bfcfff;
        }
        .remark-form button {
            padding: 4px 10px;
            font-size: 1em;
        }
        @media (max-width: 600px) {
            .container { padding: 12px 2vw; }
            table, th, td { font-size: 1em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>端口服务监控</h2>
        <div class="scan-section">
            <h3>本机所有开放端口（可一键加入监控）</h3>
            <div class="scan-list">
                {% for port in new_ports %}
                <div class="scan-item">
                    <form method="post" action="/add">
                        <input type="hidden" name="port" value="{{ port }}">
                        <span>{{ port }}</span>
                        <input type="text" name="remark" placeholder="备注/服务名">
                        <button type="submit">加入监控</button>
                    </form>
                </div>
                {% endfor %}
                {% if new_ports|length == 0 %}
                <span style="color:#888;">暂无未监控的开放端口</span>
                {% endif %}
            </div>
        </div>
        <div class="scan-section">
            <h3>所有被防火墙禁用的端口</h3>
            <div class="scan-list">
                {% for port in blocked_ports %}
                <div class="scan-item">
                    <span>{{ port }}</span>
                </div>
                {% endfor %}
                {% if blocked_ports|length == 0 %}
                <span style="color:#888;">暂无被防火墙禁用的端口</span>
                {% endif %}
            </div>
        </div>
        <form method="post" action="/add" style="text-align:center; margin-bottom: 12px;">
            <input type="number" name="port" placeholder="新增端口" required>
            <input type="text" name="remark" placeholder="备注/服务名" style="width:140px;">
            <button type="submit">添加端口</button>
        </form>
        <table>
            <tr><th>端口</th><th>状态</th><th>服务名</th><th>备注</th><th>防火墙</th><th>操作</th></tr>
            {% for port, status, service, remark, blocked in ports %}
            <tr>
                <td>{{ port }}</td>
                <td>{% if blocked %}<span style="color:#ef4444;font-weight:bold;">已禁用</span>{% else %}<span style="color:#22c55e;font-weight:bold;">已放行</span>{% endif %}</td>
                <td>{{ service }}</td>
                <td>
                    <form method="post" action="/edit_remark" class="remark-form" style="display:inline;">
                        <input type="hidden" name="port" value="{{ port }}">
                        <input type="text" name="remark" value="{{ remark }}" placeholder="备注/服务名">
                        <button type="submit">保存</button>
                    </form>
                </td>
                <td>
                    <div style="display:flex; gap:8px; justify-content:center; align-items:center;">
                        {% if not blocked %}
                        <form method="post" action="/close" style="display:inline">
                            <input type="hidden" name="port" value="{{ port }}">
                            <button type="submit" onclick="setTimeout(function(){location.reload();}, 800)">禁用端口</button>
                        </form>
                        {% else %}
                        <form method="post" action="/open" style="display:inline">
                            <input type="hidden" name="port" value="{{ port }}">
                            <button type="submit" onclick="setTimeout(function(){location.reload();}, 800)">放行端口</button>
                        </form>
                        {% endif %}
                    </div>
                </td>
                <td>
                    <form method="post" action="/delete" style="display:inline">
                        <input type="hidden" name="port" value="{{ port }}">
                        <button type="submit">删除</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
        <p style="text-align:center; margin-top:18px; color:#888;">刷新页面可查看最新状态。</p>
    </div>
</body>
</html>
'''





def load_ports():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            # 兼容老格式（int）
            ports = []
            for p in data:
                if isinstance(p, int):
                    ports.append({"port": p, "remark": ""})
                else:
                    ports.append(p)
            return ports
    return DEFAULT_PORTS.copy()

def save_ports(ports):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(ports, f)

def check_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except:
        return False

def get_service_name(port):
    try:
        out = subprocess.check_output(["lsof", "-iTCP:%d" % port, "-sTCP:LISTEN"], text=True)
        for line in out.splitlines()[1:]:
            return line.split()[0]
    except:
        return "-"

def ensure_pf_include():
    pf_main = "/etc/pf.conf"
    pf_custom = "/etc/pf.ports_block.conf"
    include_line = f'include "{pf_custom}"\n'
    # 确保自定义规则文件存在
    if not os.path.exists(pf_custom):
        with open(pf_custom, "w") as f:
            pass
    # 检查主配置是否已包含
    with open(pf_main, "r") as f:
        lines = f.readlines()
    if not any(pf_custom in l for l in lines):
        with open(pf_main, "a") as f:
            f.write("\n" + include_line)

def pf_block_port(port):
    # 添加pfctl规则，阻止端口入站
    rule = f"block drop in proto tcp from any to any port {port}"
    pf_conf = "/etc/pf.ports_block.conf"
    ensure_pf_include()
    with open(pf_conf, "a") as f:
        f.write(rule + "\n")
    subprocess.run(["sudo", "pfctl", "-f", "/etc/pf.conf"])
    subprocess.run(["sudo", "pfctl", "-e"])  # 启用pfctl

def pf_unblock_port(port):
    # 移除pfctl规则，恢复端口访问
    pf_conf = "/etc/pf.ports_block.conf"
    ensure_pf_include()
    if not os.path.exists(pf_conf):
        return
    with open(pf_conf, "r") as f:
        lines = f.readlines()
    lines = [l for l in lines if f"port {port}" not in l]
    with open(pf_conf, "w") as f:
        f.writelines(lines)
    subprocess.run(["sudo", "pfctl", "-f", "/etc/pf.conf"])

def kill_port_process(port):
    try:
        out = subprocess.check_output(["lsof", "-tiTCP:%d" % port, "-sTCP:LISTEN"], text=True)
        for pid in out.strip().splitlines():
            subprocess.run(["kill", "-9", pid])
    except Exception as e:
        pass

def scan_open_ports():
    # 扫描本机所有监听的TCP端口
    try:
        out = subprocess.check_output(["lsof", "-iTCP", "-sTCP:LISTEN", "-Pn"], text=True)
        ports = set()
        for line in out.splitlines()[1:]:
            parts = line.split()
            for p in parts:
                if p.startswith("TCP") and ":" in p:
                    port = int(p.split(":")[-1])
                    ports.add(port)
        return sorted(list(ports))
    except Exception as e:
        return []

def pf_is_blocked(port):
    pf_conf = "/etc/pf.ports_block.conf"
    if not os.path.exists(pf_conf):
        return False
    with open(pf_conf, "r") as f:
        for line in f:
            if f"port {port}" in line:
                return True
    return False

@app.route("/", methods=["GET"])
def index():
    ports = load_ports()
    port_status = [(p["port"], check_port(p["port"]), get_service_name(p["port"]), p.get("remark", ""), pf_is_blocked(p["port"])) for p in ports]
    # 扫描所有开放端口
    scanned_ports = scan_open_ports()
    # 过滤掉已在监控列表的端口
    monitored_ports = set(p["port"] for p in ports)
    new_ports = [p for p in scanned_ports if p not in monitored_ports]
    # 新增：扫描所有被pf禁用的端口
    pf_conf = "/etc/pf.ports_block.conf"
    blocked_ports = []
    if os.path.exists(pf_conf):
        with open(pf_conf, "r") as f:
            for line in f:
                if "port " in line:
                    try:
                        port = int(line.split("port ")[-1].strip())
                        blocked_ports.append(port)
                    except:
                        pass
    return render_template_string(HTML, ports=port_status, new_ports=new_ports, blocked_ports=blocked_ports)

@app.route("/add", methods=["POST"])
def add_port():
    port = int(request.form["port"])
    remark = request.form.get("remark", "")
    ports = load_ports()
    if not any(p["port"] == port for p in ports):
        ports.append({"port": port, "remark": remark})
        save_ports(ports)
    return redirect(url_for('index'))

@app.route("/delete", methods=["POST"])
def delete_port():
    port = int(request.form["port"])
    ports = load_ports()
    ports = [p for p in ports if p["port"] != port]
    save_ports(ports)
    return redirect(url_for('index'))

@app.route("/close", methods=["POST"])
def close_port():
    port = int(request.form["port"])
    pf_block_port(port)
    return redirect(url_for('index'))

@app.route("/open", methods=["POST"])
def open_port():
    port = int(request.form["port"])
    pf_unblock_port(port)
    return redirect(url_for('index'))

@app.route("/edit_remark", methods=["POST"])
def edit_remark():
    port = int(request.form["port"])
    remark = request.form.get("remark", "")
    ports = load_ports()
    for p in ports:
        if p["port"] == port:
            p["remark"] = remark
    save_ports(ports)
    return redirect(url_for('index'))

if __name__ == "__main__":
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    app.run(host="0.0.0.0", port=5005, debug=True)
