from openai import AzureOpenAI

# Initialize the Azure OpenAI client
endpoint = "https://qrizz-us.openai.azure.com/"
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint = endpoint,
    api_key="b46942d9305c42d78df6078a465419ae"  
)

def call_llm(prompt: str, deployment_name: str = "gpt-4o"):
    """
    Call Azure OpenAI with the given prompt.
    
    Args:
        prompt: The text prompt to send to the model
        deployment_name: The Azure OpenAI deployment name to use
        
    Returns:
        The text response from the model
    """
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=4096,
        temperature=0.7,
        top_p=1.0,
        model=deployment_name
    )
    
    return response.choices[0].message.content

# print(call_llm("give any authorized source of Secondary data collection for vedic period .", deployment_name="gpt-4o"))