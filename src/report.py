from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from collections import Counter

def generate_investor_pdf(investor_name, df):
    """
    Generate a PDF report for a given investor.
    Includes:
    - Startups invested in
    - Top domains
    - Top co-investors
    """
    # Filter rows for the given investor
    inv_rows = df[df['investors_list'].apply(lambda x: investor_name in x)]

    # Startups
    startups = inv_rows['startup_name'].tolist()

    # Domains
    domains = [v for vl in inv_rows['verticals_list'] for v in vl]

    # Co-investors
    co_investors = Counter()
    for inv_list in inv_rows['investors_list']:
        for i in inv_list:
            if i != investor_name:
                co_investors[i] += 1

    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, y, f"Investor Report: {investor_name}")
    y -= 40

    # Total startups
    c.setFont("Helvetica", 14)
    c.drawString(50, y, f"Total Startups Invested In: {len(startups)}")
    y -= 25

    # Top Startups
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

    # Finish PDF
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
