
import requests
class CircularInfoGraphicsPage:
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
  <title>Proposed Solution - Colorful Version</title>
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
      background: linear-gradient(135deg, #fdfbfb, #ebedee);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}

    .title {{
      font-size: 2rem;
      font-weight: bold;
      color: #222;
      border-left: 5px solid #4a90e2;
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
      border-radius: 12px;
      box-shadow: 0 3px 10px rgba(0,0,0,0.05);
      overflow: hidden;
      transition: transform 0.3s;
    }}

    .card:hover {{
      transform: translateY(-3px);
    }}

    .card-header {{
      padding: 0.7rem 1rem;
      font-size: 1.1rem;
      font-weight: bold;
      color: white;
    }}

    .card-body {{
      padding: 0.8rem 1rem;
    }}

    .card-body p {{
      font-size: 0.95rem;
      color: #333;
      margin: 0;
    }}

    /* Unique colors for each card header */
    .c1 {{ background: linear-gradient(to right, #42a5f5, #1e88e5); }}
    .c2 {{ background: linear-gradient(to right, #66bb6a, #43a047); }}
    .c3 {{ background: linear-gradient(to right, #ffa726, #fb8c00); }}
    .c4 {{ background: linear-gradient(to right, #ab47bc, #8e24aa); }}
    .c5 {{ background: linear-gradient(to right, #ef5350, #e53935); }}

    .image-placeholder {{
      margin-top: 1rem;
      height: 150px;
      border: 2px dashed #ccc;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #999;
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
        <div class="card-header c1">Digital Leadership Diagnostics</div>
        <div class="card-body">
          <p>Identify strengths and areas for improvement to lead digital transformation effectively.</p>
        </div>
      </div>
      <div class="card">
        <div class="card-header c2">Behavioral Coaching</div>
        <div class="card-body">
          <p>Develop key leadership behaviors tailored for driving digital change.</p>
        </div>
      </div>
      <div class="card">
        <div class="card-header c3">Competency-Based Learning</div>
        <div class="card-body">
          <p>Structured journeys to build innovation, execution, and resilience capabilities.</p>
        </div>
      </div>
      <div class="card">
        <div class="card-header c4">Custom LMS Plugin</div>
        <div class="card-body">
          <p>Role-based nudges and behavioral assignments to reinforce learning.</p>
        </div>
      </div>
      <div class="card">
        <div class="card-header c5">JSW Competency Dictionary</div>
        <div class="card-body">
          <p>Embed essential behaviors into daily routines using a structured framework.</p>
        </div>
      </div>
    </div>

    <div class="image-placeholder">
      [Diagram Placeholder: Components & Interconnections]
    </div>

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
            print('✅ Infographics html generated')
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
