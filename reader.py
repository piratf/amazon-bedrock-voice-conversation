import time
import pyaudio
import boto3
from config import config
from logger import logger
from user_input_manager import UserInputManager

class Reader:
    def __init__(self):
        self.polly = boto3.client('polly', region_name=config['region'])
        self.p = pyaudio.PyAudio()
        self.audio = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
        self.chunk = 1024

    def read(self, text, text_type='text'):
        logger.debug(f'text to speech: {text}, type: {text_type}')
        response = self.polly.synthesize_speech(
            Text=text,
            TextType=text_type,
            Engine=config['polly']['Engine'],
            LanguageCode=config['polly']['LanguageCode'],
            VoiceId=config['polly']['VoiceId'],
            OutputFormat=config['polly']['OutputFormat'],
        )

        stream = response['AudioStream']

        while True:
            # Check if user signaled to shutdown Bedrock speech
            # UserInputManager.start_shutdown_executor() will raise Exception. If not ideas but is functional.
            if UserInputManager.is_executor_set() and UserInputManager.is_shutdown_scheduled():
                UserInputManager.start_shutdown_executor()

            data = stream.read(self.chunk)
            self.audio.write(data)
            if not data:
                break

    def close(self):
        time.sleep(1)
        self.audio.stop_stream()
        self.audio.close()
        self.p.terminate()