from collections import deque
import json

class ConversationContext:
    def __init__(self, max_turns=5):
        self.context = deque(maxlen=max_turns)

    def add_turn(self, turn_type, system_prompt, user_input, assistant_message):
        self.context.append({
            "type": turn_type,
            "system": system_prompt,
            "user": user_input,
            "assistant": assistant_message
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
