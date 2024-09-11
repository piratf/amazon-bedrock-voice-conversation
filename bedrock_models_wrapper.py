import json
from logger import logger
from config import config, change_model

class BedrockModelsWrapper:
    @staticmethod
    def define_body(text, context=None, system_prompt=None, model_id=None):
        if model_id is not None:
            change_model(model_id)
            logger.info(f"Use model {model_id}, {config['bedrock']['api_request']}")
        model_id = model_id if model_id else config['bedrock']['api_request']['modelId']
        current_model_id = model_id
        model_provider = current_model_id.split('.')[0]
        body = config['bedrock']['api_request']['body'].copy()

        if model_provider == 'amazon':
            body['inputText'] = text
        elif model_provider == 'meta':
            body['prompt'] = text
        elif model_provider == 'anthropic':
            body = BedrockModelsWrapper._prepare_anthropic_body(text, context, body, system_prompt)
        elif model_provider == 'cohere':
            body['prompt'] = text
        else:
            raise Exception('Unknown model provider.')

        return body

    @staticmethod
    def _prepare_anthropic_body(text, context, config_body, system_prompt):
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config_body.get('max_tokens_to_sample', 300),
            "messages": [],
            "temperature": config_body.get('temperature', 1),
            "top_p": config_body.get('top_p', 0.999),
            "top_k": config_body.get('top_k', 250),
            "stop_sequences": config_body.get('stop_sequences', [])
        }

        if system_prompt:
            body["system"] = system_prompt
        elif 'system' in config_body:
            body["system"] = config_body['system']

        if context:
            for turn in context:
                body["messages"].append({"role": "user", "content": turn['user']})
                body["messages"].append({"role": "assistant", "content": turn['assistant']})

        body["messages"].append({"role": "user", "content": text})

        return body

    @staticmethod
    def get_stream_chunk(event):
        return event.get('chunk')

    @staticmethod
    def get_stream_text(chunk):
        model_id = config['bedrock']['api_request']['modelId']
        model_provider = model_id.split('.')[0]

        chunk_obj = ''
        text = ''
        if model_provider == 'amazon':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['outputText']
        elif model_provider == 'meta':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['generation']
        elif model_provider == 'anthropic':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            if 'type' in chunk_obj and chunk_obj['type'] == 'content_block_delta':
                text = chunk_obj.get('delta', {}).get('text', '')
            elif 'type' in chunk_obj and chunk_obj['type'] == 'message_delta':
                text = chunk_obj.get('delta', {}).get('content', [{}])[0].get('text', '')
            else:
                text = ''
        elif model_provider == 'cohere':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = ' '.join([c["text"] for c in chunk_obj['generations']])
        else:
            raise NotImplementedError('Unknown model provider.')

        return text

    @staticmethod
    def get_non_stream_text(response_body):
        model_id = config['bedrock']['api_request']['modelId']
        model_provider = model_id.split('.')[0]

        if model_provider == 'amazon':
            return response_body['results'][0]['outputText']
        elif model_provider == 'meta':
            return response_body['generation']
        elif model_provider == 'anthropic':
            return response_body['content'][0]['text']
        elif model_provider == 'cohere':
            return ' '.join([g['text'] for g in response_body['generations']])
        else:
            raise NotImplementedError('Unknown model provider.')
