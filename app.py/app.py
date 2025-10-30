from flask import Flask, request, render_template, Response, session
from PIL import Image
import os

if os.path.exists("soil_reports.db"):
    os.remove("soil_reports.db")

os.environ['KAGGLE_CONFIG_DIR'] = r'C:\Users\likith\OneDrive\Desktop\crop_recommendation_system\app.py'


import pytesseract, os, sqlite3
saved_reports = []
from database import extract_values, extract_all_numbers, save_to_db
from recommendation import recommend_crops
from market_price import get_crop_price
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'a9f8b7c6d5e4g3h2i1j0k9l8m7n6o5p4'
def init_soil_table():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Drop the table if it exists
    cursor.execute('DROP TABLE IF EXISTS soil_reports')

    # Recreate with correct schema
    cursor.execute('''
        CREATE TABLE soil_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer TEXT,
            location TEXT,
            crop TEXT,
            nitrogen REAL,
            phosphorus REAL,
            potash REAL,
            ph REAL,
            moisture REAL,
            interpretation TEXT
        )
    ''')

    conn.commit()
    conn.close()
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

translations = {
    'en': {
    'title': 'Upload Soil Report',
    'farmer': 'Farmer Name',
    'location': 'Location',
    'crop': 'Intended Crops',
    'month': 'Month of Sowing',
    'upload': 'Upload Soil Report Image',
    'submit': 'Submit',
    'parsed': 'Parsed Values',
    'recommended': 'Recommended Crops with Market Prices',
    'saved': 'View Saved Reports',
    'nitrogen': 'Nitrogen',
    'phosphorus': 'Phosphorus',
    'potash': 'Potash',
    'ph': 'pH',
    'moisture': 'Moisture',
    'months': [
        'January','February','March','April','May','June',
        'July','August','September','October','November','December'
    ],
    'revenue': 'Total Revenue',
    'cost': 'Total Cost',
    'profit': 'Net Profit',
    'break_even': 'Break-even Price',
    'print': 'Print this page',
    'calculator': 'Calculator',
    'yield': 'Yield per hectare (kg)',
    'seed_cost': 'Seed Cost (₹)',
    'fertilizer_cost': 'Fertilizer Cost (₹)',
    'labor_cost': 'Labor Cost (₹)',
    'irrigation_cost': 'Irrigation Cost (₹)',
    'equipment_cost': 'Equipment Cost (₹)',
    'report': 'Report',
    'warning_ph': '⚠️ pH level is outside optimal range (5.5–6.5)',
    'warning_moisture': '⚠️ Soil moisture is low. Irrigation may be needed.',
    'warning_crop': "⚠️ Intended crop 'ragi' may not be optimal for current soil conditions.",
    'lang_code': 'en'
    },
    'kn': {
    'title': 'ಮಣ್ಣಿನ ವರದಿ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
    'farmer': 'ರೈತನ ಹೆಸರು',
    'location': 'ಸ್ಥಳ',
    'crop': 'ಬೆಳೆ',
    'month': 'ಬಿತ್ತನೆ ತಿಂಗಳು',
    'upload': 'ಮಣ್ಣಿನ ವರದಿ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
    'submit': 'ಸಲ್ಲಿಸು',
    'parsed': 'ಪಾರ್ಸ್ ಮಾಡಿದ ಮೌಲ್ಯಗಳು',
    'recommended': 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು',
    'saved': 'ಉಳಿಸಿದ ವರದಿಗಳು',
    'nitrogen': 'ನೈಟ್ರೋಜನ್',
    'phosphorus': 'ಫಾಸ್ಫರಸ್',
    'potash': 'ಪೊಟಾಶ್',
    'ph': 'ಪಿಎಚ್ ಮೌಲ್ಯ',
    'moisture': 'ಆದ್ರತೆ',
    'months': [
        'ಜನವರಿ', 'ಫೆಬ್ರವರಿ', 'ಮಾರ್ಚ್', 'ಏಪ್ರಿಲ್', 'ಮೇ', 'ಜೂನ್',
        'ಜುಲೈ', 'ಆಗಸ್ಟ್', 'ಸೆಪ್ಟೆಂಬರ್', 'ಅಕ್ಟೋಬರ್', 'ನವೆಂಬರ್', 'ಡಿಸೆಂಬರ್'
    ],
    'revenue': 'ಒಟ್ಟು ಆದಾಯ',
    'cost': 'ಒಟ್ಟು ವೆಚ್ಚ',
    'profit': 'ನಿಕಾಸು ಲಾಭ',
    'break_even': 'ಬ್ರೇಕ್-ಈವೆನ್ ಬೆಲೆ',
    'print': 'ಈ ಪುಟವನ್ನು ಮುದ್ರಿಸಿ',
    'calculator': 'ಕ್ಯಾಲ್ಕುಲೇಟರ್',
    'yield': 'ಪ್ರತಿ ಹೆಕ್ಟೇರ್ ಉತ್ಪಾದನೆ (ಕೆ.ಜಿ)',
    'seed_cost': 'ಬೀಜ ವೆಚ್ಚ (₹)',
    'fertilizer_cost': 'ಸಾರ ವೆಚ್ಚ (₹)',
    'labor_cost': 'ಕಾರ್ಮಿಕ ವೆಚ್ಚ (₹)',
    'irrigation_cost': 'ನೀರಾವರಿ ವೆಚ್ಚ (₹)',
    'equipment_cost': 'ಉಪಕರಣ ವೆಚ್ಚ (₹)',
    'report': 'ವರದಿ',
    'warning_ph': '⚠️ ಪಿಎಚ್ ಮೌಲ್ಯ ಸೂಕ್ತ ಶ್ರೇಣಿಗೆ ಹೊರಗಿದೆ (5.5–6.5)',
    'warning_moisture': '⚠️ ಮಣ್ಣಿನ ತೇವಾಂಶ ಕಡಿಮೆ ಇದೆ. ನೀರಾವರಿ ಅಗತ್ಯವಿರಬಹುದು.',
    'warning_crop': "⚠️ ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ 'ರಾಗಿ' ಈ ಮಣ್ಣಿಗೆ ಸೂಕ್ತವಲ್ಲದಿರಬಹುದು.",
    'lang_code': 'kn'
    },
    'hi': {
    'title': 'मिट्टी रिपोर्ट अपलोड करें',
    'farmer': 'किसान का नाम',
    'location': 'स्थान',
    'crop': 'फसल',
    'month': 'बोने का महीना',
    'upload': 'मिट्टी रिपोर्ट छवि अपलोड करें',
    'submit': 'जमा करें',
    'parsed': 'विश्लेषित मान',
    'recommended': 'अनुशंसित फसलें और बाजार मूल्य',
    'saved': 'सहेजी गई रिपोर्टें',
    'nitrogen': 'नाइट्रोजन',
    'phosphorus': 'फॉस्फोरस',
    'potash': 'पोटाश',
    'ph': 'पीएच मान',
    'moisture': 'नमी',
    'months': [
        'जनवरी', 'फरवरी', 'मार्च', 'अप्रैल', 'मई', 'जून',
        'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर'
    ],
    'revenue': 'कुल राजस्व',
    'cost': 'कुल लागत',
    'profit': 'शुद्ध लाभ',
    'break_even': 'ब्रेक-ईवन मूल्य',
    'print': 'इस पृष्ठ को प्रिंट करें',
    'calculator': 'कैलकुलेटर',
    'yield': 'प्रति हेक्टेयर उपज (किग्रा)',
    'seed_cost': 'बीज लागत (₹)',
    'fertilizer_cost': 'उर्वरक लागत (₹)',
    'labor_cost': 'श्रम लागत (₹)',
    'irrigation_cost': 'सिंचाई लागत (₹)',
    'equipment_cost': 'उपकरण लागत (₹)',
    'report': 'रिपोर्ट',
    'warning_ph': '⚠️ पीएच मान इष्टतम सीमा (5.5–6.5) से बाहर है',
    'warning_moisture': '⚠️ मिट्टी की नमी कम है। सिंचाई की आवश्यकता हो सकती है।',
    'warning_crop': "⚠️ चयनित फसल 'रागी' वर्तमान मिट्टी की स्थिति के लिए उपयुक्त नहीं हो सकती है।",
    'lang_code': 'hi'
    },
    'te': {
    'title': 'మట్టి నివేదికను అప్‌లోడ్ చేయండి',
    'farmer': 'రైతు పేరు',
    'location': 'ప్రాంతం',
    'crop': 'పంట',
    'month': 'విత్తే నెల',
    'upload': 'మట్టి నివేదిక చిత్రాన్ని అప్‌లోడ్ చేయండి',
    'submit': 'సమర్పించండి',
    'parsed': 'విభజించిన విలువలు',
    'recommended': 'సిఫార్సు చేసిన పంటలు మరియు మార్కెట్ ధరలు',
    'saved': 'సేవ్ చేసిన నివేదికలు',
    'nitrogen': 'నైట్రోజన్',
    'phosphorus': 'ఫాస్ఫరస్',
    'potash': 'పొటాష్',
    'ph': 'pH విలువ',
    'moisture': 'తేమ',
    'months': [
        'జనవరి', 'ఫిబ్రవరి', 'మార్చి', 'ఏప్రిల్', 'మే', 'జూన్',
        'జూలై', 'ఆగస్ట్', 'సెప్టెంబర్', 'అక్టోబర్', 'నవంబర్', 'డిసెంబర్'
    ],
    'revenue': 'మొత్తం ఆదాయం',
    'cost': 'మొత్తం ఖర్చు',
    'profit': 'నికర లాభం',
    'break_even': 'బ్రేక్-ఈవెన్ ధర',
    'print': 'ఈ పేజీని ముద్రించండి',
    'calculator': 'క్యాలిక్యులేటర్',
    'yield': 'ప్రతి హెక్టేరు దిగుబడి (కిలోలు)',
    'seed_cost': 'విత్తన ఖర్చు (₹)',
    'fertilizer_cost': 'ఎరువుల ఖర్చు (₹)',
    'labor_cost': 'శ్రమ ఖర్చు (₹)',
    'irrigation_cost': 'పారిశుద్ధి ఖర్చు (₹)',
    'equipment_cost': 'పరికరాల ఖర్చు (₹)',
    'report': 'నివేదిక',
    'warning_ph': '⚠️ pH విలువ అనుకూల పరిధికి (5.5–6.5) బయట ఉంది',
    'warning_moisture': '⚠️ మట్టి తేమ తక్కువగా ఉంది. నీటిపారుదల అవసరం కావచ్చు.',
    'warning_crop': "⚠️ ఎంపిక చేసిన పంట 'రాగి' ప్రస్తుత మట్టి పరిస్థితులకు అనుకూలంగా ఉండకపోవచ్చు.",
    'lang_code': 'te'
    }
}

