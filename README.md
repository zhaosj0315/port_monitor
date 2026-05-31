# Port Monitor

> 一款基于 Python Flask 的本地端口服务监控与防火墙快速配置工具。
> 
> A lightweight Python Flask utility for local port service monitoring and firewall rule management.

[English](#english) | [中文](#中文)

---

<a name="中文"></a>
## 中文

`Port Monitor` 旨在解决本地开发、微服务架构以及局域网运维中，多端口状态追踪不便和系统防火墙规则配置繁琐的痛点。

### 功能特性

- **端口状态实时监测**：支持自定义端口列表（如 Streamlit, FastAPI, Jupyter, Ollama 等），实时呈现通断状态。
- **进程与服务关联**：智能识别当前占用特定端口的进程 PID、进程名称及路径，并支持一键强杀（Kill）冲突进程。
- **简易防火墙管理**：为本地防火墙（支持 macOS `pfctl` 和 Linux `iptables`/`ufw` 探测）提供极简的开关与封禁/放行端口界面。
- **可视化 Web UI**：内置精美的自适应网页（Responsive Dashboard），支持移动端和桌面端全屏显示，方便挂载在监控副屏。
- **配置文件持久化**：自定义监控的端口列表与备注自动保存于 `ports.json` 中。

### 快速开始

1. **安装依赖**：
   ```bash
   pip install flask
   ```
2. **运行服务**：
   ```bash
   python port_monitor.py
   ```
   服务默认运行在 `http://127.0.0.1:8502`（或在 `port_monitor.py` 中配置的自定义端口）。

---

<a name="english"></a>
## English

`Port Monitor` is designed to simplify port state tracking and local firewall management for microservice developers and homelab administrators.

### Features

- **Real-time Port Telemetry**: Monitor the connection status of custom ports (e.g. Streamlit, FastAPI, Jupyter, Ollama) on a single responsive dashboard.
- **Process Binding Insights**: Auto-detect process name, PID, and executable path binding to a specific port, with one-click terminal kill support.
- **Firewall Integration**: A simplified interface for managing local firewall rule blocks and allows (supports macOS `pfctl` and Linux `ufw`/`iptables` wrappers).
- **Responsive Dashboard**: Beautiful web UI built with embedded styles, optimized for both desktop side-car screens and mobile devices.
- **Persistent Configuration**: Custom port lists and metadata are dynamically saved in `ports.json`.

### Quick Start

1. **Install Dependencies**:
   ```bash
   pip install flask
   ```
2. **Run Utility**:
   ```bash
   python port_monitor.py
   ```

---

## License

MIT License © 2025
