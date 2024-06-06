from app.models import get_subject_collection
from bson import json_util, ObjectId
from flask import Flask, request, jsonify
from datetime import datetime
import pdfplumber
import random
import json
import re



# author:    admin
# create one problem info and save json
# return true or false

# save problem title and json filename in db
def save_subject_db(title, content, filename):
    subject_collection = get_subject_collection()
    db_problem = subject_collection.insert_one({"title": title, "content": content, "filename": filename})
    if db_problem:
        return True
    return False

# 
def save_as_json(data, json_path):
    json_path = f"./build/json/{json_path}"
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        return True
    return False

# extract questions from pdf
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
                elif re.match(r"^[A-F]\.", line):
                    q_f = 1
                    options.append(line)
                elif line.startswith("Correct Answer:"):
                    answers = line.split(":")[-1].strip()
                    correct_answers = [ans for ans in list(answers) if ans.isalpha()]
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

    if len(questions) > 0:
        return True, questions
    else:
        return False, []

# main save json from pdf
def save_subject(title, content):
    local_url = "./build/pdf/temp"
    status, questions = extract_questions_from_pdf(local_url)
    if not status:
        return False
    
    filename = get_random_filename()
    status = save_as_json(questions, filename)
    if not status:
        return False
    status = save_subject_db(title, content, filename)

    if not status:
        return False
    return True




def get_allSubjects():
    subject_collection = get_subject_collection()
    cursor = subject_collection.find()
    data = [doc for doc in cursor]
    for doc in data:
        doc['_id'] = str(doc['_id'])
    return data


# author:   admin
# delete one problem info and delete json
def delete_subject(subject_id):
    subject_collection = get_subject_collection()
    subject_collection.delete_one({"_id": ObjectId(subject_id)})


# get all problems infos
def get_problems_infos():
    subject_collection = get_subject_collection()
    return list(subject_collection.find())

# get exam problem for student
# params:   subject_id, problem_cnt
# return:   json problems
def get_subjects(subject_id, problem_cnt):
    # get one problem info from db
    def get_subject_info(subject_id):
        subject_collection = get_subject_collection()
        return subject_collection.find_one({"_id": ObjectId(subject_id)})

    # get one problem array from local file
    def get_problems_file(filename):
        local_url = f"./build/json/{filename}"
        with open(local_url, "r") as file:
            data = file.read()
            file.close()

        try:
            json_data = json.loads(data)
            return json_data
        except json.JSONDecodeError as e:
            return {}
    
    subject_info = get_subject_info(subject_id)
    db_filename = subject_info["filename"]
    
    prob_list = get_problems_file(db_filename)
    db_totalcnt = len(prob_list)
    if db_totalcnt < int(problem_cnt):
        return parse_json([])
    else:
        problem_nums = get_random_array(db_totalcnt, problem_cnt)
        i = 0
        final_problems = []
        for num in problem_nums:
            final_problems.append(prob_list[num])
        return final_problems

#get random filename
def get_random_filename():
    filename = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return filename

# get json from data
def parse_json(data):
    return json.loads(json_util.dumps(data))

#get random array from total and cnt
def get_random_array(total, cnt):
    return random.sample(range(1, total), cnt)