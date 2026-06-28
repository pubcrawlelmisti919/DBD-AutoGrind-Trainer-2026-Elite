import asyncio
import aiohttp
import logging
from pathlib import Path

log = logging.getLogger(__name__)

UPDATE_URL = "https://api.skydock.netlify.app/latest_offsets.json"
OFFSETS_FILE = Path("offsets.py")

async def check_for_updates() -> None:
    """Fetch the latest offset definitions and update offsets.py."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(UPDATE_URL) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    log.info(f"New offsets available: version {data.get('version')}")
                else:
                    log.warning("Update server returned non‑200")
    except Exception as e:
        log.error(f"Auto‑update check failed: {e}")
