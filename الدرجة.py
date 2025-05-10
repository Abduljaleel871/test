from flask import Flask, render_template_string, request

app = Flask(__name__)

# القاموس مع المفاتيح المركبة (صفة + شهادة) أو فقط الصفة إذا لا تتطلب شهادة
job_grades = {
    'مستشار طبي أول': {'درجة': 12, 'علاوة': 0, 'requires_degree': False},
    'أخصائي طبي أول': {'درجة': 11, 'علاوة': 1, 'requires_degree': False},
    'أخصائي طبي ثان دكتوراه': {'درجة': 10, 'علاوة': 2, 'requires_degree': True},
    'أخصائي طبي ثان ماجستير': {'درجة': 10, 'علاوة': 1, 'requires_degree': True},
    'طبيب أول دكتوراه': {'درجة': 10, 'علاوة': 0, 'requires_degree': True},
    'طبيب أول ماجستير': {'درجة': 9, 'علاوة': 2, 'requires_degree': True},
    'طبيب ثان': {'درجة': 9, 'علاوة': 0, 'requires_degree': False},
    'طبيب ثالث بكالوريوس طب وجراحة': {'درجة': 8, 'علاوة': 3, 'requires_degree': True},
    'طبيب ثالث بكالوريوس طب وجراحة الفم والأسنان': {'درجة': 8, 'علاوة': 2, 'requires_degree': True},
    'طبيب ثالث بكالوريوس صيدلة': {'درجة': 8, 'علاوة': 1, 'requires_degree': True},
    'كبير الفنيين': {'درجة': 10, 'علاوة': 2, 'requires_degree': False},
    'فني صحي أول بكالوريوس/دبلوم عالي': {'درجة': 9, 'علاوة': 2, 'requires_degree': True},
    'فني صحي أول دبلوم متوسط': {'درجة': 8, 'علاوة': 2, 'requires_degree': True},
    'فني صحي ثان بكالوريوس/دبلوم عالي': {'درجة': 8, 'علاوة': 0, 'requires_degree': True},
    'فني صحي ثان دبلوم متوسط': {'درجة': 7, 'علاوة': 2, 'requires_degree': True},
    'فني صحي ثالث': {'درجة': 6, 'علاوة': 3, 'requires_degree': False},
    'فني صحي رابع': {'درجة': 6, 'علاوة': 0, 'requires_degree': False},
    'معاون صحي أول': {'درجة': 4, 'علاوة': 0, 'requires_degree': False},
    'معاون صحي ثان': {'درجة': 3, 'علاوة': 2, 'requires_degree': False},
    'معاون صحي ثالث': {'درجة': 2, 'علاوة': 2, 'requires_degree': False},
    'معاون صحي رابع': {'درجة': 1, 'علاوة': 0, 'requires_degree': False}
}

MAX_GRADE = 12

# قائمة الصِفات الوظيفية (مفاتيح بدون الشهادة)
job_categories = sorted(set([key.split()[0] + (' ' + key.split()[1] if len(key.split()) > 1 else '') for key in job_grades.keys()]))

# قائمة الشهادات العلمية المتكررة في القاموس
degrees_list = sorted(set([
    'دكتوراه',
    'ماجستير',
    'بكالوريوس طب وجراحة',
    'بكالوريوس طب وجراحة الفم والأسنان',
    'بكالوريوس صيدلة',
    'بكالوريوس/دبلوم عالي',
    'دبلوم عالي',
    'دبلوم متوسط',
    ''
]))

# دالة لبناء المفتاح في القاموس بناءً على الفئة والشهادة
def build_key(category, degree):
    # بعض الفئات تتطلب شهادة مرفقة
    # نبحث أولاً عن المفتاح الكامل category + degree
    full_key = f"{category} {degree}".strip()
    if full_key in job_grades:
        return full_key
    # إذا لم تتطلب الشهادة أو المفتاح الكامل غير موجود، نبحث بالمجرد category
    if category in job_grades:
        return category
    # محاولة أخرى: بعض الفئات في القاموس تحتوي على كلمات أكثر، نجرب تطابق يبدأ بالمجرد category
    for key in job_grades.keys():
        if key.startswith(category):
            return key
    return None

