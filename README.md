# A股 Level-2 高频行情数据中心 · 逐笔明细与千档盘口流

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Protocol](https://img.shields.io/badge/Protocol-WebSocket%20%7C%20REST-green.svg)](#)
[![Data](https://img.shields.io/badge/Data-Level--2%20Tick%20%26%20Depth-orange.svg)](#)
[![Symbols](https://img.shields.io/badge/Coverage-5000%2B%20Symbols-cyan.svg)](#)
[![Latency](https://img.shields.io/badge/Latency-%3C%205ms-red.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**专为量化交易、高频做市、订单流 (Order Flow) 策略与盘口微观结构研究打造的 A股 Level-2 高精度行情服务**

[🌐 在线交互看板体验 (Live Demo)](https://luffy953.github.io/level2-data/) · [📊 数据结构字典](#-数据结构与字段规范) · [⚡ 快速开始](#-快速开始) · [💬 申请免费试用](#-免费测试与技术交流)

</div>

---

## 📌 项目概述

在现代量化交易中，普通 Level-1（五档切片、3秒一次快照）已无法满足订单流失衡分析、大单异动监控、微观结构预测及高频做市的需求。

**Level2-Data** 致力于为量化团队、私募机构与独立研究员提供**全市场、低延迟、高完整度**的 A股 Level-2 高频数据解决方案。支持沪深全市场股票、ETF、可转债实时 WebSocket 推流与高精度历史逐笔清洗回测。

### 🌟 核心特性

- ⚡ **毫秒级逐笔成交 (Tick Trade)**：每笔成交毫秒时间戳、主动买卖方向 (B/S)、真实撮合量价、买卖双方原始申报单号精确匹配。
- 📋 **逐笔委托与撤单 (Tick Order)**：全量委托订单流，精准捕捉机构大单挂单、垫单、扫盘与秒级大单撤销行为。
- 📊 **千档深度盘口 (1000-Level Depth)**：超越传统十档盘口，支持双向各 1000 档位订单深度累计与微观分布。
- 🔍 **最优档位挂单队列 (Top-50 Queue)**：买一/卖一档位前 50 笔委托明细分布，拆解排队单构成。
- 🔄 **高并发稳定推流**：支持 WebSocket 订阅、断线重连、心跳保活；支持全量历史数据导出为 Parquet / CSV / ClickHouse。

---

## 🖥️ 在线交互看板

项目自带高颜值金融终端交互看板，无需配置本地环境，直接点击体验千档盘口与逐笔数据流展示：

👉 **[点击直接访问在线看板 (GitHub Pages)](https://luffy953.github.io/level2-data/)**

---

## 📐 数据结构与字段规范

### 1. 逐笔成交数据流 (`channel: l2.trade`)

| 字段名称 | 类型 | 说明 | 示例 |
| :--- | :--- | :--- | :--- |
| `channel` | string | 数据通道标识 | `"l2.trade"` |
| `symbol` | string | 证券代码 (带市场后缀) | `"600519.SH"` |
| `tradeSeq` | int64 | 成交唯一递增序号 | `4192084` |
| `time` | string | 毫秒撮合时间戳 | `"2026-09-23 14:58:22.480"` |
| `price` | float | 实际成交价格 (元) | `1425.80` |
| `volumeShares` | int64 | 成交股数 (股) | `2000` |
| `amount` | float | 成交金额 (元) | `2851600.00` |
| `side` | string | 内外盘方向：`B`=主动买 (外盘), `S`=主动卖 (内盘), `N`=未知 | `"B"` |
| `buyOrderId` | int64 | 买方原始申报单号 | `1849250` |
| `sellOrderId` | int64 | 卖方原始申报单号 | `1846012` |

### 2. 逐笔委托与撤单流 (`channel: l2.order`)

| 字段名称 | 类型 | 说明 | 示例 |
| :--- | :--- | :--- | :--- |
| `channel` | string | 数据通道标识 | `"l2.order"` |
| `symbol` | string | 证券代码 | `"600519.SH"` |
| `orderSeq` | int64 | 委托唯一递增序号 | `3891045` |
| `orderId` | int64 | 订单编号 | `1849120` |
| `time` | string | 申报时间戳 | `"2026-09-23 14:58:22.180"` |
| `orderType` | string | 委托类型：`BUY`(买), `SELL`(卖), `CANCEL`(撤单) | `"CANCEL"` |
| `price` | float | 申报价格 (市价单为 0 或市价类型编码) | `1426.00` |
| `volumeShares` | int64 | 申报股数 / 撤销股数 | `10000` |
| `origOrderId` | int64 | 撤单对应的原订单编号 | `1849120` |

### 3. 千档盘口与队列 (`channel: l2.depth`)

```json
{
  "channel": "l2.depth",
  "symbol": "600519.SH",
  "time": "2026-09-23 14:58:22.500",
  "lastPrice": 1425.80,
  "bids": [
    {"level": 1, "price": 1425.80, "volume": 8500, "ordersCount": 28},
    {"level": 2, "price": 1425.50, "volume": 6000, "ordersCount": 15},
    {"level": 3, "price": 1425.00, "volume": 12400, "ordersCount": 42}
  ],
  "asks": [
    {"level": 1, "price": 1426.00, "volume": 5200, "ordersCount": 19},
    {"level": 2, "price": 1426.50, "volume": 7800, "ordersCount": 23},
    {"level": 3, "price": 1427.00, "volume": 15600, "ordersCount": 56}
  ],
  "bid1Queue": [1200, 800, 2000, 500, 1000, 3000],
  "ask1Queue": [1500, 700, 1000, 2000]
}
```

---

## ⚡ 快速开始

可以使用任何支持 WebSocket 的编程语言（Python / C++ / Go / Rust / Node.js）进行订阅。以下为 Python 极简客户端接入示例：

```bash
pip install websocket-client
```

```python
import json
import websocket

# 获取测试 Token 请联系微信: luffy953
TOKEN = "YOUR_TRIAL_TOKEN"
WS_ENDPOINT = f"wss://quote.stream.example.com/ws/l2?token={TOKEN}"

def on_message(ws, message):
    data = json.loads(message)
    ch = data.get("channel")
    if ch == "l2.trade":
        print(f"[{data['time']}] 逐笔成交 {data['symbol']} 价格:{data['price']} 股数:{data['volumeShares']} 方向:{data['side']}")
    elif ch == "l2.depth":
        print(f"[{data['time']}] 盘口更新 {data['symbol']} 买一:{data['bids'][0]['price']} 卖一:{data['asks'][0]['price']}")

def on_open(ws):
    print(">>> 连接建立成功，开始订阅行情...")
    sub_payload = {
        "action": "subscribe",
        "symbols": ["600519.SH", "000001.SZ", "300750.SZ"],
        "channels": ["l2.trade", "l2.order", "l2.depth"]
    }
    ws.send(json.dumps(sub_payload))

if __name__ == "__main__":
    ws = websocket.WebSocketApp(WS_ENDPOINT, on_open=on_open, on_message=on_message)
    ws.run_forever()
```

---

## 🎁 免费测试与技术交流

我们为 GitHub 开源社区的开发者提供以下免费支持与资源包：

> 💡 **如何领取福利 / 申请测试权限：**
> 
> 添加微信：**`luffy953`**  
> *(添加时请备注：**GitHub / 量化**，以便快速通过)*

### 免费专享福利：
1. **免费领取历史样本包**：
   - 包含贵州茅台 (600519)、宁德时代 (300750) 等沪深核心标的**单日全量逐笔成交、逐笔委托与千档盘口回测文件** (Parquet / CSV / JSON)。
2. **免费申请 3~7 天实时推流测试 Token**：
   - 独立 API 接入凭证，体验毫秒级 WebSocket 推流与全市场 5000+ 标的实时订阅。
3. **技术交流与私有化支持**：
   - 交流微观盘口特征工程（如订单流失衡 OFI、买卖排队撤单率、大单冲击成本等）；
   - 支持私有化行情接入网关定制、ClickHouse / DolphinDB 存储方案咨询。

---

## ⚠️ 免责声明 (Disclaimer)

1. 本项目所载说明、代码示例及数据展示仅供**量化策略研发、学术研究与编程技术交流**使用。
2. 本项目不提供任何投资建议，不引导参与任何实际证券交易，亦不对基于相关数据产生的任何交易盈亏承担责任。
3. 数据版权归属于各证券交易所及合法数据授权方。市场有风险，投资需谨慎。
