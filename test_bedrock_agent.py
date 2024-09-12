from app import BedrockWrapper
from config import config
from logger import logger


def test_invoke_bedrock_agent():
    # Create an instance of BedrockWrapper
    bedrock_wrapper = BedrockWrapper()

    # Test inputs
    test_inputs = [
        # "What are the best champions for beginners in League of Legends?",
        # "Can you tell me more about one of those champions?",
        # "What items should I build for that champion?",
        # "How do I improve my last-hitting skills?",
        # "Thank you for your help!"
        "I want to know about jax's story and spells",
        "What items should I build for jax?",
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n--- Round {i} ---")
        print(f"User: {test_input}")
        
        # Call invoke_bedrock_agent
        response = bedrock_wrapper.invoke_bedrock_agent(test_input)
        
        # Print the response
        print(f"Assistant: {response}")

    print("\nTest completed. Check the logs for detailed output.")

if __name__ == "__main__":
    test_invoke_bedrock_agent()
