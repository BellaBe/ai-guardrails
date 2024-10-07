import asyncio
from nats.aio.client import Client as NATS
from loguru import logger
import os

class NATSClient:
    def __init__(self, server_url=None):
        self.server_url = server_url or os.getenv("NATS_SERVER_URL", "nats://127.0.0.1:4222")
        self.nc = NATS()

    async def connect(self):
        try:
            await self.nc.connect(self.server_url)
            logger.info(f"Connected to NATS at {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")

    async def publish(self, subject, message):
        await self.nc.publish(subject, message.encode('utf-8'))
        logger.info(f"Published message to {subject}")

    async def subscribe(self, subject, callback):
        await self.nc.subscribe(subject, cb=callback)
        logger.info(f"Subscribed to {subject}")

    async def close(self):
        await self.nc.close()
        logger.info("NATS connection closed")
