import boto3
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor, as_completed
from logger import logger

class BedrockKnowledgeBase:
    def __init__(self):
        self.client = boto3.client('bedrock-agent-runtime')

    def query(self, kb_id, query_text, max_results=20):
        all_results = []
        next_token = None

        while len(all_results) < max_results:
            try:
                kwargs = {
                    'knowledgeBaseId': kb_id,
                    'retrievalQuery': {
                        'text': query_text
                    },
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': min(5, max_results - len(all_results))
                        }
                    }
                }
                if next_token:
                    kwargs['nextToken'] = next_token

                response = self.client.retrieve(**kwargs)

                # Process the results
                for result in response.get('retrievalResults', []):
                    all_results.append({
                        'content': result.get('content', {}).get('text', ''),
                        'score': result.get('score', 0),
                        'source': result.get('location', {}).get('type', 'Unknown')
                    })

                # Check if there are more results
                next_token = response.get('nextToken')
                if not next_token:
                    break  # No more results to retrieve

            except ClientError as e:
                logger.error(f"Error querying knowledge base: {e}")
                break

        return all_results

    def query_all(self, kb_ids, query_text, max_results_per_kb=10):
        all_results = {}

        with ThreadPoolExecutor(max_workers=len(kb_ids)) as executor:
            future_to_kb = {executor.submit(self.query, kb_id, query_text, max_results_per_kb): kb_id for kb_id in kb_ids}
            
            for future in as_completed(future_to_kb):
                kb_id = future_to_kb[future]
                try:
                    results = future.result()
                    all_results[kb_id] = results
                except Exception as exc:
                    print(f'{kb_id} generated an exception: {exc}')

        return all_results

    def format_results(self, results, include_kb_id=False):
        formatted_results = []
        for kb_id, kb_results in results.items():
            for result in kb_results:
                formatted_result = f"Content: {result['content']}\nScore: {result['score']}\nSource: {result['source']}"
                if include_kb_id:
                    formatted_result = f"Knowledge Base: {kb_id}\n{formatted_result}"
                formatted_results.append(formatted_result)
        return "\n---\n".join(formatted_results)

# Example usage
# kb = BedrockKnowledgeBase()
# kb_ids = ['kb1', 'kb2', 'kb3']
# results = kb.query_all(kb_ids, 'What is the capital of France?', max_results_per_kb=5)
# formatted_output = kb.format_results(results, include_kb_id=True)
# print(formatted_output)