crop_translations = {
    'Cotton': {
        'en': 'Cotton',
        'kn': 'ಹತ್ತಿ',
        'hi': 'कपास',
        'te': 'పత్తి'
    },
    'Finger Millet': {
        'en': 'Finger Millet',
        'kn': 'ರಾಗಿ',
        'hi': 'रागी',
        'te': 'రాగి'
    },
    'Paddy': {
        'en': 'Paddy',
        'kn': 'ಅಕ್ಕಿ',
        'hi': 'धान',
        'te': 'వరి'
    },
    'Wheat': {
        'en': 'Wheat',
        'kn': 'ಗೋಧಿ',
        'hi': 'गेहूं',
        'te': 'గోధుమ'
    },
    'Maize': {
        'en': 'Maize',
        'kn': 'ಜೋಳ',
        'hi': 'मक्का',
        'te': 'మక్కజొన్న'
    },
    'Groundnut': {
        'en': 'Groundnut',
        'kn': 'ಶೇಂಗಾ',
        'hi': 'मूंगफली',
        'te': 'వేరుశెనగ'
    },
    'Sugarcane': {
        'en': 'Sugarcane',
        'kn': 'ಕಬ್ಬು',
        'hi': 'गन्ना',
        'te': 'చెరకు'
    },
    'Sunflower': {
        'en': 'Sunflower',
        'kn': 'ಸೂರ್ಯಕಾಂತಿ',
        'hi': 'सूरजमुखी',
        'te': 'సూర్యకాంతి'
    },
    'Soybean': {
        'en': 'Soybean',
        'kn': 'ಸೊಯಾಬೀನ್',
        'hi': 'सोयाबीन',
        'te': 'సోయాబీన్'
    },
    'Chickpea': {
        'en': 'Chickpea',
        'kn': 'ಕಡಲೆಕಾಯಿ',
        'hi': 'चना',
        'te': 'సెనగ'
    },
    'Red Gram': {
        'en': 'Red Gram',
        'kn': 'ತುಗರಿ ಬೇಳೆ',
        'hi': 'अरहर',
        'te': 'కందిపప్పు'
    },
    'Green Gram': {
        'en': 'Green Gram',
        'kn': 'ಹೆಸರುಕಾಳು',
        'hi': 'मूंग',
        'te': 'పెసరపప్పు'
    },
    'Black Gram': {
        'en': 'Black Gram',
        'kn': 'ಉದ್ದಿನಕಾಳು',
        'hi': 'उड़द',
        'te': 'మినపప్పు'
    },
    "pigeonpeas": {
    "en": "Pigeon Peas",
    "kn": "ತುಗರಿ ಬೇಳೆ",
    "hi": "अरहर दाल",
    "te": "కందిపప్పు"
    },
    "mango": {
        "en": "Mango",
        "kn": "ಮಾವಿನ ಹಣ್ಣು",
        "hi": "आम",
        "te": "మామిడి"
    },
    "orange": {
    "en": "Orange",
    "kn": "ಕಿತ್ತಳೆ ಹಣ್ಣು",
    "hi": "संतरा",
    "te": "నారింజ"
    }
    
}

