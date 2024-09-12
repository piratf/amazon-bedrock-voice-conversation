from collections import deque
import json

from logger import logger


class ConversationContext:
    def __init__(self, max_turns=20):
        self.context = deque(maxlen=max_turns)

    def add_text_turn_v2(self, role, content):
        self.add_content_turn({
            "role": role,
            "content": content
        })

    def get_recent_history(self, num_turns=3):
        # Get the specified number of recent turns, or all turns if less are available
        recent_turns = list(self.context)[-num_turns:]
        
        # Format the turns into a string
        formatted_history = ""
        for turn in recent_turns:
            formatted_history += f"Human: {turn['user']}\n"
            formatted_history += f"AI: {turn['assistant']}\n\n"
        
        return formatted_history.strip()

    def to_json(self):
        return json.dumps(list(self.context))

    @classmethod
    def from_json(cls, json_str):
        context = cls()
        context.context = deque(json.loads(json_str), maxlen=context.context.maxlen)
        return context

    def add_content_turn(self, turn):
        self.context.append(turn)
        self.auto_clean_context()

    def auto_clean_context(self):
        # Ensure the first message always has the "user" role
        while self.context and self.context[0]['role'] != 'user':
            self.context.popleft()
            # If it is a tool_result message, remove it
            if self.context and isinstance(self.context[0]['content'], list) and isinstance(self.context[0]['content'][0], dict) and self.context[0]['content'][0].get('type') == 'tool_result':
                self.context.popleft()
        logger.info(f"Context length: {len(self.context)}")
