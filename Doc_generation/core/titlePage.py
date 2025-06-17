import requests

class titlePage:
    def __init__(self, api_key, endpoint_url, api_version="2025-01-01-preview"):
        self.api_key = api_key
        self.endpoint = endpoint_url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

    def generate_html(self, context):
        prompt = f"""
Generate a full HTML page with inline CSS that resembles a horizontal title slide. Use the following details:
- Only the logo should be displayed at the top center (logo url: https://powerofi.co.in/wp-content/uploads/2023/01/cropped-cropped-logo3-02-300x221.png)
- Leave a large margin below the logo
- Centered title (bold, teal or dark green)
- Single line Subtitle below the title in italics

context of slide:
{context}

refer this template:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Coaching Proposal</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: Georgia, serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      max-width: 270mm;
      max-height: 170mm;
      background: white;
    }}

    .logo-container {{
      margin-top: 40px;
      text-align: center;
    }}

    .logo-container img {{
      width: 150px;
    }}

    .spacer {{
      height: 100px;
    }}

    .content {{
      text-align: center;
      padding: 0 40px;
    }}

    .content h1 {{
      color: #0a7369;
      font-size: 32px;
      font-weight: bold;
      margin-bottom: 10px;
    }}

    .content p {{
      font-style: italic;
      font-size: 18px;
      color: #000;
    }}
  </style>
</head>
<body>

  <div class="logo-container">
    <img src="https://powerofi.co.in/wp-content/uploads/2023/01/cropped-cropped-logo3-02-300x221.png" alt="Power of i Logo">
  </div>

  <div class="spacer"></div>

  <div class="content">
    <h1>title_text</h1>
    <p>subtitle_text</p>
  </div>

</body>
</html>

*strictly stay with the template above* while generating the html css code
without any explaination return html and embedded CSS and no external dependencies. Keep layout neat, professional, and centered in PPT format
"""
        data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 2000
        }

        response = requests.post(self.endpoint, headers=self.headers, json=data)

        if response.status_code == 200:
            html = response.json()['choices'][0]['message']['content']
            print('✅ title html generated')
            return html
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")