@app.route('/')
def index():
    lang = request.args.get('language') or session.get('language', 'en')
    session['language'] = lang
    t = translations.get(lang, translations['en'])
    return render_template('upload.html', t=t)

import joblib
model = joblib.load('crop_model.pkl')  # Load the trained model once at the top of your app

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['soilReport']
    farmer_name = request.form['farmerName']
    location = request.form['location']
    crop_type = request.form['cropType']
    sowing_month = int(request.form['sowingMonth'])
    language = request.form.get('language', 'en')
    session['language'] = language
    t = translations.get(language, translations['en'])

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    text = pytesseract.image_to_string(Image.open(filepath), config='--psm 11')

    try:
        nitrogen, phosphorus, potash, ph_value, moisture = extract_values(text)
    except Exception:
        numbers = extract_all_numbers(text)
        return f"<h2>Extracted Text:</h2><pre>{text}</pre><h2>Detected Numbers:</h2><p>{numbers}</p><p>⚠️ Unable to auto-map values.</p>"

    # ✅ ML prediction
    temperature = 25
    humidity = 60
    rainfall = 100
    features = [[nitrogen, phosphorus, potash, temperature, humidity, ph_value, rainfall]]
    predicted_crop = model.predict(features)[0]
    translated_prediction = crop_translations.get(predicted_crop, {}).get(language, predicted_crop)
    predicted_price = get_crop_price(predicted_crop)
    # ✅ Save to database
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    interpretation = f"N={nitrogen}, P={phosphorus}, K={potash}, pH={ph_value}, Moisture={moisture}"
    cursor.execute('''
        INSERT INTO soil_reports (farmer, location, crop, nitrogen, phosphorus, potash, ph, moisture, interpretation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (farmer_name, location, crop_type, nitrogen, phosphorus, potash, ph_value, moisture, interpretation))
    conn.commit()
    conn.close()

    # ✅ Your existing recommendation logic
    recommended_crops, warnings = recommend_crops(
        nitrogen, phosphorus, potash, ph_value, moisture,
        crop_type, sowing_month, language, translations
    )

    translated_crops = [
        {
            "name": crop_translations[crop][language],
            "price": get_crop_price(crop),
            "original": crop
        }
        for crop in recommended_crops
    ]

    saved_reports.append({
        'farmer': farmer_name,
        'location': location,
        'crop': crop_type,
        'month': sowing_month,
        'recommendations': recommended_crops,
        'warnings': warnings,
        'language': language,
        'timestamp': datetime.now(),
        'ml_prediction': predicted_crop  # ✅ Store ML prediction in memory
    })

    return render_template('results.html',
    t=t,
    crop=crop_type,
    nitrogen=nitrogen,
    phosphorus=phosphorus,
    potash=potash,
    ph_value=ph_value,
    moisture=moisture,
    translated_crops=translated_crops,
    warnings=warnings,
    language=language,
    ml_prediction=translated_prediction,
    ml_price=predicted_price,
    crop_translations=crop_translations  # ✅ Add this line
)

@app.route('/calculator')
def calculator():
    crop = request.args.get('crop', '')
    price = request.args.get('price', '')
    language = request.args.get('language', 'en')
    t = translations.get(language, translations['en'])
    return render_template('calculator.html', crop=crop, price=price, t=t)

@app.route('/calculate', methods=['POST'])
def calculate():
    crop = request.form['crop']
    yield_per_hectare = float(request.form['yield'])
    market_price = float(request.form['price'])
    seed_cost = float(request.form['seed'])
    fertilizer_cost = float(request.form['fertilizer'])
    labor_cost = float(request.form['labor'])
    irrigation_cost = float(request.form['irrigation'])
    equipment_cost = float(request.form['equipment'])
    language = request.form.get('language', 'en')
    t = translations.get(language, translations['en'])

    total_cost = seed_cost + fertilizer_cost + labor_cost + irrigation_cost + equipment_cost
    total_revenue = yield_per_hectare * market_price
    net_profit = total_revenue - total_cost
    break_even_price = total_cost / yield_per_hectare if yield_per_hectare else 0

    return render_template('result.html',
                           crop=crop,
                           revenue=round(total_revenue, 2),
                           cost=round(total_cost, 2),
                           profit=round(net_profit, 2),
                           break_even=round(break_even_price, 2),
                           t=t)

@app.route('/reports')
def view_reports():
    language = request.args.get('language') or session.get('language', 'en')
    session['language'] = language
    t = translations.get(language, translations['en'])

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM soil_reports ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()

    # Build HTML safely and cleanly
    html = f"""
    <html>
    <head>
        <title>{t['saved']}</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>{t['saved']}</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>{t['farmer']}</th>
                <th>{t['location']}</th>
                <th>{t['crop']}</th>
                <th>{t['nitrogen']}</th>
                <th>{t['phosphorus']}</th>
                <th>{t['potash']}</th>
                <th>{t['ph']}</th>
                <th>{t['moisture']}</th>
                <th>{t['report']}</th>
            </tr>
    """

    for row in rows:
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

    html += f"""
        </table>
        <p><a href="/?language={t['lang_code']}">{t['upload']}</a></p>
        <p><a href="/export_csv">📤 Export as CSV</a></p>
    </body>
    </html>
    """

    return html
@app.route('/debug_reports')
def debug_reports():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM soil_reports ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return f"<pre>{rows}</pre>"
@app.route('/export_csv')
def export_csv():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM soil_reports')
    rows = cursor.fetchall()
    conn.close()

    def generate():
        yield 'ID,Farmer,Location,Crop,N,P,K,pH,Moisture,Interpretation\n'
        for row in rows:
            yield ','.join(str(cell) for cell in row) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=soil_reports.csv"})
@app.route('/debug_schema')
def debug_schema():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(soil_reports)")
    columns = cursor.fetchall()
    conn.close()
    return f"<pre>{columns}</pre>"
if __name__ == '__main__':
    init_soil_table()
    app.run(debug=True)