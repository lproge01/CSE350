from flask import Flask, render_template, request
import mysql.connector
from itertools import product
import re
from datetime import datetime

app = Flask(__name__)

db_access = {
    'host'      : 'localhost',
    'user'      : 'root',
    'password'  : '',
    'database'  : 'cse350'
}

DAY_MAP = {
    'Mo' : 'Mon', 'Tu' : 'Tue', 'We' : 'Wed', 
    'Th' : 'Thu', 'Fr' : 'Fri', 'Sa' : 'Sat', 'Su' : 'Sun'
}

def time_to_minutes(t):
    t = t.strip().upper()
    try:
        return int(datetime.strptime(t, "%I:%M%p").hour) * 60 + int(datetime.strptime(t, "%I:%M%p").minute)
    except ValueError:
        return int(datetime.strptime(t, "%I %p").hour) * 60

def parse_time(time_str):
    if not time_str.strip():
        return []
    
    match = re.match(r'([A-Za-z]+)\s+(\d{1,2}:\d{2}[APMapm]+)\s*-\s*(\d{1,2}:\d{2}[APMapm]+)', time_str.strip())
    if not match:
        return []
    
    days_str, start_time_str, end_time_str, = match.groups()

    days = re.findall(r'(Mo|Tu|We|Th|Fr|Sa|Su)', days_str)

    start_minutes = time_to_minutes(start_time_str)
    end_minutes = time_to_minutes(end_time_str)

    return [(DAY_MAP[d], start_minutes, end_minutes) for d in days]

def times_conflict(t1, t2):
    blocks1 = parse_time(t1)
    blocks2 = parse_time(t2)

    for day1, s1, e1, in blocks1:
        for day2, s2, e2, in blocks2:
            if day1 == day2 and not (e1 <= s2 or s1 >= e2):
                return True
    return False

def has_conflict(schedule):
    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            t1 = schedule[i]['time']
            t2 = schedule[j]['time']
            if t1 and t2 and times_conflict(t1, t2):
                return True
    return False

def satis_prefs(row, blocked_times):
    class_blocks = parse_time(row.get('time', ''))
    for cb in class_blocks:
        print(cb)

    blocked_ranges = []
    for bt in blocked_times:
        print(bt)
        try:
            bt_clean = bt.strip().upper()
            bt_start = time_to_minutes(bt_clean)
            bt_end = bt_start + 60
            blocked_ranges.append((bt_start, bt_end))
        except Exception:
            continue

    for _, class_start, class_end in class_blocks:
        for bt_start, bt_end in blocked_ranges:
            if class_start < bt_end and class_end > bt_start:
                return False

    return True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    
    classes = []
    excluded_classes = []
    for i in range(1, 11):
        code = request.form.get(f'class{i}', '').upper()
        pref = request.form.get(f'pref{i}', 'No preference')
        if code:
            parts = code.split()
            if len(parts) != 2:
                excluded_classes.append(f"{parts} {''}: not found")
                continue
            dept, num = parts
            classes.append({'dept': dept.upper(), 'num' : num, 'pref': pref})

    blocked_times = request.form.getlist('blocked_times')
    core_prefs = request.form.getlist('core_prefs')

    course_options = []

    conn = mysql.connector.connect(**db_access)
    cursor = conn.cursor(dictionary=True)

    if core_prefs:
        for pref in core_prefs:
            if pref in ('S', 'B'):
                query = "SELECT * FROM catalog WHERE card_core = %s"
                param = (pref,)
            else:
                query = "SELECT * FROM catalog WHERE card_core LIKE %s"
                param = (f"%{pref}%",)

            cursor.execute(query, param)
            core_classes = cursor.fetchall()
            core_classes = [c for c in core_classes if satis_prefs(c, blocked_times)]

            if core_classes:
                course_options.append(core_classes)
            else:
                excluded_classes.append(f"No available courses for core requirement '{pref}'")


    for course in classes:
        query = """
        SELECT * FROM catalog
        WHERE department = %s AND number = %s
        """
        
        cursor.execute(query, (course['dept'], course['num']))
        sections = cursor.fetchall()

        if not sections:
            excluded_classes.append(f"{course['dept']} {course['num']}: not found")
            continue

        #filter by location/online
        if course['pref'] != 'No preference':
            filtered = [s for s in sections if s['location'].lower() == course['pref'].lower()]
            if course['pref'] == "In-person":
                filtered = [s for s in sections if s['location'].lower() != 'online']
            if not filtered:
                excluded_classes.append(f"{course['dept']} {course['num']}: preference '{course['pref']}' not available")
                continue
            sections = filtered

        #filter blocked times
        filtered = [s for s in sections if satis_prefs(s, blocked_times)]
        if not filtered:
            excluded_classes.append(f"{course['dept']} {course['num']}: only in blocked times")
            continue

        course_options.append(filtered)

    cursor.close()
    conn.close()

    print("course options", course_options)
    if not course_options:
        return render_template('results.html', results=[])
    
    all_combos = product(*course_options)

    valid_schedules = []
    for combo in all_combos:
        if not has_conflict(combo):
            valid_schedules.append(combo)

    return render_template('results.html', results=valid_schedules, excluded=excluded_classes)
                

if __name__ == '__main__':
    app.run(debug=True)
