import os
import json
import asyncio
import logging

log = logging.getLogger("ipc")

SOCK = "/run/lsmy/provision.sock"

LAST_TELEMETRY = {
    "temperature": 0.0,
    "humidity": 0.0,
    "no2": 0.0,
    "pm10": 0.0,
    "pm25": 0.0,
}

async def handle_client(reader, writer):
    try:
        data = await reader.readline()
        if not data:
            return

        req = json.loads(data.decode())
        log.info("IPC RX: %s", req)

        if req.get("cmd") == "send_telemetry":
            telemetry = {
                "temperature": float(req.get("temperature", 0)),
                "humidity": float(req.get("humidity", 0)),
                "no2": float(req.get("no2", 0)),
                "pm10": float(req.get("pm10", 0)),
                "pm25": float(req.get("pm25", 0)),
            }

            log.info("Telemetry received: %s", telemetry)

            LAST_TELEMETRY.update(telemetry)

            resp = {"status": "ok"}
        else:
            resp = {"status": "error", "error": "Unknown command"}

        writer.write((json.dumps(resp) + "\n").encode())
        await writer.drain()

    except Exception:
        log.exception("IPC handler error")
    finally:
        writer.close()

async def send_telemetry_ipc(data: dict, timeout=3):
    reader, writer = await asyncio.wait_for(
        asyncio.open_unix_connection(SOCK),
        timeout=timeout
    )

    msg = {
        "cmd": "send_telemetry",
        "temperature": data.get("temperature", 0),
        "humidity": data.get("humidity", 0),
        "no2": data.get("no2", 0),
        "pm10": data.get("pm10", 0),
        "pm25": data.get("pm25", 0),
    }

    writer.write((json.dumps(msg) + "\n").encode())
    await writer.drain()

    resp = await reader.readline()
    writer.close()

    return json.loads(resp.decode())


async def ipc_server_task():
    if os.path.exists(SOCK):
        os.unlink(SOCK)

    server = await asyncio.start_unix_server(
        handle_client,
        path=SOCK
    )
    os.chmod(SOCK, 0o660)

    log.info("IPC server listening on %s", SOCK)

    async with server:
        await server.serve_forever()

