from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from MySQLdb import _mysql
import os

load_dotenv()

db = _mysql.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), passwd=os.getenv("DB_PASS"), db=os.getenv("DB_NAME"), charset='utf8')

app = Flask(__name__)
CORS(app)

# Регулируемые параметры маршрутов
app_conf = { 
    # Количество записей на странице списка
    'PAGE_CAPACITY': 10
}

@app.route('/list/<int:page>', methods=['GET'])
def lst(page):
    start = (page - 1) * app_conf['PAGE_CAPACITY']
    db.query("SELECT COUNT(*) from vacancy")
    count = list(db.store_result().fetch_row(maxrows=0, how=1))[0]['COUNT(*)']
    db.query("SELECT * from vacancy, teacher WHERE vacancy.teacher_teacher_id=teacher.teacher_id LIMIT {}, {}".format(start, app_conf['PAGE_CAPACITY']))
    vacancies = db.store_result().fetch_row(maxrows=0, how=1)
    vacancies = map(lambda row: {
        'id': int(row['vacancy_id']),
        'pay': { 'start': int(row['fork_start']), 'end': None if row['fork_end'] is None else int(row['fork_end'])  },
        'title': row['title'].decode('utf8'),
        'age': 1,
        'seniority': 1,
        'short_name': row['short_name'].decode('utf8'),
        'phone_number': row['phone_number'].decode('utf8'),
        'description': row['description'].decode('utf8')
    }, vacancies)
    vacancies = list(vacancies)
    return jsonify({ 'count': int(count), 'list': vacancies })

@app.route('/read/<int:id>', methods=['GET'])
def read(id):
    db.query("SELECT * from vacancy, teacher WHERE vacancy_id={} AND vacancy.teacher_teacher_id=teacher.teacher_id".format(id))
    vacancy = list(db.store_result().fetch_row(maxrows=0, how=1))[0]
    db.query("SELECT s.speciality_id, s.name from speciality AS s, teacher_has_speciality AS ths WHERE ths.teacher_teacher_id={} AND s.speciality_id = ths.speciality_speciality_id".format(int(vacancy['teacher_id']))
    specialities = db.store_result().fetch_row(maxrows=0, how=1)
    specialities = map(lambda row: [int(row['speciality_id']), row['name'].decode("utf-8")], specialities)
    specialities = list(specialities)
    db.query("SELECT s.speciality_id, s.name from speciality AS s")
    all_specialities = db.store_result().fetch_row(maxrows=0, how=1)
    all_specialities = map(lambda row: [int(row['speciality_id']), row['name'].decode("utf-8")], all_specialities)
    all_specialities = list(all_specialities)
    return jsonify({
        'title': vacancy['title'].decode('utf-8'),
        'pay': { 'start': vacancy['fork_start'].decode('utf-8'), 'end': vacancy['fork_end'].decode('utf-8') },
        'seniority': Date.now().year() - int(vacancy['date_of_birth']),
        'career_start': int(vacancy['career_start']),
        'description': vacancy['description'].decode('utf-8'),
        'phone_number': vacancy['phone_number'].decode('utf-8'),
        'email': vacancy['email'].decode('utf-8'),
        'telegram': vacancy['telegram'].decode('utf-8'),
        'full_name': vacancy['full_name'].decode('utf-8'),
        'short_name': vacancy['short_name'].decode('utf-8'),
        'age': Date.now().year() - vacancy['date_of_birth'].year(),
        'date_of_birth': vacancy['date_of_birth'].format("%Y-%m-%d"),
        'about': vacancy['about'],
        'specialities': specialities,
        'all_specialities': all_specialities,
        'teacher_id': int(vacancy['teacher_id'])
    })

@app.route('/specialities', methods=['GET'])
def specialities():
    db.query("SELECT s.speciality_id, s.name from speciality AS s")
    all_specialities = db.store_result().fetch_row(maxrows=0, how=1)
    all_specialities = list(map(lambda v: [int(v['speciality_id']), v['name'].decode("utf-8")], all_specialities))
    return jsonify({ 'all_specialities': all_specialities })

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    db.query("DELETE FROM vacancy WHERE vacancy_id={}".format(id))
    return 'Success', 200

@app.route('/create', methods=['POST'])
def create():
    payload = request.get_json()
    data = payload
    speciality_id = data['speciality_id']

    pay_start = data['pay']['start']
    pay_start = 'NULL' if len(pay_start) == 0 else pay_start 

    pay_end = data['pay']['end']
    pay_start = 'NULL' if len(pay_end) == 0 else pay_end 

    db.query("INSERT INTO teacher VALUES (DEFAULT, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(data['full_name'], data['short_name'], data['date_of_birth'], data['about'], data['career_start'], data['email'], data['telegram']))
    teacher_id = db.store_result().last_id()

    db.query("INSERT INTO vacancy VALUES (DEFAULT, {}, {}, '{}', '{}', {}, {})".format(pay_start, pay_end, data['title'], data['description'], speciality_id, teacher_id))
    vacancy_id = db.store_result().last_id()

    db.query("INSERT INTO teacher_has_speciality VALUES ({}, {})".format(teacher_id, speciality_id))

    return jsonify({ 'id': vacancy_id })

@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    payload = request.get_json()
    data = payload
    vacancy_id = data['vacancy_id']

    pay_start = data['pay']['start']
    pay_start = 'NULL' if len(pay_start) == 0 else pay_start 

    pay_end = data['pay']['end']
    pay_start = 'NULL' if len(pay_end) == 0 else pay_end 

    db.query("UPDATE teacher SET full_name='{}', short_name='{}', date_of_birth='{}', about='{}', career_start='{}', phone_number='{}', email='{}', telegram='{}' WHERE teacher_id={}".format(data['full_name'], data['short_name'], data['date_of_birth'], data['about'], data['career_start'], data['email'], data['telegram']))
    db.query("UPDATE vacancy SET fork_start={}, fork_end={}, title='{}', description='{}', speciality_speciality_id={} WHERE vacancy_id={}".format(pay_start, pay_end, data['title'], data['description'], speciality_id, teacher_id))
    db.query("UPDATE teacher_has_speciality SET speciality_speciality_id={} WHERE teacher_teacher_id={}".format(teacher_id, speciality_id))

    return jsonify({ 'id': vacancy_id })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))