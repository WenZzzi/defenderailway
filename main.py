import httpx
import asyncio
import os
import sys
from datetime import datetime, timezone

BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
CHAT_ID = os.environ["TG_CHAT_ID"]
URL = "https://fred-mcp-server-production-efe8.up.railway.app/mcp"

status = "ok"

def log(msg):
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)

async def send_tg(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

async def check():
    global status
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(URL, json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                                  headers={"Content-Type": "application/json"})
        is_railway_404 = r.status_code == 404 and "train has not arrived" in r.text.lower()
        alive = (r.status_code < 500) and not is_railway_404
        log(f"检查结果: status={r.status_code}, railway_404={is_railway_404}, alive={alive}")
    except Exception as e:
        alive = False
        log(f"检查结果: 连接失败 ({type(e).__name__}), alive=False")

    if not alive and status == "ok":
        await send_tg("🔴 <b>FRED MCP</b> 宕机\n检测时间：" + now)
        status = "down"
        log("→ 已发送宕机通知")
    elif alive and status == "down":
        await send_tg("🟢 <b>FRED MCP</b> 已恢复\n恢复时间：" + now)
        status = "ok"
        log("→ 已发送恢复通知")

async def main():
    await send_tg("✅ 监控启动（测试模式，每 60 秒检查一次）")
    log("监控启动")
    while True:
        await check()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
