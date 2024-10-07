import asyncio
from src.services.input_guardrail_service import InputGuardrailService
from src.services.output_guardrail_service import OutputGuardrailService
from src.services.orchestrator_service import Orchestrator
from src.config import Config
from src.utils.logger import setup_logger
from loguru import logger


async def get_input_source():
    """
    Prompt the user for the source type (user or llm).
    """
    loop = asyncio.get_running_loop()
    source = await loop.run_in_executor(None, input, "Enter source (user/llm): ")
    return source.lower()

async def get_user_question():
    """
    Prompt the user for the question or input content.
    """
    loop = asyncio.get_running_loop()
    question = await loop.run_in_executor(None, input, "Enter the user question or input: ")
    return question

async def get_input_source():
    """
    Prompt the user for the source type (user or llm).
    """
    loop = asyncio.get_running_loop()
    source = await loop.run_in_executor(None, input, "Enter source (user/llm): ")
    return source.lower()

async def get_conversation_history():
    """
    Prompt the user for the conversation history.
    """
    loop = asyncio.get_running_loop()
    history = await loop.run_in_executor(None, input, "Enter the conversation history: ")
    return history


async def get_llm_response():
    """
    Simulate or get the LLM's response.
    """
    loop = asyncio.get_running_loop()
    llm_response = await loop.run_in_executor(None, input, "Enter the LLM response: ")
    return llm_response


async def input_loop(orchestrator: Orchestrator):
    try:
        while True:
            # Get input source (user or llm)
            source = await get_input_source()

            if source.lower() == "llm":
                # For LLM, we need the user question, conversation history, and the LLM response
                user_question = await get_user_question()
                conversation_history = await get_conversation_history()
                llm_response = await get_llm_response()

                # Create structured input data with LLM composite information
                structured_input = {
                    "source": "llm",
                    "user_question": user_question,  # The original user question
                    "conversation_history": conversation_history,  # Conversation history
                    "llm_response": llm_response  # LLM generated response
                }
            else:
                # For user input, we only need the user's content
                user_question = await get_user_question()

                structured_input = {
                    "source": "user",
                    "user_question": user_question  # User's input content
                }

            # Process the structured input through the orchestrator
            response = await orchestrator.process_request(structured_input)
            print(f"Assistant: {response}")
    except KeyboardInterrupt:
        logger.info("User interrupted the application.")


async def main():
    setup_logger()
    logger.info("Starting all services...")

    # Load configuration
    config = Config()

    # Pass config to services
    input_service = InputGuardrailService(config)
    output_service = OutputGuardrailService(config)
    orchestrator_service = Orchestrator(config)

    # Start services
    await asyncio.gather(
        input_service.start(),
        output_service.start(),
        orchestrator_service.start()
    )

    # Start unified input loop for both user and LLM inputs
    await input_loop(orchestrator_service)



if __name__ == "__main__":
    asyncio.run(main())
