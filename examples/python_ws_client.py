"""
A-Share Level-2 WebSocket Client Demo
-------------------------------------
用于演示如何订阅 A股 Level-2 逐笔成交、逐笔委托与千档盘口数据。
获取测试 Token 与历史高频回测数据，请联系微信: luffy953 (备注: GitHub/量化)
"""

import json
import time
import websocket

# 测试凭证与接入网关地址
TRIAL_TOKEN = "YOUR_TRIAL_TOKEN"
WS_ENDPOINT = f"wss://quote.stream.example.com/ws/l2?token={TRIAL_TOKEN}"

# 拟订阅的标的代码与通道列表
SUBSCRIBE_SYMBOLS = ["600519.SH", "000001.SZ", "300750.SZ"]
SUBSCRIBE_CHANNELS = ["l2.trade", "l2.order", "l2.depth"]


def on_message(ws, message):
    try:
        data = json.loads(message)
        channel = data.get("channel")
        symbol = data.get("symbol")
        timestamp = data.get("time")

        if channel == "l2.trade":
            price = data.get("price")
            vol = data.get("volumeShares")
            side = data.get("side")  # B=主动买, S=主动卖
            print(f"[{timestamp}] [逐笔成交] {symbol} | 价格: {price:.2f} | 数量: {vol}股 | 方向: {side}")

        elif channel == "l2.order":
            order_type = data.get("orderType")  # BUY, SELL, CANCEL
            price = data.get("price")
            vol = data.get("volumeShares")
            print(f"[{timestamp}] [逐笔委托] {symbol} | 类型: {order_type} | 申报单价: {price:.2f} | 申报量: {vol}股")

        elif channel == "l2.depth":
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            bid1 = f"{bids[0]['price']} ({bids[0]['volume']}股)" if bids else "N/A"
            ask1 = f"{asks[0]['price']} ({asks[0]['volume']}股)" if asks else "N/A"
            print(f"[{timestamp}] [千档盘口] {symbol} | 买一: {bid1} <---> 卖一: {ask1}")

    except Exception as e:
        print(f"解析消息异常: {e}")


def on_error(ws, error):
    print(f"[-] 连接发生错误: {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"[!] 连接关闭: status={close_status_code}, msg={close_msg}")


def on_open(ws):
    print("[+] 成功与 Level-2 行情服务建立 WebSocket 连接！")
    subscribe_request = {
        "action": "subscribe",
        "symbols": SUBSCRIBE_SYMBOLS,
        "channels": SUBSCRIBE_CHANNELS,
        "timestamp": int(time.time() * 1000)
    }
    ws.send(json.dumps(subscribe_request))
    print(f"[+] 已发送订阅指令: 标的={SUBSCRIBE_SYMBOLS}, 通道={SUBSCRIBE_CHANNELS}")


if __name__ == "__main__":
    print("正在启动 Level-2 行情接收客户端...")
    print("提示: 申请测试 Token 请联系微信: luffy953")
    
    ws_app = websocket.WebSocketApp(
        WS_ENDPOINT,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws_app.run_forever()
