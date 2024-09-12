import asyncio
import json
import os
import time
import pyaudio
import sys
import boto3
import sounddevice
import traceback
import requests

from concurrent.futures import ThreadPoolExecutor
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream

from config import config, model_id, aws_region
from logger import logger
from bedrock_agent import BedrockAgent
from bedrock_models_wrapper import BedrockModelsWrapper
from src.tools.db_manager import SingletonDatabaseConnection
from reader import Reader
from user_input_manager import UserInputManager

p = pyaudio.PyAudio()
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=config['region'])
polly = boto3.client('polly', region_name=config['region'])
transcribe_streaming = TranscribeStreamingClient(region=config['region'])

def printer(text, level):
    if level == 'info':
        logger.info(text)
    elif level == 'debug':
        logger.debug(text)

class BedrockWrapper:
    def __init__(self):
        self.speaking = False
        self.bedrock_agent = BedrockAgent(bedrock_runtime)

    def is_speaking(self):
        return self.speaking

    def invoke_bedrock(self, text):
        logger.debug('Bedrock generation started')
        self.speaking = True

        body = BedrockModelsWrapper.define_body(text)
        logger.debug(f"Request body: {body}")

        try:
            body_json = json.dumps(body)
            response = bedrock_runtime.invoke_model_with_response_stream(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )

            logger.debug('Capturing Bedrocks response/bedrock_stream')
            bedrock_stream = response.get('body')

            audio_gen = to_audio_generator(bedrock_stream)
            logger.debug('Created bedrock stream to audio generator')

            reader = Reader()
            for audio in audio_gen:
                reader.read(audio)

            reader.close()

        except Exception as e:
            logger.error(e)
            time.sleep(2)
            self.speaking = False

        time.sleep(1)
        self.speaking = False
        logger.debug('Bedrock generation completed')

    def invoke_bedrock_agent(self, text):
        logger.debug('Bedrock Agent processing started')
        self.speaking = True

        try:
            full_text_response = self.bedrock_agent.process_with_tools(text)
            
            logger.debug('Capturing Bedrock Agent response stream')

            self.bedrock_agent.speech_queue.add_text(full_text_response)
            self.bedrock_agent.speech_queue.wait_until_done()

            # Get the full response from the queue
            logger.debug(f"Final question: {text}")
            logger.debug(f"Final response: {full_text_response}")

        except Exception as e:
            logger.exception("An error occurred during Bedrock Agent processing:")
            traceback.print_exc()
            
            if isinstance(e, boto3.exceptions.Boto3Error):
                logger.error("AWS Boto3 related error occurred. Please check your AWS credentials and permissions.")
            elif isinstance(e, json.JSONDecodeError):
                logger.error("JSON decoding error. The response from Bedrock Agent might be malformed.")
            elif isinstance(e, requests.exceptions.RequestException):
                logger.error("Network error occurred. Please check your internet connection.")
            else:
                logger.error(f"An unexpected error occurred: {str(e)}")
            
            time.sleep(2)
            self.speaking = False

        time.sleep(1)
        self.speaking = False
        logger.debug('Bedrock Agent processing completed')

def to_audio_generator(bedrock_stream):
    prefix = ''

    if bedrock_stream:
        for event in bedrock_stream:
            chunk = BedrockModelsWrapper.get_stream_chunk(event)
            if chunk:
                text = BedrockModelsWrapper.get_stream_text(chunk)

                if '.' in text:
                    a = text.split('.')[:-1]
                    to_polly = ''.join([prefix, '.'.join(a), '. '])
                    prefix = text.split('.')[-1]
                    print(to_polly, flush=True, end='')
                    yield to_polly
                else:
                    prefix = ''.join([prefix, text])

        if prefix != '':
            print(prefix, flush=True, end='')
            yield f'{prefix}.'

        print('\n')

def stream_data(stream):
    chunk = 1024
    if stream:
        polly_stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            output=True,
        )

        while True:
            data = stream.read(chunk)
            polly_stream.write(data)

            # If there's no more data to read, stop streaming
            if not data:
                time.sleep(0.5)
                stream.close()
                polly_stream.stop_stream()
                polly_stream.close()
                break
    else:
        # The stream passed in is empty
        pass

