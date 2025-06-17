import requests
import base64

class ImageGenerator:
    def __init__(self):
        self.api_key = "b46942d9305c42d78df6078a465419ae"
        self.endpoint = "https://qrizz-us.openai.azure.com/openai/deployments/dall-e-3/images/generations?api-version=2024-02-01"

    def generate_image_base64(self, prompt, content):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        rule = f"""
        Generate the image for ppt slide.
        Don't make it artistic.
        It should look like a formal image for a proposals document.
        Keep only textual info in the image without any minor graphics
        Keep the text information accurate with proper spellings
        Align the image with this content of the slide:
        {content}

        Image description:
        {prompt}
        """

        data = {
            "prompt": rule,
            "n": 1,
            "size": "1024x1024"
        }

        response = requests.post(self.endpoint, headers=headers, json=data)

        if response.status_code == 200:
            image_url = response.json()["data"][0]["url"]
            image_response = requests.get(image_url)

            if image_response.status_code == 200:
                encoded_string = base64.b64encode(image_response.content).decode("utf-8")
                print(f"✅ Image generated and encoded")
                return f"data:image/png;base64,{encoded_string}"
            else:
                print(f"❌ Failed to download image from URL: {image_response.status_code}")
        else:
            print(f"❌ Failed to generate image: {response.status_code}\n{response.text}")
        return None
    

    