#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股 Level-2 高频行情数据接入示例 · 毫秒级时间戳与端到端延迟计算
-----------------------------------------------------------------
功能特点：
1. 逐笔成交 (Tick Trade) / 逐笔委托与撤单 (Tick Order) / 千档深度 (1000-Level Depth)
2. 毫秒级交易所撮合时间戳 (time: YYYY-MM-DD HH:MM:SS.mmm)
3. 网关物理接收时间戳 (receivedAt: ISO-8601) 测算高频端到端毫秒延迟

依赖安装：
    pip install websocket-client
"""

import json
import time
from datetime import datetime
import websocket

# 获取测试 Token 请联系微信: luffy953 或 LUFFY9531 (添加备注: GitHub/量化)
TOKEN = "YOUR_TRIAL_TOKEN"
WS_ENDPOINT = f"wss://quote.stream.example.com/ws/l2?token={TOKEN}"


def parse_latency_ms(data, recv_local_ts):
    """根据网关物理接收时间戳计算端到端延迟 (毫秒)"""
    if "receivedAt" not in data:
        return None
    try:
        gw_dt = datetime.fromisoformat(data["receivedAt"])
        gw_ts = gw_dt.timestamp()
        return (recv_local_ts - gw_ts) * 1000.0
    except Exception:
        return None


def on_message(ws, message):
    recv_local_ts = time.time()  # 客户端本地物理接收时间
    try:
        data = json.loads(message)
    except Exception as e:
        print(f"解析 JSON 失败: {e}")
        return

    ch = data.get("channel")
    symbol = data.get("symbol", "--")
    match_time = data.get("time", "--")  # 撮合毫秒时间戳，例如 "2026-09-23 14:58:22.480"
    latency_ms = parse_latency_ms(data, recv_local_ts)
    lat_str = f"延迟: {latency_ms:4.1f}ms" if latency_ms is not None else "延迟: --ms"

    if ch == "l2.trade":
        price = data.get("price", 0.0)
        vol = data.get("volumeShares", 0)
        side = data.get("side", "N")
        buy_id = data.get("buyOrderId", 0)
        sell_id = data.get("sellOrderId", 0)
        side_label = "主动买" if side == "B" else ("主动卖" if side == "S" else "未知")
        print(f"[{match_time}] 逐笔成交 | {symbol:<9} | 价格: {price:>8.2f} | 数量: {vol:>6}股 | 方向: {side_label} | 买单: {buy_id:<8} 卖单: {sell_id:<8} | {lat_str}")

    elif ch == "l2.order":
        order_type = data.get("orderType", "--")
        price = data.get("price", 0.0)
        vol = data.get("volumeShares", 0)
        order_id = data.get("orderId", 0)
        type_str = "买入" if order_type == "BUY" else ("卖出" if order_type == "SELL" else "撤单")
        print(f"[{match_time}] 逐笔委托 | {symbol:<9} | 类型: {type_str:<4} | 价格: {price:>8.2f} | 数量: {vol:>6}股 | 单号: {order_id:<8} | {lat_str}")

    elif ch == "l2.depth":
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        b1_str = f"{bids[0]['price']:.2f}({bids[0]['volume']}股)" if bids else "--"
        a1_str = f"{asks[0]['price']:.2f}({asks[0]['volume']}股)" if asks else "--"
        print(f"[{match_time}] 千档盘口 | {symbol:<9} | 买一: {b1_str:<16} 卖一: {a1_str:<16} | 深度: {len(bids)}x{len(asks)}档 | {lat_str}")


def on_open(ws):
    print(">>> [WebSocket] 连接建立成功，开始订阅高精毫秒级行情流...")
    # 订阅示例：贵州茅台(沪主板)、平安银行(深主板)、宁德时代(创业板)
    sub_payload = {
        "action": "subscribe",
        "symbols": ["600519.SH", "000001.SZ", "300750.SZ"],
        "channels": ["l2.trade", "l2.order", "l2.depth"]
    }
    ws.send(json.dumps(sub_payload))
    print(f">>> [WebSocket] 已发送订阅请求: {json.dumps(sub_payload, ensure_ascii=False)}")


def on_error(ws, error):
    print(f">>> [WebSocket] 发生异常: {error}")


def on_close(ws, close_status_code, close_msg):
    print(f">>> [WebSocket] 连接关闭: code={close_status_code}, msg={close_msg}")


if __name__ == "__main__":
    print("=" * 80)
    print("A股 Level-2 高频数据流接收客户端启动 (包含毫秒撮合时间戳与物理延迟测算)")
    print("=" * 80)
    ws = websocket.WebSocketApp(
        WS_ENDPOINT,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
