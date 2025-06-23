from flask import Flask, render_template, request
import csv

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_schedule', methods=['GET','POST'])
def generate_schedule():
    if request.method == 'POST':
        classes = []
        
        for i in range(1, 11):
            class_code = request.form.get(f'class{i}', '').strip()
            pref = request.form.get(f'pref{i}', 'No preference')
            if class_code:
                classes.append({'code': class_code, 'pref': pref})

        blocked_times = request.form.getlist('blocked_times')
        core_prefs = request.form.getlist('core_prefs')

        results = []

        submitted_codes = [c['code'].strip().upper().replace(' ', '') for c in classes]

        with open('catalog.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            for row in reader:
                department = row.get('department','').strip()
                number = row.get('number','').strip()
                row_code = f"{department}{number}".upper()

                if row_code not in submitted_codes:
                    continue
                if any(bt.lower() in row.get('time','').lower() for bt in blocked_times):
                    continue
                if core_prefs:
                    card_core_val = row.get('card_core','').strip()
                    if card_core_val and card_core_val not in core_prefs:
                        continue
                results.append(row)
        
        return render_template('results.html', results=results)
    
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)