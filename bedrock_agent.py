import json
from bedrock_models_wrapper import BedrockModelsWrapper
from conversation_context import ConversationContext
from logger import logger
from config import config
from bedrock_knowledge_base import BedrockKnowledgeBase

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
            return self._chat_with_user(corrected_text)
        else:
            logger.info("Processing as question")
            return self._solve_question(corrected_text)

    def _fix_typos(self, text):
        prompt = f"""
Here's a list of all current League of Legends champion names for reference:
Aatrox, Ahri, Akali, Akshan, Alistar, Amumu, Anivia, Annie, Aphelios, Ashe, Aurelion Sol, Aurora, Azir, Bard, Bel’Veth, Blitzcrank, Brand, Braum, Briar, Caitlyn, Camille, Cassiopeia, Cho'Gath, Corki, Darius, Diana, Dr. Mundo, Draven, Ekko, Elise, Evelynn, Ezreal, Fiddlesticks, Fiora, Fizz, Galio, Gangplank, Garen, Gnar, Gragas, Graves, Gwen, Hecarim, Heimerdinger, Hwei, Illaoi, Irelia, Ivern, Janna, Jarvan IV, Jax, Jayce, Jhin, Jinx, Kai'Sa, Kalista, Karma, Karthus, Kassadin, Katarina, Kayle, Kayn, Kennen, Kha'Zix, Kindred, Kled, Kog'Maw, K’Sante, LeBlanc, Lee Sin, Leona, Lillia, Lissandra, Lucian, Lulu, Lux, Malphite, Malzahar, Maokai, Master Yi, Milio, Miss Fortune, Mordekaiser, Morgana, Naafiri, Nami, Nasus, Nautilus, Neeko, Nidalee, Nilah, Nocturne, Nunu & Willump, Olaf, Orianna, Ornn, Pantheon, Poppy, Pyke, Qiyana, Quinn, Rakan, Rammus, Rek'Sai, Rell, Renata Glasc, Renekton, Rengar, Riven, Rumble, Ryze, Samira, Sejuani, Senna, Seraphine, Sett, Shaco, Shen, Shyvana, Singed, Sion, Sivir, Skarner, Smolder, Sona, Soraka, Swain, Sylas, Syndra, Tahm Kench, Taliyah, Talon, Taric, Teemo, Thresh, Tristana, Trundle, Tryndamere, Twisted Fate, Twitch, Udyr, Urgot, Varus, Vayne, Veigar, Vel'Koz, Vex, Vi, Viego, Viktor, Vladimir, Volibear, Warwick, Wukong, Xayah, Xerath, Xin Zhao, Yasuo, Yone, Yorick, Yuumi, Zac, Zed, Zeri, Ziggs, Zilean, Zoe, Zyra

Correct any possible typos of League of Legends champion names or game-specific terms in the following text.
If no corrections are needed, return the original text unchanged. Provide only the corrected or original text without any additional explanations.

For example:

Input Text: "Who is why?"
Corrected Text: "Who is Vi?"

Input Text: "Who is Cathlin?"
Corrected Text: "Who is Caitlyn?"

Input Text: "{text}"

Corrected Text: "
"""
        response = self._invoke_bedrock(prompt, turn_type="Spell Check", system_prompt="", is_stream=False)

        logger.debug(f"Spell check input: {text}")
        logger.debug(f"Spell check response: {response}")
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
    "is_question": boolean,
    "is_about_lol": boolean,
    "explanation": "A brief explanation of your analysis"
}}
"""
        return self._invoke_bedrock(prompt, turn_type="Analysis", system_prompt="", is_stream=False)

    def _chat_with_user(self, text):
        return self._invoke_bedrock(text, turn_type="Chat", system_prompt="You are a friendly AI assistant.", is_stream=True)

    def _solve_question(self, text):
        # Step 1: Analyze if knowledge bases are needed
        # kb_analysis = self._analyze_knowledge_base_need(text)

        # Mock kb_analysis data for testing
        kb_analysis = {
            "kb_needed": True,
            "kb_ids": ["FQYOEZO3D0"],
        }

        # Step 2: Fetch from knowledge bases if needed
        kb_content = self._fetch_from_knowledge_bases(kb_analysis, text) if kb_analysis['kb_needed'] else ""

        # Step 3: Combine question with KB content and solve
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
        return self._invoke_bedrock(enhanced_prompt, turn_type="Question", system_prompt="You are a knowledgeable and enthusiastic League of Legends expert, eager to help players understand the game better.", is_stream=True)

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
            return f"Relevant Knowledge Base Information:\n{formatted_results}"
        return ""

    def _invoke_bedrock(self, prompt, include_context=True, turn_type="Chat", is_stream=False, system_prompt=None):
        context = self.context.context if include_context else None
        body = BedrockModelsWrapper.define_body(prompt, context=context, system_prompt=system_prompt)
        body_json = json.dumps(body)

        logger.debug(f"Invoking Bedrock with prompt: {prompt}")

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
