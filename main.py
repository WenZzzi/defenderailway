import httpx
import asyncio
import os
from datetime import datetime

BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
CHAT_ID = os.environ["TG_CHAT_ID"]

status = "ok"

async def send_tg(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

async def check():
    global status
    now = datetime.utcnow().strftime("%H:%M UTC")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post("https://fred-mcp-server-production-efe8.up.railway.app/mcp")
        alive = r.status_code not in [502, 503, 504]
    except Exception:
        alive = False

    if not alive and status == "ok":
        await send_tg("🔴 <b>FRED MCP</b> 宕机\n检测时间：" + now)
        status = "down"
    elif alive and status == "down":
        await send_tg("🟢 <b>FRED MCP</b> 已恢复\n恢复时间：" + now)
        status = "ok"

async def main():
    await send_tg("✅ 监控启动，每 5 分钟检查一次 FRED MCP")
    while True:
        await check()
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
