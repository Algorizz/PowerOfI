import requests

class fullHtmlGen():
    def __init__(self, api_key, endpoint_url):
        self.api_key = api_key
        self.endpoint = endpoint_url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

    def generate_html(self, full_html):
        text ="""
body {
        font-family: "Georgia", serif;
        margin: 0;
        background: white;
        color: #1a3e3f;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }
      .container {
        border-radius: 18px;
        padding: 48px 40px 36px 40px;
        max-width: 800px;
        width: 100%;
        margin: 40px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
      }
      h1 {
        color: #0a3171;
        margin-top: 0;
        margin-bottom: 18px;
        font-size: 2.2em;
        letter-spacing: 1px;
        text-align: center;
      }
      .subtitle {
        font-weight: bold;
        color: #f5881f;
        font-size: 1.15em;
        margin-bottom: 16px;
        text-align: center;
      }
      .italic {
        font-style: italic;
        color: #2f6f73;
        margin-bottom: 28px;
        text-align: center;
      }
      ol {
        margin-top: 12px;
        padding-left: 22px;
        width: 100%;
      }
      li {
        margin-bottom: 22px;
        font-size: 1.07em;
        line-height: 1.6;
      }
      ul {
        margin-top: 10px;
        margin-bottom: 0;
        padding-left: 22px;
      }
      .bullet {
        color: #1a3e3f;
        font-size: 0.98em;
        margin-bottom: 7px;
      }
      strong {
        color: #0a3171;
      }
      .footer {
        margin-top: 36px;
        height: 8px;
        width: 100%;
        border-radius: 0 0 18px 18px;
        background: linear-gradient(to right, #f5b921, #f5881f, #2f6f73);
      }
      @media (max-width: 800px) {
        .container {
          padding: 28px 10px 20px 10px;
        }
        h1 {
          font-size: 1.3em;
        }
      }
      @media print {
        body,
        html {
          width: 210mm;
          height: 297mm;
          margin: 0;
          padding: 0;
          background: white !important;
        }
        .container {
          box-sizing: border-box;
          width: 190mm;
          min-height: 277mm;
          margin: 0 auto;
          padding: 24mm 10mm 20mm 10mm;
          background: white;
          border-radius: 0;
          box-shadow: none;
        }
        .footer {
          display: none;
        }
      }
      """


        prompt = f"""
        generate a good looking proposal css for below html.

        here is the full HTMl code:
        {full_html}

        refer this style:
        {text}

        
        without any explaination return CSS inside <style> tag and no external dependencies. Keep layout neat, professional 
        """

        data = {
        "messages": [
            {"role": "system", "content": "You are a expert PPT generator using HTML."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 4069
        }

        response = requests.post(self.endpoint, headers=self.headers, json=data)
        if response.status_code == 200:
            html = response.json()['choices'][0]['message']['content']
            print('✅ full css generated')
            return html
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")