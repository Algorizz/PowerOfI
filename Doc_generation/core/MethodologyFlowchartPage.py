import requests

class MethodologyFlowchartPage:
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
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title> Methodology</title>
  <style>
    body {{
  font-family: 'Segoe UI', sans-serif;
  margin: 0;
  padding: 1rem;
  background: #f9f9f9;
  max-width: 270mm;
  max-height: 170mm;
  color: #333;
}}

h1 {{
  text-align: center;
  color: #0a3171;
}}

.subtitle {{
  text-align: center;
  font-style: italic;
  margin-bottom: 1.5rem;
}}
.methodology-container {{
  max-width: 800px;
  margin: 0 auto;
}}

.methodology-flow {{
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.8px;
  background: #ccc;
  border-radius: 10px;
  overflow: hidden;
}}

.step {{
  padding: 1rem;
  background: #fff;
  text-align: center;
}}

.step h2 {{
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}}

.step ul {{
  text-align: left;
  margin-left: 1rem;
  list-style-type: none;
  padding-left: 0;
}}

.rapport {{ background-color: #f9c784; }}
.contract {{ background-color: #f98e8b; }}
.outcome {{ background-color: #fff3b0; }}
.experience {{ background-color: #b5ead7; }}
.action {{ background-color: #d3c0f9; }}
.value {{ background-color: #f7d794; }}
.celebrate {{ background-color: #ffb7b2; }}

.footer {{
  margin-top: 1rem;
  font-size: 0.9rem;
  text-align: center;
  color: #555;
}}
  </style>
</head>
<body>
  <div class="methodology-container">
    <h1>My Methodology</h1>
    <p class="subtitle">(based on Erickson International’s philosophy and approach)</p>
    <div class="methodology-flow">
      <div class="step rapport">
        <h2>Rapport</h2>
        <ul>
          <li>Softeners</li>
          <li>Back tracking</li>
          <li>Open-ended questions</li>
          <li>Recapping</li>
          <li>Appreciation</li>
          <li>Erickson Principles: OK/ATness</li>
          <li>Change is inevitable</li>
        </ul>
      </div>
      <div class="step contract">
        <h2>Set Contract</h2>
        <p>We have ___ minutes. What might be the best possible outcome?</p>
      </div>
      <div class="step outcome">
        <h2>Outcome Frame</h2>
        <p><strong>For today’s session:</strong></p>
        <ul>
          <li>What do you want?</li>
          <li>Why is it important?</li>
          <li>How would you know you got it?</li>
          <li><strong>S.M.A.R.T. Goals</strong></li>
        </ul>
      </div>
      <div class="step experience">
        <h2>Creating an Experience</h2>
        <ul>
          <li>Who else?</li>
          <li>Why? How?</li>
          <li>Where? When?</li>
          <li>Logical Levels</li>
          <li>“As If” Shifts</li>
          <li>Scaling / Wheels</li>
        </ul>
      </div>
      <div class="step action">
        <h2>Action Steps</h2>
        <p>What are your action steps?</p>
      </div>
      <div class="step value">
        <h2>Value</h2>
        <p>How was this of value to you?</p>
      </div>
      <div class="step celebrate">
        <h2>Celebrate</h2>
        <p>Coach appreciates client. 🎉</p>
      </div>
    </div>
    <p class="footer">Rapport, Coach Position, and Solution-Focused Questioning happen throughout. Recontract as necessary.</p>
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
            print('✅ methodology html generated')
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")