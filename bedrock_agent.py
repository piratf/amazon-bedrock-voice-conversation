import json
from bedrock_models_wrapper import BedrockModelsWrapper
from conversation_context import ConversationContext
from logger import logger
from config import config, change_model
from bedrock_knowledge_base import BedrockKnowledgeBase
from src.tools.function_dispatcher import function_dispatcher
import queue
import threading

class BedrockAgent:
    def __init__(self, bedrock_runtime):
        self.bedrock_runtime = bedrock_runtime
        self.context = ConversationContext()
        self.knowledge_base = BedrockKnowledgeBase()
        logger.info("BedrockAgent initialized")

    def process(self, text):
        # Step 0: Fix typos in the input
        corrected_text = self._fix_typos(text)

        # Step 1: Analyze the input
        json_content = self._analyze_input(corrected_text)

        # Parse the extracted JSON content
        try:
            analysis = json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON content: {e}")
            analysis = {"is_about_lol": False, "explanation": "Error in parsing input"}
            print(f"An error occurred while processing your input: {e}")

        if not analysis.get("is_about_lol", False):
            logger.info("Processing as chat")
            return self._chat_with_user(corrected_text)
        else:
            logger.info("Processing as question")
            return self._solve_question(corrected_text)

    # To support tools, this function always return full text response
    # The text response will have SSML tags for TTS
    def process_with_tools(self, text):
        corrected_text = self._fix_typos(text)

        return self._solve_question_with_tools(corrected_text)

    def _solve_question_with_tools(self, text):
        enhanced_prompt = f"""Respond briefly and casually to: {text}. Keep your answer short and friendly:"""
        return self._invoke_bedrock(enhanced_prompt,
                                    is_stream=False,
                                    turn_type="Final Ask",
                                    system_prompt="""You are a friendly AI assistant who's an expert in League of Legends. 
                                    Keep your responses brief and to the point, ideally no more than 2-3 sentences. 
                                    Use a casual, friendly tone. If the topic isn't about League, try to steer the conversation back to it when possible.
                                    Be prepared to switch between light-hearted banter and in-depth game analysis as the conversation flows.  
                                    Always format your responses using SSML tags.
SSML formatting rules:

- Enclose all responses in <speak> tags
- Use <p> tags for paragraphs or distinct thoughts
- Insert <break> tags with specific timings (e.g., <break time="0.5s"/>) for natural pauses
- Apply <prosody> tags for rate and volume adjustments only
- Set the overall speech rate to 93% using <prosody rate="90%">
- Use <prosody rate="slow"> or <prosody volume="soft"> for emphasis on key points
- Ensure all tags are properly closed
""",
                                    use_tools=True)

    def _fix_typos(self, text):
        prompt = f"""
Here's a list of all current League of Legends champion names for your reference:
Aatrox, Ahri, Akali, Akshan, Alistar, Amumu, Anivia, Annie, Aphelios, Ashe, Aurelion Sol, Aurora, Azir, Bard, Bel'Veth, Blitzcrank, Brand, Braum, Briar, Caitlyn, Camille, Cassiopeia, Cho'Gath, Corki, Darius, Diana, Dr. Mundo, Draven, Ekko, Elise, Evelynn, Ezreal, Fiddlesticks, Fiora, Fizz, Galio, Gangplank, Garen, Gnar, Gragas, Graves, Gwen, Hecarim, Heimerdinger, Hwei, Illaoi, Irelia, Ivern, Janna, Jarvan IV, Jax, Jayce, Jhin, Jinx, Kai'Sa, Kalista, Karma, Karthus, Kassadin, Katarina, Kayle, Kayn, Kennen, Kha'Zix, Kindred, Kled, Kog'Maw, K'Sante, LeBlanc, Lee Sin, Leona, Lillia, Lissandra, Lucian, Lulu, Lux, Malphite, Malzahar, Maokai, Master Yi, Milio, Miss Fortune, Mordekaiser, Morgana, Naafiri, Nami, Nasus, Nautilus, Neeko, Nidalee, Nilah, Nocturne, Nunu & Willump, Olaf, Orianna, Ornn, Pantheon, Poppy, Pyke, Qiyana, Quinn, Rakan, Rammus, Rek'Sai, Rell, Renata Glasc, Renekton, Rengar, Riven, Rumble, Ryze, Samira, Sejuani, Senna, Seraphine, Sett, Shaco, Shen, Shyvana, Singed, Sion, Sivir, Skarner, Smolder, Sona, Soraka, Swain, Sylas, Syndra, Tahm Kench, Taliyah, Talon, Taric, Teemo, Thresh, Tristana, Trundle, Tryndamere, Twisted Fate, Twitch, Udyr, Urgot, Varus, Vayne, Veigar, Vel'Koz, Vex, Vi, Viego, Viktor, Vladimir, Volibear, Warwick, Wukong, Xayah, Xerath, Xin Zhao, Yasuo, Yone, Yorick, Yuumi, Zac, Zed, Zeri, Ziggs, Zilean, Zoe, Zyra

Task: The input is a sentence generated by TTS, due to inaccurate speech recognition, there might be misidentification of champion names as other words, or misidentification of words in previous context. you need to carefully dissect each word, find and correct the errors.

Input: {text}

Instructions:
1. Carefully analyze the input text for any words that might be misspelled League of Legends champion names.
2. Which champion's name sounds most like the word? Replace the word with the correct spelling.
3. Make no other changes to the text.
4. Return only the corrected or original text, without any explanations.

Output:
"""
        response = self._invoke_bedrock(prompt, include_context=True, turn_type="Spell Check", system_prompt="", is_stream=False, model_id="anthropic.claude-3-5-sonnet-20240620-v1:0")

        logger.info(f"Spell check input: {text}")
        logger.info(f"Spell check response: {response}")
        return response.strip()

    def _analyze_input(self, text):
        prompt = f"""Analyze the following input and answer two questions:

1. Is it a question or a casual chat?
2. Is it about League of Legends?

Input: "{text}"

Also, provide a brief explanation of your analysis.

Output the JSON ONLY.

Example output format:
{{
    "is_about_lol": boolean,
    "explanation": "A brief explanation of your analysis"
}}
"""
        return self._invoke_bedrock(prompt, turn_type="Analysis", system_prompt="", is_stream=False, model_id="anthropic.claude-instant-v1")

    def _chat_with_user(self, text):
        return self._invoke_bedrock_with_queue(text, turn_type="Final Ask", system_prompt="You are a friendly AI assistant.")

    def _solve_question(self, text):
        kb_analysis = {
            "kb_needed": True,
            "kb_ids": ["FQYOEZO3D0"],
        }

        # before fetching from knowledge bases, the question should be completed with the history of the conversation
        completed_question = self._complete_question_for_kb(text)

        kb_content = self._fetch_from_knowledge_bases(kb_analysis, completed_question) if kb_analysis['kb_needed'] else ""

        enhanced_prompt = f"""You're a League of Legends expert. Provide the shortest possible accurate answer:

Question: {text}

Relevant Knowledge Base Information:
{kb_content}

Instructions:
1. Carefully analyze the question and the provided knowledge base information.
2. Formulate a clear, concise, and accurate answer based on the available information.
3. If the knowledge base doesn't contain enough information to fully answer the question, use your general knowledge about League of Legends to supplement the answer.
4. If there are any ambiguities or multiple interpretations of the question, address the most likely interpretation.
5. Provide specific examples or references from the game when relevant.
6. If the question cannot be answered with the given information, explain why and suggest what additional information might be needed.

Answer:"""
        return self._invoke_bedrock_with_queue(enhanced_prompt, turn_type="Final Ask", system_prompt="You are a knowledgeable and enthusiastic League of Legends expert, eager to help players understand the game better.")

    def _analyze_knowledge_base_need(self, text):
        prompt = f"""Analyze if the following question requires information from knowledge bases:

Question: "{text}"

Output JSON only with the following structure:
{{
    "kb_needed": boolean,
    "kb_ids": list of strings,
    "explanation": string
}}

Available knowledge bases:
1. "lol_champions": Contains information about League of Legends champions, their abilities, and stats.
2. "lol_items": Contains information about items, runes, and other game mechanics in League of Legends.
3. "lol_stories": Contains information about the universe of League of Legends, including champions' backstories, legends, myths, and lore.

Analyze the question and choose the most appropriate knowledge base IDs, or an empty list if none are relevant.
"""
        response = self._invoke_bedrock(prompt, turn_type="KBAnalysis", system_prompt="You are an AI that determines if external knowledge is needed to answer questions.", is_stream=False)
        return json.loads(response)

    def _fetch_from_knowledge_bases(self, kb_analysis, question):
        if kb_analysis['kb_needed'] and kb_analysis['kb_ids']:
            results = self.knowledge_base.query_all(kb_analysis['kb_ids'], question, max_results_per_kb=10)
            formatted_results = self.knowledge_base.format_results(results, include_kb_id=True)
            logger.debug(f"Knowledge base results: {formatted_results}")
            return f"Relevant Knowledge Base Information:\n{formatted_results}"
        return ""

    # _invoke_bedrock will return a stream response if is_stream is True 
    # otherwise it will return a text response
    def _invoke_bedrock(self, prompt, include_context=True, turn_type="Chat", is_stream=False, system_prompt=None, model_id=None, use_tools=True):
        context = self.context.context if include_context else None
        body = BedrockModelsWrapper.define_body(prompt, context=context, system_prompt=system_prompt, model_id=model_id, use_tools=use_tools)
        body_json = json.dumps(body)

        logger.debug(f"Invoking Bedrock with body: {body_json}")

        if turn_type=="Final Ask":
            self.context.add_text_turn_v2("user", prompt)
        # if use_tools is true, it will continue to invoke bedrock until don't need to call any tools
        while True:
            response = self.bedrock_runtime.invoke_model(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )
            full_response = json.loads(response.get('body').read())

            logger.debug(f"Bedrock response: {full_response}")

            if not use_tools or full_response.get('stop_reason') != 'tool_use':
                break

            if 'content' in full_response and isinstance(full_response['content'], list):
                for content_block in full_response['content']:
                    if content_block.get('type') == 'tool_use':
                        tool_use = content_block
                        tool_name = tool_use['name']
                        tool_input = tool_use['input']
                        tool_use_id = tool_use['id']

                        # Call the appropriate tool using the function dispatcher
                        tool_result = function_dispatcher(tool_name, **tool_input)

                        # Add the tool use request to the messages
                        tool_use_turn = {
                            'role': 'assistant',
                            'content': [{
                                'type': 'tool_use',
                                'id': tool_use_id,
                                'name': tool_name,
                                'input': tool_input
                            }]
                        }
                        body['messages'].append(tool_use_turn)
                        # We need to add tool_use to the context
                        self.context.add_content_turn(tool_use_turn)
                        # Add the tool result to the messages and re-invoke the model
                        tool_result_turn = {
                            'role': 'user',
                            'content': [{
                                'type': 'tool_result',
                                'tool_use_id': tool_use_id,
                                'content': json.dumps(tool_result)
                            }]
                        }
                        body['messages'].append(tool_result_turn)
                        self.context.add_content_turn(tool_result_turn)

                        logger.info(f"Use tool: {tool_name}, input: {tool_input}")
                        logger.debug(f"Tool result: {tool_result}")

                        body_json = json.dumps(body)
                        break
                else:
                    # If no tool_use was found, we have our final response
                    break
            else:
                # If there's no content list, we have our final response
                break

        text_response = BedrockModelsWrapper.get_non_stream_text(full_response)
        logger.info(f"Text response: {text_response}")
        # Add turn to context if it's not an analysis
        if turn_type == "Final Ask":
            self.context.add_text_turn_v2("assistant", text_response)
        return text_response

    def _process_stream_response(self, bedrock_stream):
        full_response = ""
        for event in bedrock_stream:
            chunk = BedrockModelsWrapper.get_stream_chunk(event)
            if chunk:
                text = BedrockModelsWrapper.get_stream_text(chunk)
                full_response += text
        return full_response

    def _process_non_stream_response(self, response):
        response_body = json.loads(response.get('body').read())
        return BedrockModelsWrapper.get_non_stream_text(response_body)

    def _invoke_bedrock_with_queue(self, text, turn_type, system_prompt, use_tools=False):
        response_queue = queue.Queue()
        
        def collect_full_response(stream):
            full_response = ""
            for event in stream:
                chunk = BedrockModelsWrapper.get_stream_chunk(event)
                if chunk:
                    text = BedrockModelsWrapper.get_stream_text(chunk)
                    full_response += text
                    yield event
            response_queue.put(full_response)

        response_stream = self._invoke_bedrock(text, turn_type, system_prompt, is_stream=True, use_tools=use_tools)
        return collect_full_response(response_stream), response_queue

    def _complete_question_for_kb(self, question):
        # Get the recent conversation history
        recent_history = self.context.get_recent_history(num_turns=10)  # Adjust the number of turns as needed

        # Construct a prompt to complete the question
        prompt = f"""Given the following conversation history and a new question, provide a more complete version of the question that incorporates relevant context from the conversation history. Do not answer the question, just reformulate it with added context if necessary.

Conversation History:
{recent_history}

New Question: {question}

Complete Question:"""

        # Use Bedrock to generate the completed question
        completed_question = self._invoke_bedrock(prompt, turn_type="Question Completion", system_prompt="You are an AI assistant that helps to provide context to questions based on conversation history.", is_stream=False)

        logger.debug(f"Original question: {question}")
        logger.debug(f"Completed question: {completed_question}")

        return completed_question.strip()
