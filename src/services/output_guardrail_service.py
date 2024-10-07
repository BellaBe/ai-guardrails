import json
from src.clients.nats_client import NATSClient
from src.guardrails.output_guardrails import OutputGuardrails
from loguru import logger

class OutputGuardrailService:
    def __init__(self, config):
        self.nats_client = NATSClient()
        self.output_guardrails = OutputGuardrails(config)

    async def start(self):
        await self.nats_client.connect()
        await self.nats_client.subscribe("output_guardrail", self.handle_output_guardrail_task)

    async def handle_output_guardrail_task(self, msg):
        try:
            # Decode the composite object received
            data = json.loads(msg.data.decode())
            llm_response = data['llm_response']
            user_input = data['user_question']
            conversation_history = data['conversation_history']

            logger.info(f"Processing output guardrail for LLM response: {llm_response}")

            # Validate LLM response against guardrails
            status, message = await self.output_guardrails.run(llm_response, user_input, conversation_history)

            # Publish result back to orchestrator
            await self.nats_client.publish("output_guardrail_response", json.dumps({'status': status, 'message': message}))
        except Exception as e:
            logger.error(f"Error processing output guardrail task: {e}")

    async def close(self):
        await self.nats_client.close()
