import requests

class pointOfViewPage:
    def __init__(self, api_key, endpoint_url, api_version="2025-01-01-preview"):
        self.api_key = api_key
        self.endpoint = endpoint_url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

    def generate_html(self, context):

        prompt = f"""
        Generate a professional, slide-like HTML page with inline CSS that includes:
        - Title 
        - Subtitle 
        - Bulltet points (bullet icons should be close to text)
        - try to keep it in single page with good formating
        
        context of the slide:
        {context}

        Refer this template:
        <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Point of View on Coaching</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            margin: 40px;
            background: white;
            color: #1a3e3f;
            max-width: 270mm;
            max-height: 170mm;
        }}
        
        h1 {{
            color: #0a3171;
            margin-top: 30px;
        }}
        .subtitle {{
            font-weight: bold;
        }}
        .italic {{
            font-style: italic;
        }}
        ol {{
            margin-top: 20px;
            list-style-type: none;
            padding-left: 0;
        }}
        li {{
            margin-bottom: 20px;
            list-style-type: none;
            padding-left: 0;
        }}
        .footer {{
            margin-top: 40px;
            height: 20px;
            background: linear-gradient(to right, #f5b921, #f5881f, #2f6f73);
        }}
        
    </style>
</head>
<body>


    <h1>My Point of View on Coaching</h1>
    <p class="subtitle">My unique proposition is <strong>IMPACT COACHING</strong> – enabling leaders to have a positive, sustainable impact</p>
    <p class="italic">
        Based on my experience over the last twenty-five years, and the insights I have garnered, I believe that:
    </p>

    <ol>
        <li><strong>Understanding and Connecting with the CONTEXT is key to Effective Coaching</strong>
            <ul>
                <li class="bullet">A leader’s role and impact are always within a context. Understanding the context well is crucial for the Coach at the start of the journey</li>
                <li class="bullet">Coaching in a vacuum doesn’t work. It is important to build subtle connects with the leader’s team/stakeholders/organization</li>
            </ul>
        </li>

        <li><strong>Alignment on the RIGHT GOAL(S) is crucial</strong>
            <ul>
                <li class="bullet">In organization-sponsored coaching, the goal(s) must be relevant to the organization AND truly matter to the Coachee</li>
                <li class="bullet">Investing time upfront in determining the goal(s) is needed; Openness to adjust and realign these as the journey progresses is also important</li>
            </ul>
        </li>

        <li><strong>Effective Coaching leverages both, ART & SCIENCE</strong>
            <ul>
                <li class="bullet">The science comes from high quality assessments, a structured process, and effective coaching tools</li>
                <li class="bullet">The art lies in the Coach’s style, trust and rapport built with the Coachee, and drawing useful insights from stakeholder feedback</li>
            </ul>
        </li>

        <li><strong>The Coaching journey over time must be INSIDE OUT & OUTSIDE IN</strong>
            <ul>
                <li class="bullet">It must help leaders (the coachees) go within, and become more self-aware and reflective</li>
                <li class="bullet">It must then enable them to enhance their influence, inspire others, and create an impact on the ecosystem</li>
            </ul>
        </li>

        <li><strong>CONFIDENTIALITY is NON-COMPROMISABLE</strong>
            <ul>
                <li class="bullet">Once the goals and the process are aligned between the Coach, the Organization and the Coach, coaching conversations are completely confidential, and sharing is the strict prerogative of the Coachee</li>
            </ul>
        </li>
    </ol>

  
</body>
</html>
       

        *strictly stay with the template* above while generating the html css code
        *do not add any box to show image*
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
            print('✅ POV html generated')
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")