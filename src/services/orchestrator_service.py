import json
import asyncio
from loguru import logger
from src.clients.nats_client import NATSClient

class Orchestrator:
    def __init__(self, config):
        self.nats_client = NATSClient()
        self.config = config
        self.user_input = None
        self.response_event = asyncio.Event()
        self.final_response = None

    async def start(self):
        try:
            await self.nats_client.connect()
            logger.info("NATS client connected")

            # Subscribe to input and output guardrail responses
            await self.nats_client.subscribe("input_guardrail_response", self.handle_input_guardrail_response)
            await self.nats_client.subscribe("output_guardrail_response", self.handle_output_guardrail_response)
        except Exception as e:
            logger.error(f"Failed to start orchestrator service: {e}")

    async def process_request(self, input_data):
        """
        Dispatch content to either the input guardrail (for user input)
        or the output guardrail (for LLM content).
        :param input_data: dict with fields like {'content': '...', 'source': 'user' or 'llm'}
        """
        source = input_data.get("source", "user")

        try:
            if source == "user":
                # Dispatch user input to the input guardrail
                user_question = input_data.get("user_question", "")
                await self.nats_client.publish("input_guardrail", user_question)
                logger.debug(f"Dispatched to input_guardrail: {user_question}")
            elif source == "llm":
                # Dispatch LLM input (composite object) to the output guardrail
                await self.nats_client.publish("output_guardrail", json.dumps(input_data))
                logger.debug(f"Dispatched to output_guardrail with composite data: {input_data}")

            # Wait for the appropriate guardrail response
            await asyncio.wait_for(self.response_event.wait(), timeout=30)  # Timeout after 10 seconds
            self.response_event.clear()
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for guardrail responses")
            self.final_response = "Request timed out. Please try again."
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.final_response = "There was an error processing your request."

        return self.final_response

    async def handle_input_guardrail_response(self, msg):
        """
        Handle the response from the input guardrail.
        """
        status = msg.data.decode()
        logger.info(f"Received input guardrail response: {status}")

        if status == "allowed":
            # Input guardrail approved, ready for LLM processing
            logger.info("Input guardrail passed, ready for LLM processing.")
            self.final_response = "Input allowed."
        else:
            logger.info("Input guardrail blocked the request.")
            self.final_response = "Your input was not accepted."

        self.response_event.set()

    async def handle_output_guardrail_response(self, msg):
        """
        Handle the response from the output guardrail after processing LLM responses.
        """
        data = json.loads(msg.data.decode())
        status = data['status']
        message = data['message']
        logger.info(f"Received output guardrail response: {status}, message: {message}")

        if status == "allowed":
            logger.info("Output guardrail passed, delivering response to user.")
            self.final_response = message
        else:
            logger.info("Output guardrail blocked the response.")
            self.final_response = "Sorry, I cannot provide that information."

        self.response_event.set()

    async def close(self):
        await self.nats_client.close()
