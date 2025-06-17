
def getProfileHtml():
    text = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Background</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            margin: 40px auto;
            max-width: 270mm;
            max-height: 150mm; 
            background: #ffffff;
            color: #0a3171;
            line-height: 1.6;
        }

        h1 {
            color: #1a3e3f;
            margin-bottom: 20px;
            border-bottom: 2px solid #f5b921;
            padding-bottom: 5px;
        }

        .subtitle {
            font-weight: bold;
        }

        .italic {
            font-style: italic;
            font-size: 0.9rem;
        }

        .content {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
        }

        .profile-img {
            width: 150px;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            flex-shrink: 0;
        }

        .text {
            flex: 1;
            min-width: 300px;
            text-align: justify;
        }

        .text p {
            font-size: 1rem;
            margin-bottom: 1em;
        }

        .text strong {
            color: #f5881f;
        }

        a {
            color: #1a3e3f;
            text-decoration: none;
            border-bottom: 1px dotted #f5b921;
        }

        a:hover {
            color: #f5881f;
        }

        .footer {
            margin-top: 60px;
            height: 20px;
            background: linear-gradient(to right, #f5b921, #f5881f, #2f6f73);
            border-radius: 10px;
        }

        @media (max-width: 600px) {
            .content {
                flex-direction: column;
                align-items: center;
            }

            .profile-img {
                width: 120px;
            }

            .text {
                text-align: left;
            }
        }
    </style>
</head>
<body>

    <h1>My Background</h1>

    <div class="content">
        <img src="https://powerofi.co.in/wp-content/uploads/2023/01/Diya-Kapur-Misra-Leadership-coach-1.png" alt="Diya Kapur Misra" class="profile-img">
        <div class="text">
            <p>I am <strong>Diya Kapur Misra</strong>, a <strong>LEADERSHIP IMPACT COACH</strong> and Diversity & Inclusion Champion, based in Mumbai, India.</p>

            <p>Driven by purpose, I strive to leave every situation and individual better for my involvement. My professional journey since 1999 has been diverse—spanning HR, consulting, and entrepreneurship. I've worked with esteemed organizations like Unilever, Hewitt, Cadbury/Kraft Foods, and Korn Ferry.</p>

            <p>Over the years, I have impacted over 2500 leaders across 43+ organizations, gaining deep insights into leadership and business dynamics—especially in today’s BANI world: <em>brittle, anxious, non-linear, and incomprehensible</em>.</p>

            <p>Inspired by my children’s adaptability during the pandemic, I reflected on enabling leaders to thrive, not just survive. This led me to create <strong>THE POWER OF i</strong>, a leadership model combining my professional experiences and personal journey as a parent.</p>

            <p>Learn more about my philosophy and services at <a href="https://powerofi.co.in" target="_blank">powerofi.co.in</a>.</p>

            <p>Clients often describe my approach as offering “the understanding of an insider with the perspective of an outsider.” Read their voices at <a href="https://powerofi.co.in/testimonials/" target="_blank">testimonials</a>.</p>

            <p>I also lead initiatives like <em>up! SURGE – Journey to the C-Suite</em>, and actively contribute to gender equity through XL4W and LinkedIn.</p>

            <p>I’m a double Gold Medallist from XLRI Jamshedpur, and an Economics topper from Delhi University. Outside of work, I’m a mom, writer, singer, traveller, and theatre enthusiast.</p>

            <p>Connect with me via <a href="mailto:diya@powerofi.co.in">email</a> or on <a href="http://linkedin.com/in/diya-kapur-misra-05317" target="_blank">LinkedIn</a>.</p>
        </div>
    </div>

    <div class="footer"></div>

</body>
</html>
"""
    return text

def getCredentialHtml():
    text = """

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Credentials & Collaborations</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            margin: 40px;
            background: white;
            color: #1a3e3f;
            max-width: 270mm;
            max-height: 170mm;
        }

        h1 {
            color: #0a3171;
            margin-top: 30px;
        }

        .subtitle {
            font-weight: bold;
        }

        ul, ol {
            margin-top: 20px;
            list-style-type: none;
            padding-left: 0;
        }

        li {
            margin-bottom: 10px;
        }

        .certifications ul {
            list-style-type: none;
            padding-left: 0;
        }

        .certifications ul {
            list-style-type: circle;
            padding-left: 20px;
        }

        .client-logos {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 30px;
        }

        .client-logos img {
            height: 50px;
            object-fit: contain;
            filter: grayscale(100%);
        }

        .footer {
            margin-top: 40px;
            height: 20px;
            background: linear-gradient(to right, #f5b921, #f5881f, #2f6f73);
        }
    </style>
</head>
<body>

    <h1>Credentials & Collaborations Over Time…</h1>

    <ul>
        <li>Combination of Business HR and Consulting experience in stalwart organisations - HUL, Hewitt, Cadbury/Kraft, and Korn Ferry</li>
        <li>Grown business through collaborations with Korn Ferry, The River Group LLC, Paradox Strategies, and Dr. Linda Hill</li>
        <li>Touched 2500+ leaders across 43+ organisations & 15 industries</li>
        <li>Developed strong client relationships and best-in-class output, resulting in 80% repeat clients and 90% client referrals/endorsement</li>
    </ul>

    <div class="certifications">
        <p class="subtitle">Global Certifications include:</p>
        <ul>
            <li>Innovation Coaching Certificate Program (ICCP) by The Painted Sky, ACSTH (ICF recognised)</li>
            <li>Collective Genius from Dr. Linda Hill, Paradox Strategies, USA</li>
            <li>TalentX7 Learning Agility Assessment from Dr. Kenneth De Meuse, Leader’sGene Consulting</li>
            <li>Coaching Certificate Program, ACTP and Team Coaching by Erickson Coaching International (ICF-recognised)</li>
            <li>Hogan suite from Hogan Assessment Systems</li>
            <li>LSI, GSI and OCI from Human Synergistics</li>
            <li>MBTI from the MBTI Institute</li>
        </ul>
    </div>

    <p>Exploring Advisory Board positions in the Social Impact sector through ISDM and Dasra’s ‘Women on Boards’ program.</p>

    <h2>Clients Include:</h2>
    <div class="client-logos">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTPAWYqoR1E-YMPwd869I0X2WuToOjTrPXgQ&s" alt="TCS">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" alt="Amazon">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/75/Aditya_Birla_Group_Logo.svg/1200px-Aditya_Birla_Group_Logo.svg.png" alt="Aditya Birla">
        <img src="https://dreamdth.com/wp-content/uploads/2019/11/Tata-Sky-logo-scaled.jpg" alt="Tata Sky">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Godrej_Logo.svg/2560px-Godrej_Logo.svg.png" alt="Godrej">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Genpact_logo.svg/1200px-Genpact_logo.svg.png" alt="Genpact">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR4cGB-DsZurpfb2055uRS3GS8ymJLVEEqMjQ&s" alt="Rogers">
        <img src="https://upload.wikimedia.org/wikipedia/en/6/62/Glenmark_Pharmaceuticals_logo.png" alt="Glenmark">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Logo_Gunnebo.gif/1200px-Logo_Gunnebo.gif" alt="Gunnebo">
    </div>

    <div class="footer"></div>

</body>
</html>
"""
    return text




def getThankYouHtml():
    text = """

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Thank You - Power Of I</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            margin: 0;
            padding: 0;
            background-color: #ffffff;
            color: #1a3e3f;
            text-align: center;
        }

        .container {
            padding: 40px 20px;
        }

        .logo {
            width: 120px;
            margin: 30px auto;
        }

        h1 {
            font-size: 48px;
            margin-top: 20px;
            color: #0a3171;
        }

        .contact {
            margin-top: 30px;
            font-size: 18px;
            line-height: 1.8;
        }

        .contact a {
            color: #1a3e3f;
            text-decoration: none;
        }

        .contact a:hover {
            text-decoration: underline;
        }

        .footer {
            margin-top: 60px;
            height: 20px;
            background: linear-gradient(to right, #f5b921, #f5881f, #2f6f73);
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Logo -->
        <img class="logo" src="https://powerofi.co.in/wp-content/uploads/2023/01/cropped-cropped-logo3-02-300x221.png" alt="Power of I Logo">

        <!-- Thank You Message -->
        <h1>Thank You!</h1>

        <!-- Contact Information -->
        <div class="contact">
            <p><strong>Contact Us</strong></p>
            <p><a href="https://www.powerofi.co.in" target="_blank">www.powerofi.co.in</a></p>
            <p><a href="https://www.linkedin.com/in/diya-kapur-misra-05317" target="_blank">linkedin.com/in/diya-kapur-misra-05317</a></p>
            <p><a href="mailto:diya@powerofi.co.in">diya@powerofi.co.in</a></p>
            <p><a href="tel:+919867324627">+91 98673 24627</a></p>
        </div>
    </div>

    <!-- Footer Gradient -->
    <div class="footer"></div>

</body>
</html>
"""
    return text