# src/guardrails/input_guardrails.py

import re
from loguru import logger

class InputGuardrails:
    def __init__(self, guardrails_config):
        self.guardrails = guardrails_config

    async def validate_topics(self, user_input: str):
        allowed_topics = [topic.lower() for topic in self.guardrails['topics']['allowed']]
        off_topic_keywords = [keyword.lower() for keyword in self.guardrails['topics']['off_topic']]

        # Check for off-topic content
        if any(keyword in user_input.lower() for keyword in off_topic_keywords):
            logger.warning(f"Off-topic content detected: {user_input}")
            return "not_allowed", "Your request is off-topic."

        # Check if the input contains at least one allowed topic keyword
        if not any(topic in user_input.lower() for topic in allowed_topics):
            logger.warning(f"Input does not match allowed topics: {user_input}")
            return "not_allowed", "Your request is not related to allowed topics."

        logger.info("Input within allowed topics")
        return "allowed", None

    async def detect_prompt_injections(self, user_input: str):
        patterns = self.guardrails['injections']['prompt_injections'] + self.guardrails['injections']['jailbreak_patterns']
        patterns = [pattern.lower() for pattern in patterns]

        # Check for prompt injections or jailbreak patterns
        if any(re.search(re.escape(pattern), user_input.lower()) for pattern in patterns):
            logger.warning(f"Prompt injection or jailbreak detected: {user_input}")
            return "not_allowed", "Your request contains disallowed patterns."

        logger.info("No prompt injection or jailbreak detected")
        return "allowed", None

    async def run(self, user_input: str):
        logger.info("Running input guardrails")
        
        status, message = await self.detect_prompt_injections(user_input)
        if status == "not_allowed":
            return status, message

        status, message = await self.validate_topics(user_input)
        if status == "not_allowed":
            return status, message

        return "allowed", None
