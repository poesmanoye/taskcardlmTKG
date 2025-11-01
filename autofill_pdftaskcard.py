import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import base64

# --- Konfigurasi halaman ---
st.set_page_config(page_title="TASKCARD AUTOFILL TKG", page_icon="logo.png", layout="centered")

# --- Header ---
st.markdown("""
    <h1 style='text-align:center; color: #FFFFFF;'>TASKCARD LINE MAINTENANCE TKG</h1>
    <p style='text-align:center; color:#00FFFF;'>Task Card Daily And Pre-Flight For Boeing 737 NG or Airbus A320</p>
    <hr>
""", unsafe_allow_html=True)

# --- Template PDF dan rentang halaman ---
page_ranges = {
    "DI BATIK REV 08.pdf": (2, 27),
    "PF BATIK REV 02.pdf": (2, 8),
    "WK BATIK REV 10.pdf": (2, 16),
    "TC DAILY REV 39.pdf": (4, 31),
    "TC PF REV 14.pdf": (2, 8),
}

# --- Pilih template ---
template_name = st.selectbox("📄 Choose TaskCard", list(page_ranges.keys()), index=4)
start_page, end_page = page_ranges[template_name]
start_page -= 1  # index mulai dari 0

# --- Form input data ---
with st.form("pdf_form"):
    st.subheader("ENTER DATA CORRECTLY")
    col1, col2 = st.columns(2)
    with col1:
        work_order = st.text_input("WORK ORDER NO.")
        ac_reg = st.text_input("A/C REG.")
        ac_msn = st.text_input("A/C MSN.")
    with col2:
        ac_eff = st.text_input("A/C Effectivity")
        operator = st.text_input("OPERATOR")
    submitted = st.form_submit_button("🚀 Generate PDF")

# --- Jika user klik tombol Generate ---
if submitted:
    try:
        template = PdfReader(template_name)
        output = PdfWriter()

        for i, page in enumerate(template.pages):
            if start_page <= i < end_page:
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)
                can.setFont("Helvetica", 9)
                can.drawString(69, 734, work_order)
                can.drawString(149, 734, ac_reg)
                can.drawString(206, 734, ac_msn)
                can.drawString(270, 734, ac_eff)
                can.drawString(360, 734, operator)
                can.save()
                packet.seek(0)
                overlay_pdf = PdfReader(packet)
                page.merge_page(overlay_pdf.pages[0])
            output.add_page(page)

        result = BytesIO()
        output.write(result)
        result.seek(0)

        # --- Encode hasil PDF ke base64 untuk tombol download & print ---
        pdf_data = result.getvalue()
        b64 = base64.b64encode(pdf_data).decode('utf-8')

        # --- Tampilan tombol sejajar (CSS) ---
        st.markdown("""
            <style>
            .button-row {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-top: 15px;
            }
            .button-row a, .button-row button {
                background-color: #2563eb;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                transition: 0.2s;
            }
            .button-row a:hover, .button-row button:hover {
                background-color: #1e40af;
            }
            .button-row .print-btn {
                background-color: #16a34a;
            }
            .button-row .print-btn:hover {
                background-color: #15803d;
            }
            </style>
        """, unsafe_allow_html=True)

        # --- Pesan sukses ---
        st.success(f"✅ Berhasil isi otomatis: {template_name} (hal {start_page+1}–{end_page})")

        # --- HTML tombol sejajar (Download + Print) ---
        buttons_html = f"""
        <div class="button-row">
            <a href="data:application/pdf;base64,{b64}" 
               download="FINAL_{template_name.replace('.pdf', '')}.pdf">
               ⬇️ DOWNLOAD TASKCARD
            </a>
            <button class="print-btn" 
                onclick="var pdfWin = window.open('', '_blank'); 
                         pdfWin.document.write('<iframe src=\'data:application/pdf;base64,{b64}\' 
                         width=\'100%\' height=\'100%\'></iframe>'); 
                         pdfWin.document.close(); pdfWin.focus(); pdfWin.print();">
                🖨️ PRINT TASKCARD
            </button>
        </div>
        """
        st.markdown(buttons_html, unsafe_allow_html=True)

    except FileNotFoundError:
        st.error("⚠️ File template tidak ditemukan. Pastikan semua PDF ada di folder yang sama dengan app.py")

# --- Footer ---
st.markdown("<hr><p style='text-align:center;color:#94a3b8;'>Dibuat oleh poesmanoye V1</p>", unsafe_allow_html=True)
