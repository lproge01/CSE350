from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

db_access = {
    'host'      : 'localhost',
    'user'      : 'root',
    'password'  : '',
    'database'  : 'cse350'
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_schedule', methods=['GET','POST'])
def generate_schedule():
    if request.method == 'POST':
        
        classes = []
        for i in range(1, 11):
            code = request.form.get(f'class{i}', '').upper()
            pref = request.form.get(f'pref{i}', 'No preference')
            if code:
                classes.append({'code': code, 'pref': pref})

        blocked_times = request.form.getlist('blocked_times')
        core_prefs = request.form.getlist('core_prefs')

        results =[]

        try:
            conn = mysql.connector.connect(**db_access)
            cursor = conn.cursor(dictionary=True)

            for c in classes:
                dept, number = c['code'].split()
                query = """
                SELECT * FROM catalog
                WHERE department = %s AND number = %s
                """
                cursor.execute(query, (dept, number))
                for row in cursor.fetchall():
                    if blocked_times and any(bt in row['time'] for bt in blocked_times):
                        continue
                    if core_prefs and row['card_core'] not in core_prefs:
                        continue
                    results.append(row)

            cursor.close()
            conn.close()

        except mysql.connector.Error as error:
            return f"Database error: {error}"
        
        return render_template('results.html', results=results)
                

if __name__ == '__main__':
    app.run(debug=True)