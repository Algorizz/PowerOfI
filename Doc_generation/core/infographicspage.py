import requests

class InfoGraphicsPage:
    def __init__(self, api_key, endpoint_url, api_version="2025-01-01-preview"):
        self.api_key = api_key
        self.endpoint = endpoint_url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

    def generate_html(self, context):
       

        prompt = f"""
        Create a visually clean, HTML slide-style layout with a flowchart that shows a methodology.
        - Main title 
        - Subtitle 
        - Make sure the flowchart fits properly in the page
        - Make sure the flowchart is small and desent in size, with small font
    
        context of the slide:
        {context}

        Refer this style sheet and html template:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Proposed Solution</title>
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      margin: 0;
      padding: 1rem;
      background: white;
      max-width: 270mm;
      max-height: 170mm;
    }}

    .container {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      border-radius: 12px;
      padding: 1rem;
      background: linear-gradient(135deg, #f0f8ff, #e6f7ff);
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    .title {{
      font-size: 2rem;
      font-weight: bold;
      color: #003366;
      border-left: 5px solid #00b0f0;
      padding-left: 10px;
    }}

    .section {{
      font-size: 1.1rem;
      color: #555;
      margin-bottom: 0.5rem;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
    }}

    .card {{
      background: white;
      border-left: 6px solid #00bcd4;
      border-radius: 10px;
      padding: 1rem;
      box-shadow: 0 3px 8px rgba(0,0,0,0.05);
      transition: transform 0.3s;
    }}

    .card:hover {{
      transform: scale(1.02);
    }}
    .card h3 {{
      margin-top: 0;
      font-size: 1.1rem;
      color: #00796b;
    }}

    .card p {{
      font-size: 0.95rem;
      color: #333;
    }}

    .image-placeholder {{
      margin-top: 1rem;
      height: 150px;
      border: 2px dashed #ccc;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #888;
      font-size: 0.9rem;
    }}

    footer {{
      text-align: right;
      font-size: 0.8rem;
      color: #888;
      margin-top: 1rem;
      border-top: 1px solid #ddd;
      padding-top: 0.5rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="section">Agenda / Solution Overview</div>
    <div class="title">Proposed Solution</div>

    <div class="grid">
      <div class="card">
        <h3>Digital Leadership Diagnostics</h3>
        <p>Identify strengths and areas for improvement to lead digital transformation effectively.</p>
      </div>
      <div class="card">
        <h3>Behavioral Coaching</h3>
        <p>Develop key leadership behaviors tailored for driving digital change.</p>
      </div>
      <div class="card">
        <h3>Competency-Based Learning</h3>
        <p>Structured journeys to build innovation, execution, and resilience capabilities.</p>
      </div>
      <div class="card">
        <h3>Custom LMS Plugin</h3>
        <p>Role-based nudges and behavioral assignments to reinforce learning.</p>
      </div>
      <div class="card">
        <h3>JSW Competency Dictionary</h3>
        <p>Embed essential behaviors into daily routines using a structured framework.</p>
      </div>
    </div>

    <div class="image-placeholder">
      [Diagram Placeholder: Key Components & Interconnections]
    </div>

    <footer>
      Slide Type: Solution Overview
    </footer>
  </div>
</body>
</html>


        *strictly stay with the template* above while generating the html css code
        *do not add any box to show image instead use context above to create a flowchart with using above template*
        *strictly use colours in the flowchart* 
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
            print('✅ methodology with infographics html generated')
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")