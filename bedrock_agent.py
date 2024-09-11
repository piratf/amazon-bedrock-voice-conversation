import json
from bedrock_models_wrapper import BedrockModelsWrapper
from conversation_context import ConversationContext
from logger import logger
from config import config

class BedrockAgent:
    def __init__(self, bedrock_runtime):
        self.bedrock_runtime = bedrock_runtime
        self.context = ConversationContext()
        logger.info("BedrockAgent initialized")

    # The process function will handle the user input and return the response in stream format
    # The stream format will be used to stream the response to the user in real-time
    def process(self, text):
        # Step 1: Analyze the input
        json_content = self._analyze_input(text)
        logger.debug(f"JSON content: {json_content}")
        
        # Parse the extracted JSON content
        try:
            analysis = json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON content: {e}")
            analysis = {"is_question": False, "is_about_lol": False, "explanation": "Error in parsing input"}
            print(f"An error occurred while processing your input: {e}")

        if not analysis.get("is_question", False):
            logger.info("Processing as chat")
            return self._chat_with_user(text)
        else:
            logger.info("Processing as question")
            return self._solve_question(text)

    def _analyze_input(self, text):
        prompt = f"""Analyze the following input and answer two questions:

1. Is it a question or a casual chat?
2. Is it about League of Legends?

Input: "{text}"

Output the JSON ONLY.

Examples:
Input: "Hello, how are you?"
Output:
{{
    "is_question": false,
    "is_about_lol": false,
    "explanation": "A brief explanation of your analysis"
}}
Input: "I am looking for the latest news in the League of Legends community."
Output:
{{
    "is_question": true,
    "is_about_lol": true,
    "explanation": "A brief explanation of your analysis"
}}
"""
        return self._invoke_bedrock(prompt, turn_type="Analysis", system_prompt="", is_stream=False)

    def _chat_with_user(self, text):
        return self._invoke_bedrock(text, turn_type="Chat", system_prompt="You are a friendly AI assistant.", is_stream=True)

    def _solve_question(self, text):
        return self._invoke_bedrock(text, turn_type="Question", system_prompt="You are a knowledgeable AI assistant ready to answer questions.", is_stream=True)

    def _invoke_bedrock(self, prompt, include_context=True, turn_type="Chat", is_stream=False, system_prompt=None):
        context = self.context.context if include_context else None
        body = BedrockModelsWrapper.define_body(prompt, context=context, system_prompt=system_prompt)
        body_json = json.dumps(body)
        
        logger.debug(f"Invoking Bedrock with body: {body_json}")
        
        if is_stream:
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )
            bedrock_stream = response.get('body')
            return bedrock_stream
        else:
            response = self.bedrock_runtime.invoke_model(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )
            full_response = self._process_non_stream_response(response)

            logger.debug(f"Bedrock response: {full_response}")
            
            # Add turn to context if it's not an analysis
            if turn_type != "Analysis":
                self.context.add_turn(turn_type, system_prompt, prompt, full_response)
            
            return full_response


    def _process_non_stream_response(self, response):
        response_body = json.loads(response.get('body').read())
        return BedrockModelsWrapper.get_non_stream_text(response_body)
