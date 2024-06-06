from flask import request, jsonify, redirect, url_for, flash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from app import app
# from app.controllers.auth_controller import authenticate_user, check_admin
from app.controllers.subject_controller import get_subjects, save_subject, get_allSubjects


@app.route('/api/upload', methods = ['POST'])
def upload_file():
    try:
        pdf_file = request.files['file'] 
        pdf_file.save('./build/pdf/temp')
        return jsonify({"status": True, "msg": "Upload Successfully."})
    except Exception as e:
        return jsonify({"status": False, "msg": "Upload Failed."})

@app.route('/api/subjects', methods=['GET'])
# @jwt_required()
def get_Route_Subjects():
    subjects = get_allSubjects()
    return jsonify({"status": True, "msg": "Read Subjects Successfully.", "data": subjects})

@app.route('/api/subjects', methods = ['POST'])
def save_Route_Subject():
    data = request.get_json()
    title = data["title"]
    content = data["content"]

    status = save_subject(title, content)
    if status:
        return jsonify({"status": True, "msg": "Save Successfully."})
    else:
        return jsonify({"status": False, "msg": "Save Failed."})




@app.route('/api/problems', methods=['GET'])
# @jwt_required()
def get_Route_Problems():
    subject_id = request.args.get("_id", None)
    problem_cnt = request.args.get("count", None)
    print(subject_id)
    print(problem_cnt)
    problem_cnt = int(problem_cnt)
    if not subject_id or not problem_cnt:
        return jsonify({"status": False, 'msg': 'Unregistry requests'}), 409
    
    exam_problems = get_subjects(subject_id, problem_cnt)
    if len(exam_problems) == 0:
        return jsonify({"status": False, "msg": "Can't read any problem."})    
    else:
        return jsonify({"status": True, "msg": "Read Problem Successfully.", "data": exam_problems})
