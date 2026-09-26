# port_monitor

本机端口有没有进程在听。页面只绑 `127.0.0.1:5005`，默认不改防火墙。

A localhost page that shows whether a TCP port has a listener. It binds `127.0.0.1:5005` and does not change the firewall unless you opt in.

## 跑起来

```bash
pip install flask
python port_monitor.py
```

浏览器打开 <http://127.0.0.1:5005>。

换端口：

```bash
PORT_MONITOR_PORT=5055 python port_monitor.py
```

监控名单在同目录 `ports.json`。页面上半部还会列出当前没在名单里、但本机正在听的 TCP 端口，可以补进名单。

## 页面上两列

| 列 | 含义 |
| --- | --- |
| 在听 / 没人听 | 对 `127.0.0.1` 做一次 0.5 秒的 TCP 连接 |
| 服务名 | `lsof -iTCP:<端口> -sTCP:LISTEN` 的进程名。没有 `lsof` 时显示 `-` |

这个仓库不杀进程，也不探测 Linux 的 `iptables` / `ufw`。

## 防火墙

「禁用端口 / 放行端口」默认不出现。那两条路径会改 `/etc/pf.conf`，并执行 `sudo pfctl -f /etc/pf.conf` 和 `sudo pfctl -e`。需要时再开：

```bash
PORT_MONITOR_ALLOW_PF=1 python port_monitor.py
```

没开这个环境变量时，`POST /close` 和 `POST /open` 返回 403，不会写系统文件。

`/logs/<端口>` 会为该端口启动 `sudo tcpdump`。没配免密 sudo 时，日志页连不上，端口名单页面不受影响。

## License

MIT. See [LICENSE](LICENSE).
