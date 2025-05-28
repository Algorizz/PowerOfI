import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

nltk.download('stopwords')
nltk.download('punkt_tab')


def clean_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenize
    words = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words and word.isalpha()]

    return ' '.join(filtered_words)

def process_txt_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    cleaned_text = clean_text(raw_text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    print(f"Processed text saved to: {output_path}")

# Example usage
input_txt = 'PowerofI/Output doc/Adani Natural Resources - Proposal from Diya - The Poi - Lumina & Digital Deep Dive.txt'      # your raw txt file
output_txt = 'PowerofI/Processed_docs/Adanitest1.txt'    # file after stopword removal
process_txt_file(input_txt, output_txt)
