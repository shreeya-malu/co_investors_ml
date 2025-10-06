from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from collections import Counter
from itertools import chain

from src.preprocess import preprocess_dataset
from src.apriori_unweighted import run_apriori_unweighted
from src.apriori_weighted import run_apriori_weighted

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# ------------------------------
# Global cached data
# ------------------------------
DATA = None
INSIGHTS_CACHE = {}

# ------------------------------
# Serve frontend
# ------------------------------
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ------------------------------
# Upload CSV
# ------------------------------
@app.route('/api/upload', methods=['POST'])
def upload_file():
    global DATA, INSIGHTS_CACHE
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    # Read CSV
    df = pd.read_csv(file)

    # Preprocess dataset
    DATA, _, _ = preprocess_dataset(df)
    INSIGHTS_CACHE.clear()
    return jsonify({'message': 'Upload successful!'})

# ------------------------------
# Dashboard Insights
# ------------------------------
@app.route('/api/insights', methods=['GET'])
def get_insights():
    global DATA, INSIGHTS_CACHE
    if DATA is None:
        return jsonify({'error':'No data uploaded'}), 400

    if not INSIGHTS_CACHE:
        # Top co-investors
        co_count = {}
        for inv_list in DATA['investors_list']:
            for i in inv_list:
                co_count[i] = co_count.get(i,0)+1
        top_co = sorted(co_count.items(), key=lambda x:-x[1])[:10]

        # Top domains
        domain_count = {}
        for vlist in DATA['verticals_list']:
            for v in vlist:
                domain_count[v] = domain_count.get(v,0)+1
        top_domains = sorted(domain_count.items(), key=lambda x:-x[1])[:10]

        # Basic stats
        stats = {'n_startups': len(DATA), 'n_unique_investors': len(co_count)}

        INSIGHTS_CACHE.update({
            'top_co': top_co,
            'top_domains': top_domains,
            'stats': stats
        })

    return jsonify(INSIGHTS_CACHE)

# ------------------------------
# Investor Details
# ------------------------------
@app.route('/api/investor/<investor_name>', methods=['GET'])
def investor_details(investor_name):
    global DATA
    if DATA is None:
        return jsonify({'error':'No data uploaded'}), 400

    inv_rows = DATA[DATA['investors_list'].apply(lambda x: investor_name in x)]
    startups = inv_rows['startup_name'].tolist()
    domains = list(chain.from_iterable(inv_rows['verticals_list'].tolist()))

    # Co-investors
    co_investors = Counter()
    for inv_list in inv_rows['investors_list']:
        for i in inv_list:
            if i != investor_name:
                co_investors[i] += 1

    return jsonify({
        'startups': startups,
        'domains': Counter(domains).most_common(10),
        'co_investors': co_investors.most_common(10)
    })

# ------------------------------
# Generate PDF Report
# ------------------------------
@app.route('/api/generate-report/<investor_name>', methods=['GET'])
def generate_report(investor_name):
    global DATA
    if DATA is None:
        return jsonify({'error':'No data uploaded'}), 400

    inv_rows = DATA[DATA['investors_list'].apply(lambda x: investor_name in x)]
    startups = inv_rows['startup_name'].tolist()
    domains = list(chain.from_iterable(inv_rows['verticals_list'].tolist()))
    co_investors = Counter()
    for inv_list in inv_rows['investors_list']:
        for i in inv_list:
            if i != investor_name:
                co_investors[i] += 1

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, y, f"Investor Report: {investor_name}")
    y -= 40

    c.setFont("Helvetica", 14)
    c.drawString(50, y, f"Total Startups Invested In: {len(startups)}")
    y -= 25

    # Top startups
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Top Startups:")
    y -= 20
    c.setFont("Helvetica", 12)
    for s in startups[:10]:
        c.drawString(70, y, f"- {s}")
        y -= 15

    y -= 10
    # Top Domains
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Top Domains:")
    y -= 20
    c.setFont("Helvetica", 12)
    for d, cnt in Counter(domains).most_common(10):
        c.drawString(70, y, f"- {d} ({cnt})")
        y -= 15

    y -= 10
    # Co-Investors
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Top Co-Investors:")
    y -= 20
    c.setFont("Helvetica", 12)
    for ci, cnt in co_investors.most_common(10):
        c.drawString(70, y, f"- {ci} ({cnt})")
        y -= 15

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, download_name=f"{investor_name}_report.pdf", as_attachment=True, mimetype='application/pdf')

# ------------------------------
# Network Map Data
# ------------------------------
@app.route('/api/network/<investor_name>', methods=['GET'])
def network_map(investor_name):
    global DATA
    if DATA is None:
        return jsonify({'error':'No data uploaded'}), 400

    nodes = []
    links = []

    nodes.append({'id': investor_name, 'type': 'investor'})
    inv_rows = DATA[DATA['investors_list'].apply(lambda x: investor_name in x)]
    domains_set = set()
    startups_set = set()
    for idx,row in inv_rows.iterrows():
        startup = row['startup_name']
        startups_set.add(startup)
        links.append({'from': investor_name, 'to': startup})
        for d in row['verticals_list']:
            domains_set.add(d)
            links.append({'from': startup, 'to': d})
    for s in startups_set:
        nodes.append({'id': s, 'type':'startup'})
    for d in domains_set:
        nodes.append({'id': d, 'type':'domain'})

    return jsonify({'nodes': nodes, 'links': links})

# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
