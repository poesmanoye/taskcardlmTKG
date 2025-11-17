import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import base64

# --- Konfigurasi halaman ---
st.set_page_config(page_title="TASKCARD LION GROUP", layout="centered")

# --- CSS ---
st.markdown("""
    <style>
        h1 a, h2 a, h3 a {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)


# base64 loader
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# load logo
logo_base64 = get_base64_of_image("download-removebg-preview.png")

# CSS header
st.markdown("""
    <style>
        .header-container h1 {
            color: #FF0000 !important;
            font-weight: 900 !important;
            margin-bottom: 6px !important;
        }
        .header-container p {
            font-size: 16px !important;
            color: #666 !important;
            margin-top: 0px !important;
        }
        .header-container img {
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-bottom: 5px !important;
        }
    </style>
""", unsafe_allow_html=True)

# header
st.markdown(f"""
    <div class="header-container" style="text-align:center; margin-top:-25px;">
        <img src="data:image/png;base64,{logo_base64}" width="140">
        <h1>TASKCARD LINE MAINTENANCE </h1>
        <p>TASKCARD DAILY CHECK, PRE-FLIGHT CHECK, WEEKLY CHECK ON LION GROUP</p>
    </div>
""", unsafe_allow_html=True)


# --- Peringatan Awal ---
if "show_warning" not in st.session_state:
    st.session_state.show_warning = True

if st.session_state.show_warning:
    st.markdown("""
    <div style="
        background-color:#fff3cd;
        color:#856404;
        border:1px solid #ffeeba;
        border-radius:8px;
        padding:18px;
        font-size:15px;
        text-align:justify;
        margin-bottom:15px;">
        ⚠️ <b>PERINGATAN:</b> Pastikan 
        <b><u>REVISI TASKCARD MASING-MASING OPERATOR</u></b> 
        (LION AIR / BATIK AIR) sudah update sebelum anda melanjutkan pengisian data.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("OK, MENGERTI", key="understood", use_container_width=True):
            st.session_state.show_warning = False
            st.rerun()

# --- MAIN FORM ---
else:

    # List Template
    page_ranges = {
        "TC DAILY CHECK A320 SUPER AIR JET REV 09.pdf": (1, 27),
        "TC PRE-FLIGHT CHECK A320 SUPER AIR JET REV 01.pdf": (1, 8),
        "TC WEEKLY CHECK A320 SUPER AIR JET REV 10.pdf": (1, 16),
        "TC DAILY CHECK A320 BATIK REV 08.pdf": (1, 27),
        "TC PRE-FLIGHT CHECK A320 BATIK REV 02.pdf": (1, 8),
        "TC WEEKLY CHECK A320 BATIK REV 10.pdf": (1, 16),
        "TC DAILY CHECK B737 LION REV 39.pdf": (1, 31),
        "TC PRE-FLIGHT CHECK B737 LION REV 14.pdf": (1, 8),
    }

    template_name = st.selectbox("📄 Choose TaskCard", list(page_ranges.keys()), index=3)
    start_page, end_page = page_ranges[template_name]
    start_page -= 1

    # Form Input
    with st.form("pdf_form"):
        st.subheader("MASUKAN DATA DENGAN BENAR")

        col1, col2 = st.columns(2)
        with col1:
            work_order = st.text_input("WORK ORDER NO.")
            ac_reg = st.text_input("A/C REG.")
            ac_msn = st.text_input("A/C MSN.")
            ac_type = st.selectbox(
                "A/C TYPE",
                ["B737-800 NG", "B737-900 ER", "A320", "ATR72-500", "ATR72-600"]
            )
        with col2:
            ac_eff = st.text_input("A/C Effectivity")
            operator = st.selectbox(
                "OPERATOR",
                ["LION AIR", "BATIK AIR", "SUPER AIR JET", "WINGS AIR"]
            )
            place = st.text_input("PLACE")

        submitted = st.form_submit_button("Generate TaskCard")

    # ---- BUTTON GENERATE ----
    if submitted:

        # Cek input kosong
        if not all([work_order, ac_reg, ac_msn, ac_type, ac_eff, operator, place]):
            st.warning("⚠️ Harap isi semua kolom sebelum generate Taskcard!")

        else:

            # ======================================================
            # 🔸 VALIDASI A/C EFFECTIVITY KHUSUS LION AIR SAJA
            # ======================================================
            valid_prefix = ["MLI", "ETJ", "ILF", "GEF"]

            if operator.upper() == "LION AIR":
                if not any(ac_eff.upper().startswith(prefix) for prefix in valid_prefix):
                    st.error("⚠️ Untuk LION AIR, A/C Effectivity harus diawali MLI, ETJ, ILF, atau GEF.")
                    st.stop()
            # Operator lain → TIDAK divalidasi

            # ======================================================
            # 🔸 VALIDASI OPERATOR VS TEMPLATE
            # ======================================================
            if "LION" in template_name.upper() and "LION" not in operator.upper():
                st.error("⚠️ Operator tidak sesuai! Taskcard ini untuk LION AIR.")
            elif "BATIK" in template_name.upper() and "BATIK" not in operator.upper():
                st.error("⚠️ Operator tidak sesuai! Taskcard ini untuk BATIK AIR.")
            elif "SUPER AIR JET" in template_name.upper() and "SUPER AIR JET" not in operator.upper():
                st.error("⚠️ Operator tidak sesuai! Taskcard ini untuk SUPER AIR JET.")
            else:

                # ======================================================
                # PROCESS PDF
                # ======================================================
                try:
                    template = PdfReader(template_name)
                    output = PdfWriter()

                    for i, page in enumerate(template.pages):
                        if start_page <= i < end_page:

                            packet = BytesIO()
                            can = canvas.Canvas(packet, pagesize=A4)
                            can.setFont("Helvetica", 9)

                            # ======================================================
                            # === PENEMPATAN KOORDINAT ===
                            # ======================================================

                            # === TC DAILY B737 LION REV 39 ===
                            if template_name == "TC DAILY CHECK B737 LION REV 39.pdf":
                                if i == start_page or i == start_page + 2:
                                    can.drawString(480, 734, work_order)
                                    can.drawString(45, 703, ac_reg)
                                    can.drawString(118, 703, ac_msn)
                                    can.drawString(115, 734, ac_eff)
                                    can.drawString(43, 630, operator)
                                    can.drawString(120, 630, place)
                                    can.drawString(34, 734, ac_type)
                                else:
                                    can.drawString(66, 734, work_order)
                                    can.drawString(145, 734, ac_reg)
                                    can.drawString(203, 734, ac_msn)
                                    can.drawString(270, 734, ac_eff)
                                    can.drawString(360, 734, operator)

                            # === DAILY BATIK REV 08 ===
                            elif template_name == "TC DAILY CHECK A320 BATIK REV 08.pdf":
                                if i == start_page:
                                    can.drawString(482, 735, work_order)
                                    can.drawString(45, 703, ac_reg)
                                    can.drawString(117, 703, ac_msn)
                                    can.drawString(123, 735, ac_eff)
                                    can.drawString(40, 636, operator)
                                    can.drawString(119, 636, place)
                                    can.drawString(51, 735, ac_type)
                                else:
                                    can.drawString(65, 733, work_order)
                                    can.drawString(147, 733, ac_reg)
                                    can.drawString(203, 733, ac_msn)
                                    can.drawString(277, 733, ac_eff)
                                    can.drawString(357, 733, operator)

                            # === PRE-FLIGHT BATIK REV 02 ===
                            elif template_name == "TC PRE-FLIGHT CHECK A320 BATIK REV 02.pdf":
                                if i == start_page:
                                    can.drawString(480, 734, work_order)
                                    can.drawString(47, 702, ac_reg)
                                    can.drawString(118, 702, ac_msn)
                                    can.drawString(123, 734, ac_eff)
                                    can.drawString(42, 635, operator)
                                    can.drawString(120, 635, place)
                                    can.drawString(52, 734, ac_type)
                                else:
                                    can.drawString(65, 733, work_order)
                                    can.drawString(147, 733, ac_reg)
                                    can.drawString(203, 733, ac_msn)
                                    can.drawString(277, 733, ac_eff)
                                    can.drawString(357, 733, operator)

                            # === WEEKLY BATIK REV 10 ===
                            elif template_name == "TC WEEKLY CHECK A320 BATIK REV 10.pdf":
                                if i == start_page:
                                    can.drawString(480, 734, work_order)
                                    can.drawString(47, 702, ac_reg)
                                    can.drawString(118, 702, ac_msn)
                                    can.drawString(123, 734, ac_eff)
                                    can.drawString(42, 635, operator)
                                    can.drawString(120, 635, place)
                                    can.drawString(52, 734, ac_type)
                                else:
                                    can.drawString(65, 733, work_order)
                                    can.drawString(147, 733, ac_reg)
                                    can.drawString(203, 733, ac_msn)
                                    can.drawString(277, 733, ac_eff)
                                    can.drawString(357, 733, operator)

                            # === DAILY SUPER AIR JET ===
                            elif template_name == "TC DAILY CHECK A320 SUPER AIR JET REV 09.pdf":
                                if i == start_page:
                                    can.drawString(482, 735, work_order)
                                    can.drawString(45, 703, ac_reg)
                                    can.drawString(117, 703, ac_msn)
                                    can.drawString(123, 735, ac_eff)
                                    can.drawString(40, 636, operator)
                                    can.drawString(119, 636, place)
                                    can.drawString(51, 735, ac_type)
                                else:
                                    can.drawString(65, 733, work_order)
                                    can.drawString(147, 733, ac_reg)
                                    can.drawString(203, 733, ac_msn)
                                    can.drawString(277, 733, ac_eff)
                                    can.drawString(345, 733, operator)

                            # === PRE-FLIGHT SUPER AIR JET ===
                            elif template_name == "TC PRE-FLIGHT CHECK A320 SUPER AIR JET REV 01.pdf":
                                if i == start_page:
                                    can.drawString(480, 734, work_order)
                                    can.drawString(47, 702, ac_reg)
                                    can.drawString(118, 702, ac_msn)
                                    can.drawString(123, 734, ac_eff)
                                    can.drawString(42, 635, operator)
                                    can.drawString(120, 635, place)
                                    can.drawString(52, 734, ac_type)
                                else:
                                    can.drawString(65, 733, work_order)
                                    can.drawString(147, 733, ac_reg)
                                    can.drawString(203, 733, ac_msn)
                                    can.drawString(277, 733, ac_eff)
                                    can.drawString(345, 733, operator)

                            # === WEEKLY SUPER AIR JET ===
                            elif template_name == "TC WEEKLY CHECK A320 SUPER AIR JET REV 10.pdf":
                                if i == start_page:
                                    can.drawString(480, 734, work_order)
                                    can.drawString(47, 702, ac_reg)
                                    can.drawString(118, 702, ac_msn)
                                    can.drawString(123, 734, ac_eff)
                                    can.drawString(42, 635, operator)
                                    can.drawString(120, 635, place)
                                    can.drawString(52, 734, ac_type)
                                else:
                                    can.drawString(65, 733, work_order)
                                    can.drawString(147, 733, ac_reg)
                                    can.drawString(203, 733, ac_msn)
                                    can.drawString(277, 733, ac_eff)
                                    can.drawString(345, 733, operator)

                            # === DEFAULT ===
                            else:
                                if i == start_page:
                                    can.drawString(480, 734, work_order)
                                    can.drawString(42, 703, ac_reg)
                                    can.drawString(118, 703, ac_msn)
                                    can.drawString(115, 734, ac_eff)
                                    can.drawString(42, 630, operator)
                                    can.drawString(120, 630, place)
                                    can.drawString(42, 734, ac_type)
                                else:
                                    can.drawString(69, 734, work_order)
                                    can.drawString(149, 734, ac_reg)
                                    can.drawString(206, 734, ac_msn)
                                    can.drawString(270, 734, ac_eff)
                                    can.drawString(360, 734, operator)

                            # Apply Overlay
                            can.save()
                            packet.seek(0)
                            overlay_pdf = PdfReader(packet)
                            page.merge_page(overlay_pdf.pages[0])

                        output.add_page(page)

                    # Save file
                    result = BytesIO()
                    output.write(result)
                    result.seek(0)
                    pdf_data = result.getvalue()
                    b64 = base64.b64encode(pdf_data).decode("utf-8")

                    st.success(f"✅ Taskcard Berhasil Diisi: {template_name} (hal {start_page+1}–{end_page})")
                    st.markdown(f"""
                    <div style="text-align:center; margin-top:20px;">
                        <a href="data:application/pdf;base64,{b64}" 
                           download="FINAL_{template_name.replace('.pdf', '')}.pdf"
                           style="background:#2563eb; color:white; padding:10px 20px; border-radius:8px;
                                  font-weight:600; text-decoration:none;">⬇️ DOWNLOAD TASKCARD</a>
                    </div>
                    <iframe src="data:application/pdf;base64,{b64}" width="100%" height="700px" 
                            style="border:1px solid #ccc; border-radius:10px; margin-top:20px;"></iframe>
                    """, unsafe_allow_html=True)

                except FileNotFoundError:
                    st.error("⚠️ File template tidak ditemukan. Pastikan semua PDF ada di folder yang sama dengan app.py")


# Footer
st.markdown("<hr><p style='text-align:center;color:#94a3b8;'>Dibuat oleh nomnom_</p>", unsafe_allow_html=True)

