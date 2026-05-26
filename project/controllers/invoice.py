import io
import csv
import pdfplumber
import re
from flask import Blueprint, render_template, request, Response, flash, redirect

invoice_bp = Blueprint('invoice', __name__)


@invoice_bp.route('/upload-invoice', methods=['GET', 'POST'])
def upload_invoice():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nu a fost detectat niciun fișier.')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Nu ai selectat niciun fișier.')
            return redirect(request.url)

        if file and file.filename.lower().endswith('.pdf'):
            extracted_data = []

            with pdfplumber.open(io.BytesIO(file.read())) as pdf:
                # Colectăm toate liniile de text din toate paginile într-o singură listă globală
                all_lines = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_lines.extend([l.strip() for l in text.split('\n') if l.strip()])

                raw_products = []
                code_mapping = {}

                # Pasul 1: Scanăm textul pentru a extrage produsele și identificatorii
                for idx, line in enumerate(all_lines):

                    # Cazul A: Linie de produs (conține RON)
                    if "RON" in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            try:
                                ron_idx = parts.index("RON")
                                pret_unitar = parts[ron_idx - 1]

                                # Cantitatea facturată
                                if ron_idx + 2 < len(parts):
                                    cantitate = parts[ron_idx + 2]
                                else:
                                    cantitate = parts[-1]

                                # Reconstruim textul din stânga prețului
                                left_text = " ".join(parts[:ron_idx - 1]).strip()

                                # Încercăm să vedem dacă numărul liniei s-a lipit la final (ex: "... 1")
                                nr_linie = "1"
                                match_nr = re.search(r'\s+(\d+)$', left_text)
                                if match_nr:
                                    nr_linie = match_nr.group(1)
                                    left_text = re.sub(r'\s+\d+$', '', left_text).strip()

                                # Eliminăm duplicarea codului de la începutul denumirii dacă există
                                desc_parts = left_text.split()
                                if len(desc_parts) > 1 and desc_parts[0] == desc_parts[1]:
                                    left_text = " ".join(desc_parts[1:])

                                # Verificare de siguranță pentru a nu lua antete sau totaluri
                                if "TOTAL" not in left_text.upper() and "VALOARE" not in left_text.upper() and "MONEDA" not in left_text.upper():
                                    raw_products.append({
                                        'nr_linie': nr_linie,
                                        'denumire': left_text,
                                        'pret_unitar': pret_unitar,
                                        'moneda': "RON",
                                        'cantitate': cantitate
                                    })
                            except Exception:
                                continue

                    # Cazul B: Linie salvatoare de cod (Identificator vanzator)
                    elif "Identificator vanzator" in line or "articol pentru linia" in line:
                        match_code = re.search(r'linia\s+(\d+)\s*:\s*(.+)', line, re.IGNORECASE)
                        if match_code:
                            nr_linie_id = match_code.group(1)
                            cod_articol = match_code.group(2).strip()
                            code_mapping[nr_linie_id] = cod_articol

                # Pasul 2: Corelăm produsele cu codurile lor reale pe baza numărului de linie
                for prod in raw_products:
                    nr = prod['nr_linie']
                    # Dacă am găsit codul în text, îl punem, altfel lăsăm primul cuvânt din denumire ca fallback
                    if nr in code_mapping:
                        prod_code = code_mapping[nr]
                    else:
                        words = prod['denumire'].split()
                        prod_code = words[0] if words else "Necunoscut"

                    # Curățăm denumirea finală să nu mai conțină codul în ea
                    final_desc = prod['denumire']
                    if final_desc.startswith(prod_code):
                        final_desc = final_desc[len(prod_code):].strip()

                    extracted_data.append({
                        'cod': prod_code,
                        'denumire': final_desc,
                        'pret_unitar': prod['pret_unitar'],
                        'moneda': prod['moneda'],
                        'cantitate': prod['cantitate']
                    })

            # Generarea fișierului CSV final
            output = io.StringIO()
            writer = csv.writer(output)

            # Capul de tabel standard solicitat
            writer.writerow(['Cod produs', 'Denumire produs', 'Pret unitar', 'Moneda', 'Cantitate'])

            # Adăugăm produsele extrase
            for item in extracted_data:
                writer.writerow([item['cod'], item['denumire'], item['pret_unitar'], item['moneda'], item['cantitate']])

            # Curățăm extensia în mod sigur pentru browser
            safe_filename = "extras_factura.csv"
            if file.filename:
                base_name = file.filename.rsplit('.', 1)[0]
                safe_filename = f"extras_{base_name}.csv"

            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={safe_filename}",
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                }
            )

    return render_template('invoice/upload.html')
