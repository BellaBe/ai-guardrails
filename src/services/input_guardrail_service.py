from src.clients.nats_client import NATSClient
from src.guardrails.input_guardrails import InputGuardrails
from loguru import logger

class InputGuardrailService:
    def __init__(self, config):
        self.nats_client = NATSClient()
        self.guardrails_config = config.get("input_guardrails")  # Retrieve guardrails config
        self.input_guardrails = InputGuardrails(self.guardrails_config)

    async def start(self):
        await self.nats_client.connect()
        await self.nats_client.subscribe("input_guardrail", self.handle_input_guardrail_task)

    async def handle_input_guardrail_task(self, msg):
        try:
            user_input = msg.data.decode()
            logger.info(f"Processing input guardrail for: {user_input}")
            
            # Validate user input against guardrails
            status, message = await self.input_guardrails.run(user_input)
            
            # Publish result to orchestrator
            await self.nats_client.publish("input_guardrail_response", status)
        except Exception as e:
            logger.error(f"Error processing input guardrail task: {e}")

    async def close(self):
        await self.nats_client.close()
