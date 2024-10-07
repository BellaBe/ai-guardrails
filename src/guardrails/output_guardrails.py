import asyncio
from openai import OpenAI
import numpy as np
from loguru import logger


class OutputGuardrails:
    def __init__(self, config):
        self.guardrails_config = config.get("output_guardrails")
        self.guardrails = config.get("output_guardrails")
        self.model = config.get("models")["openai_model"]
        self.llm = OpenAI()

    async def check_factual_accuracy(self, response: str):
        logger.info("Checking factual accuracy")
        prompt = f"Evaluate the factual accuracy of the following statement:\n\n'{response}'\n\nRespond with 'True' if the statement is accurate, or 'False' if it's not."

        completion = await self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1,
            temperature=0
        )
            
        result = completion.choices[0].message.content.strip().lower()
        is_accurate = result == 'true'

        if not is_accurate:
            logger.warning("Response is factually inaccurate.")
        return is_accurate

    async def check_relevancy(self, response: str, user_input: str):
        logger.info("Checking relevancy")
        # Calculate semantic similarity using embeddings
        response_embedding = await self.get_embedding(response)
        input_embedding = await self.get_embedding(user_input)
        similarity = self.cosine_similarity(response_embedding, input_embedding)

        # Set a threshold for relevancy
        if similarity < 0.7:
            logger.warning("Response is not relevant to the user's input.")
            return False
        return True

    async def get_embedding(self, text: str):
        result = self.llm.embeddings.create(
            input=text,
            engine="text-embedding-ada-002"
        )
        return result['data'][0]['embedding']

    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    async def check_policy_compliance(self, response: str):
        logger.info("Checking policy compliance")
        # Use OpenAI's Moderation API
        moderation_response = self.llm.moderations.create(
            input=response
        )
        if moderation_response["results"][0].flagged:
            logger.warning("Response violates policy.")
            return False
        return True

    async def check_contextual_coherence(self, response: str, conversation_history: list):
        logger.info("Checking contextual coherence")
        # Append the response to the conversation and evaluate
        messages = conversation_history + [{"role": "assistant", "content": response}]
        prompt = "Determine if the assistant's last response is contextually coherent within the conversation. Respond with 'True' or 'False'."

        completion = await self.llm.completions.create(
            model="gpt-3.5-turbo",
            messages=messages + [{"role": "user", "content": prompt}],
            max_tokens=1,
            temperature=0
        )
        result = completion.choices[0].message.content.strip().lower()
        is_coherent = result == 'true'

        if not is_coherent:
            logger.warning("Response lacks contextual coherence.")
        return is_coherent

    async def run(self, llm_response: str, user_input: str, conversation_history: list):
        logger.info("Running output guardrails")

        checks = await asyncio.gather(
            self.check_factual_accuracy(llm_response),
            self.check_relevancy(llm_response, user_input),
            self.check_policy_compliance(llm_response),
            self.check_contextual_coherence(llm_response, conversation_history)
        )

        if all(checks):
            return "allowed", llm_response
        else:
            return "blocked", "The response violates one or more output guardrails."
