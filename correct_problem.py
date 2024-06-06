import pdfplumber
import json
import re

def extract_questions_from_pdf(pdf_path):
    questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            question = None
            options = []
            correct_answers = []
            correct_answer_texts = []
            community_vote_distribution = {}
            
            q_f = 1 
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if q_f == 0 and not re.match(r"^[A-F]\.", line):
                    question = question + line + '\n'
                if re.match(r"^Question #\d+ Topic \d+", line):
                    q_f = 0
                    if question:
                        questions.append({
                            "question": question,
                            "options": options,
                            "correct_answers": correct_answers,
                            "correct_answer_texts": correct_answer_texts,
                            "community_vote_distribution": community_vote_distribution
                        })
                    question = ''
                    options = []
                    correct_answers = []
                    correct_answer_texts = []
                    community_vote_distribution = {}
                    continue
                elif re.match(r"^[A-F]\.", line):
                    print(question)
                    q_f = 1
                    options.append(line)
                elif line.startswith("Correct Answer:"):
                    answers = line.split(":")[-1].strip()
                    correct_answers = list(answers)
                    correct_answer_texts = []
                    for ans in correct_answers:
                        index = ord(ans) - ord('A')
                        if 0 <= index < len(options):
                            correct_answer_texts.append(options[index])
                        else:
                            correct_answer_texts.append('')
                elif line.startswith("Community vote distribution"):
                    continue
                elif re.match(r"^\d+", line):
                    if question:
                        questions.append({
                            "question": question,
                            "options": options,
                            "correct_answers": correct_answers,
                            "correct_answer_texts": correct_answer_texts,
                            "community_vote_distribution": community_vote_distribution
                        })
                        question = None
            
            if question:
                questions.append({
                    "question": question,
                    "options": options,
                    "correct_answers": correct_answers,
                    "correct_answer_texts": correct_answer_texts,
                    "community_vote_distribution": community_vote_distribution
                })
    
    return questions

def save_as_json(data, json_path):
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Path to your PDF file
pdf_path = './temp.pdf'

# Extract questions from PDF
questions_data = extract_questions_from_pdf(pdf_path)

# Path to save JSON file
json_path = 'output.json'

# Save extracted questions as JSON
save_as_json(questions_data, json_path)
