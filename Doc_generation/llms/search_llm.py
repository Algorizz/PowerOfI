from openai import OpenAI

class PerplexityResearchAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        self.model = "sonar"

    def run(self, query: str, system_role: str = None, stream: bool = False):
        messages = [
            {
                "role": "system",
                "content": (
                    system_role or
                    "You are an expert research assistant. Answer thoroughly and cite recent web knowledge where possible."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ]

        if stream:
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            for chunk in response_stream:
                print(chunk.choices[0].delta.content or "", end="", flush=True)
            print()
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content

# if __name__ == "__main__":
#     api_key = "---"  # your Perplexity key
#     agent = PerplexityResearchAgent(api_key)

#     query = input("Give your qn:-")
    
#     print("📡 Running non-streamed research...\n")
#     result = agent.run(query)
#     print("🔍 Summary:\n", result)

#     print("\n📡 Running streamed response...\n")
#     agent.run(query, stream=True)
