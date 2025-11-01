import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="PDF Auto Fill Dashboard", page_icon="🧾", layout="centered")

st.title("🧾 PDF Auto Fill Dashboard")
st.write("Pilih template & isi data untuk otomatis mengisi file PDF (Task Card, DI, PF, WK, dll).")
st.markdown("---")

# --- Dictionary halaman tiap template ---
page_ranges = {
    "DI BATIK REV 08.pdf": (2, 27),
    "PF BATIK REV 02.pdf": (2, 8),
    "WK BATIK REV 10.pdf": (2, 16),
    "TC DAILY REV 39.pdf": (4, 31),
    "TC PF REV 14.pdf": (2, 8),
}

# --- Pilihan Template ---
template_pdf = st.selectbox(
    "📄 Pilih Template PDF",
    list(page_ranges.keys()),
    index=4  # default TC PF REV 14
)

start_page, end_page = page_ranges.get(template_pdf, (2, 8))
start_page -= 1  # index mulai dari 0

# --- FORM INPUT ---
with st.form("pdf_form"):
    st.subheader("✏️ Isi Data")
    col1, col2 = st.columns(2)
    with col1:
        work_order = st.text_input("WORK ORDER NO.")
        ac_reg = st.text_input("A/C REG.")
        ac_msn = st.text_input("A/C MSN.")
    with col2:
        ac_eff = st.text_input("A/C Effectivity")
        operator = st.text_input("OPERATOR")
        uploaded_pdf = st.file_uploader("Upload File Template PDF", type=["pdf"])

    submitted = st.form_submit_button("🚀 Generate PDF")

# --- PROSES GENERATE PDF ---
if submitted:
    if not uploaded_pdf:
        st.error("⚠️ Tolong upload file PDF template dulu.")
    else:
        template = PdfReader(uploaded_pdf)
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

        st.success(f"✅ PDF berhasil diisi otomatis! ({template_pdf} halaman {start_page+1}–{end_page})")
        st.download_button(
            "⬇️ Download Hasil PDF",
            result,
            file_name=f"Output_{template_pdf.replace('.pdf', '')}.pdf",
            mime="application/pdf",
        )

st.markdown("---")
st.markdown("<p style='text-align:center; color:#94a3b8;'>Dibuat dengan ❤️ oleh TKG Line Maintenance</p>", unsafe_allow_html=True)
