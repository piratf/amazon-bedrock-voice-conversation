import os
from api_request_schema import api_request_list, get_model_ids

model_id = os.getenv('MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
aws_region = os.getenv('AWS_REGION', 'ap-northeast-1')

if model_id not in get_model_ids():
    raise ValueError(f'Error: Models ID {model_id} is not a valid model ID. Set MODEL_ID env var to one of {get_model_ids()}.')

api_request = api_request_list[model_id]

config = {
    'log_level': 'debug',  # One of: info, debug, none
    'last_speech': "If you have any other questions, please don't hesitate to ask. Have a great day!",
    'region': aws_region,
    'polly': {
        'Engine': 'neural',
        'TranscribeLanguageCode': 'zh-CN',
        'LanguageCode': 'cmn-CN',
        'VoiceId': 'Zhiyu',
        'OutputFormat': 'pcm',
        'speed': '110%',
    },
    'translate': {
        'SourceLanguageCode': 'en',
        'TargetLanguageCode': 'en',
    },
    'bedrock': {
        'response_streaming': True,
        'api_request': api_request
    }
}

def change_model(model_id):
    config['bedrock']['api_request'] = api_request_list[model_id]