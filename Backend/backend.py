from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
from ai_agent import generate_itinerary_with_agent

app = Flask(__name__)
CORS(app)


def save_itinerary_to_pdf(place, start_date, end_date, itinerary, filename="itinerary.pdf"):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Itinerary for {place}", ln=True, align='C')
    pdf.cell(
        200, 10, txt=f"From {start_date} to {end_date}", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, itinerary)
    pdf.output(filename)
    return filename


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()
    place = data.get('place')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    if not all([place, start_date, end_date]):
        return jsonify({'error': 'Missing required fields'}), 400
    itinerary = generate_itinerary_with_agent(place, start_date, end_date)
    pdf_path = save_itinerary_to_pdf(place, start_date, end_date, itinerary)
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF not found'}), 500
    return send_file(pdf_path, as_attachment=True, download_name="itinerary.pdf", mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True)
