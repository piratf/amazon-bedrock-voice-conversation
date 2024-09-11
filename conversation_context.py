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

    def get_context_string(self):
        context_str = ""
        for turn in self.context:
            if turn['system']:
                context_str += f"System: {turn['system']}\n"
            context_str += f"Human: {turn['user']}\n"
            context_str += f"Assistant: {turn['assistant']}\n\n"
        return context_str

    def to_json(self):
        return json.dumps(list(self.context))

    @classmethod
    def from_json(cls, json_str):
        context = cls()
        context.context = deque(json.loads(json_str), maxlen=context.context.maxlen)
        return context
