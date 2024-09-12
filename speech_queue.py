import queue
import re
import threading
import time
from logger import logger
from reader import Reader

class SpeechQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.reader = Reader()
        self.speaking_thread = threading.Thread(target=self._speak_loop, daemon=True)
        self.speaking_thread.start()

    def add_text(self, text):
        self.queue.put((text))

    def _speak_loop(self):
        last_text_end_time = 0
        while True:
            text = self.queue.get()
            text_type = 'text'
            if '<speak>' in text:
                text_type = 'ssml'
            # if text not begin with <speak>, clear all tag 
            if not text.startswith('<speak>') or not text.endswith('</speak>'):
                logger.error(f"Text contains <spark> but invalid: {text}")
                text = re.sub(r'<[^>]+>', '', text)
            
            current_time = time.time()
            if current_time - last_text_end_time < 1:
                time.sleep(1 - (current_time - last_text_end_time))
            
            self.reader.read(text, text_type)
            last_text_end_time = time.time()
            self.queue.task_done()
            
    def wait_until_done(self):
        self.queue.join()

    def close(self):
        self.reader.close()