def get_job_grade(category, degree, years):
    key = build_key(category, degree)
    if key is None:
        return None
    base_grade = job_grades[key]['درجة']
    base_allowance = job_grades[key]['علاوة']
    
    promotions = years // 4
    final_grade = base_grade + promotions
    if final_grade > MAX_GRADE:
        final_grade = MAX_GRADE
    
    total_allowance = base_allowance + years
    
    return {
        'الدرجة الوظيفية': final_grade,
        'العلاوات': total_allowance,
        'سنوات العمل': years,
        'ملاحظة': 'تم احتساب علاوة سنوية والانتقال للدرجة التالية بعد كل 4 سنوات'
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>حساب الدرجة الوظيفية والعلاوات</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            direction: rtl;
            padding: 20px;
            background: #f9f9f9;
            margin: 0;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px #ccc;
            box-sizing: border-box;
        }
        label {
            display: block;
            margin-top: 15px;
        }
        select, input {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            box-sizing: border-box;
            font-size: 1em;
        }
        button {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        button:hover {
            background: #0056b3;
        }
        .result, .error {
            padding: 15px;
            margin-top: 20px;
            border-radius: 5px;
            font-size: 1em;
        }
        .result {
            background: #e9ffe9;
            border: 1px solid #4CAF50;
        }
        .error {
            background: #ffe9e9;
            border: 1px solid #f44336;
        }
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            .container {
                padding: 15px;
            }
            button {
                font-size: 0.9em;
            }
            select, input {
                font-size: 0.9em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>حاسبة الدرجة الوظيفية والعلاوات</h2>
        <form method="post">
            <label for="category">اختر الصفة الوظيفية:</label>
            <select name="category" id="category" onchange="toggleDegree()" required>
                <option value="">-- اختر --</option>
                {% for cat in job_categories %}
                <option value="{{ cat }}" {% if cat == selected_category %}selected{% endif %}>{{ cat }}</option>
                {% endfor %}
            </select>

            <div id="degreeDiv" style="margin-top:15px;">
                <label for="degree">اختر نوع الشهادة العلمية (إذا كانت مطلوبة):</label>
                <select name="degree" id="degree">
                    <option value="">-- لا يوجد --</option>
                    {% for deg in degrees_list %}
                    <option value="{{ deg }}" {% if deg == selected_degree %}selected{% endif %}>{{ deg }}</option>
                    {% endfor %}
                </select>
            </div>

            <label for="years">أدخل عدد سنوات العمل:</label>
            <input type="number" id="years" name="years" min="0" value="{{ years or '' }}" required>

            <button type="submit">احسب</button>
        </form>

        {% if result %}
            <div class="result">
                <h3>النتيجة:</h3>
                <p>الدرجة الوظيفية: {{ result['الدرجة الوظيفية'] }}</p>
                <p>عدد العلاوات: {{ result['العلاوات'] }}</p>
                <p>سنوات العمل: {{ result['سنوات العمل'] }}</p>
                <p><em>{{ result['ملاحظة'] }}</em></p>
            </div>
        {% elif error %}
            <div class="error">
                <p>{{ error }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_category = None
    selected_degree = ''
    years = None
    result = None
    error = None

    if request.method == 'POST':
        selected_category = request.form.get('category', '').strip()
        selected_degree = request.form.get('degree', '').strip()
        years_str = request.form.get('years', '').strip()

        if not selected_category:
            error = "يرجى اختيار الصفة الوظيفية."
        elif not years_str.isdigit() or int(years_str) < 0:
            error = "يرجى إدخال عدد سنوات عمل صحيح (صفر أو أكثر)."
        else:
            years = int(years_str)
            res = get_job_grade(selected_category, selected_degree, years)
            if res is None:
                error = "لم يتم العثور على بيانات للفئة والمؤهل المدخلين."
            else:
                result = res

    return render_template_string(HTML_TEMPLATE,
                                  job_categories=job_categories,
                                  degrees_list=degrees_list,
                                  selected_category=selected_category,
                                  selected_degree=selected_degree,
                                  years=years,
                                  result=result,
                                  error=error)

if __name__ == '__main__':
    app.run(debug=True)

