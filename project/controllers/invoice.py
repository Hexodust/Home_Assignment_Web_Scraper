import io
import csv
import pdfplumber
import re
from flask import Blueprint, render_template, request, Response, flash, redirect

invoice_bp = Blueprint('invoice', __name__)

_CURRENCY_RE = re.compile(r'^[A-Z]{3}$')
_NUMBER_RE = re.compile(r'^-?\d+(?:[.,]\d+)?$')
_COUNTRY_RE = re.compile(r'^[A-Z]{2}$')


def _build_code_mapping(all_lines):
    mapping = {}
    for line in all_lines:
        m = re.search(r'pentru\s+linia\s+(\d+)\s*:\s*(\S+)', line, re.IGNORECASE)
        if m:
            mapping[m.group(1)] = m.group(2).strip()
    return mapping


def _row_from_tokens(tokens, code_mapping):
    if len(tokens) < 9 or not tokens[0].isdigit():
        return None
    cur_idx = next(
        (i for i, p in enumerate(tokens)
         if _CURRENCY_RE.match(p) and i >= 2 and _NUMBER_RE.match(tokens[i - 1])),
        None,
    )
    if cur_idx is None or cur_idx + 2 >= len(tokens):
        return None

    nr_linie = tokens[0]
    pret_unitar = tokens[cur_idx - 1]
    moneda = tokens[cur_idx]
    cantitate = tokens[cur_idx + 2]

    name_tokens = tokens[1:cur_idx - 1]
    if name_tokens and _COUNTRY_RE.match(name_tokens[-1]):
        name_tokens = name_tokens[:-1]

    cod = code_mapping.get(nr_linie) or (name_tokens[0] if name_tokens else 'Necunoscut')
    if name_tokens and name_tokens[0] == cod:
        name_tokens = name_tokens[1:]

    return {
        'cod': cod,
        'denumire': ' '.join(name_tokens),
        'pret_unitar': pret_unitar,
        'moneda': moneda,
        'cantitate': cantitate,
    }


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
                all_lines = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_lines.extend(l.strip() for l in text.split('\n') if l.strip())

                code_mapping = _build_code_mapping(all_lines)

                # Anchor on the product-table header:
                header_idx = next(
                    (i for i, l in enumerate(all_lines)
                     if l.startswith('Linia') and 'Nume articol' in l),
                    None,
                )

                if header_idx is None:
                    flash('Tabelul de produse (header "Linia ... Nume articol") nu a fost gasit in PDF.')
                    return redirect(request.url)

                for line in all_lines[header_idx + 1:]:
                    prod = _row_from_tokens(line.split(), code_mapping)
                    if prod:
                        extracted_data.append(prod)

            # Generarea fișierului CSV final
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(['Cod produs', 'Denumire produs', 'Pret unitar', 'Moneda', 'Cantitate'])

            for item in extracted_data:
                writer.writerow([item['cod'], item['denumire'], item['pret_unitar'], item['moneda'], item['cantitate']])

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