def aws_polly_tts(polly_text):
    logger.info(f'Character count: {len(polly_text)}')
    byte_stream_list = []
    polly_text_len = len(polly_text.split('.'))
    logger.debug(f'LEN polly_text_len: {polly_text_len}')
    for i in range(0, polly_text_len, 20):
        logger.debug(f'{i}:{i + 20}')
        polly_text_chunk = '. '.join(polly_text.split('. ')[i:i + 20])
        logger.debug(f'polly_text_chunk LEN: {len(polly_text_chunk)}')

        response = polly.synthesize_speech(
            Text=polly_text_chunk,
            Engine=config['polly']['Engine'],
            LanguageCode=config['polly']['LanguageCode'],
            VoiceId=config['polly']['VoiceId'],
            OutputFormat=config['polly']['OutputFormat'],
        )
        byte_stream = response['AudioStream']
        byte_stream_list.append(byte_stream)

    byte_chunks = []
    chunk = 1024
    for bs in byte_stream_list:
        while True:
            data = bs.read(chunk)
            byte_chunks.append(data)

            if not data:
                bs.close()
                break

    read_byte_chunks(b''.join(byte_chunks))

def read_byte_chunks(data):
    polly_stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    polly_stream.write(data)

    time.sleep(1)
    polly_stream.stop_stream()
    polly_stream.close()
    time.sleep(1)

class EventHandler(TranscriptResultStreamHandler):
    text = []
    last_time = 0
    sample_count = 0
    max_sample_counter = 20

    def __init__(self, transcript_result_stream: TranscriptResultStream, bedrock_wrapper):
        super().__init__(transcript_result_stream)
        self.bedrock_wrapper = bedrock_wrapper

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        if not self.bedrock_wrapper.is_speaking():
            if results:
                for result in results:
                    EventHandler.sample_count = 0
                    if not result.is_partial:
                        for alt in result.alternatives:
                            logger.info(f"Transcribed: {alt.transcript}")
                            EventHandler.text.append(alt.transcript)

            else:
                EventHandler.sample_count += 1
                if EventHandler.sample_count == EventHandler.max_sample_counter:

                    if len(EventHandler.text) == 0:
                        EventHandler.sample_count = 0
                    else:
                        input_text = ' '.join(EventHandler.text)
                        logger.info(f"User input: {input_text}")

                        executor = ThreadPoolExecutor(max_workers=1)
                        UserInputManager.set_executor(executor)
                        loop.run_in_executor(
                            executor,
                            self.bedrock_wrapper.invoke_bedrock_agent,
                            input_text
                        )

                    EventHandler.text.clear()
                    EventHandler.sample_count = 0

class MicStream:

    async def mic_stream(self):
        loop = asyncio.get_event_loop()
        input_queue = asyncio.Queue()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

        stream = sounddevice.RawInputStream(
            channels=1, samplerate=16000, callback=callback, blocksize=2048 * 2, dtype="int16")
        with stream:
            while True:
                indata, status = await input_queue.get()
                yield indata, status

    async def write_chunks(self, stream):
        async for chunk, status in self.mic_stream():
            await stream.input_stream.send_audio_event(audio_chunk=chunk)

        await stream.input_stream.end_stream()

    async def basic_transcribe(self):
        loop.run_in_executor(ThreadPoolExecutor(max_workers=1), UserInputManager.start_user_input_loop)

        stream = await transcribe_streaming.start_stream_transcription(
            language_code=config['polly']['TranscribeLanguageCode'],
            media_sample_rate_hz=16000,
            media_encoding=config['polly']['OutputFormat'],
        )

        handler = EventHandler(stream.output_stream, BedrockWrapper())
        await asyncio.gather(self.write_chunks(stream), handler.handle_events())

if __name__ == "__main__":
    info_text = f'''
*************************************************************
Welcome to your League of Legends Voice Chat Game Partner!

I'm here to assist you with all things League of Legends.
Whether you need strategy advice, champion information,
or just want to chat about the game, I'm ready to help!

To start talking, simply speak into your microphone.
I'll listen and respond to your questions and comments.

Remember:
- Hit ENTER at any time to interrupt me if needed.
- After interrupting, you can continue speaking as normal.

Let's dive into the world of League of Legends together!
What would you like to talk about?
*************************************************************
'''
    print(info_text)

    # Initialize the database connection
    db = SingletonDatabaseConnection()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(MicStream().basic_transcribe())
    except (KeyboardInterrupt, Exception) as e:
        if isinstance(e, KeyboardInterrupt):
            logger.info("KeyboardInterrupt detected. Exiting gracefully...")
        else:
            logger.error(f"An unexpected error occurred: {str(e)}")
    
        # Cleanup and exit
        if UserInputManager.is_executor_set():
            UserInputManager.start_shutdown_executor()
        
        logger.info("Exiting...")
