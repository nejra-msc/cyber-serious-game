import streamlit as st
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os
from google import genai

# Podešavanje stranice
st.set_page_config(page_title="CyberDefense: Personalizovana Simulacija", page_icon="🛡️", layout="centered")

# Inicijalizacija Gemini Klijenta
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
client = genai.Client(api_key=api_key) if api_key else None

# --- AI FUNKCIJE ---

def generisi_ai_feedback(scenario_naslov, scenario_opis, izabrani_odgovor, uloga, je_tacno):
    if not client: return "AI Mentor je offline."
    status_tekst = "izvrsnu" if je_tacno else "rizičnu"
    prompt = f"Djeluj kao AI Cyber Mentor. Zaposlenik ('{uloga}') je donio {status_tekst} odluku u situaciji: {scenario_naslov}. Opis: {scenario_opis}. Njegov izbor: {izabrani_odgovor}. Napiši 2 motivišuće rečenice analize na bosanskom jeziku, fokusirano na taktiku."
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except: return "Analiza trenutno nije dostupna."

def generisi_ai_titulu(ime, uloga, bodovi, max_bodova):
    if not client: return "Cyber Specijalista"
    prompt = f"Zaposlenik {ime} ({uloga}) je ostvario {bodovi}/{max_bodova}. Smisli unikatnu, moćnu titulu na bosanskom jeziku (npr. 'Digitalni Čuvar Kapije'). Vrati samo titulu."
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except: return "Cyber Branilac"

# --- PDF GENERATOR (CERTIFIKAT) ---

def generisi_pdf(ime, uloga, bodovi, max_bodova, budzet, ugled, ai_titula):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    cert_naslov = ParagraphStyle('CertNaslov', parent=styles['Heading1'], fontSize=28, textColor=colors.HexColor('#1E3A8A'), alignment=1, spaceAfter=10)
    ime_stil = ParagraphStyle('ImeStil', parent=styles['Heading2'], fontSize=24, textColor=colors.HexColor('#0F172A'), alignment=1, spaceAfter=20)
    tekst_stil = ParagraphStyle('TekstStil', parent=styles['Normal'], fontSize=12, leading=18, alignment=1, spaceAfter=30)
    titla_stil = ParagraphStyle('TitlaStil', parent=styles['Normal'], fontSize=16, textColor=colors.HexColor('#D97706'), alignment=1, spaceAfter=30)
    
    elements = [Paragraph("<b>CERTIFIKAT O USPJEŠNOJ OBUCI</b>", cert_naslov), Spacer(1, 20), Paragraph(f"<b>{ime}</b>", ime_stil)]
    elements.append(Paragraph(f"za uspješno učešće u simulaciji cyber prijetnji za sektor <b>{uloga}</b>. Pokazali ste izuzetan nivo svijesti o digitalnoj bezbjednosti.", tekst_stil))
    elements.append(Paragraph(f"Stečeni AI Cyber čin: <b>{ai_titula.upper()}</b>", titla_stil))
    
    def dodaj_borduru(canvas, doc):
        canvas.setStrokeColor(colors.HexColor('#1E3A8A')); canvas.rect(15, 15, 760, 580, stroke=1, fill=0)
        canvas.setStrokeColor(colors.HexColor('#F59E0B')); canvas.rect(20, 20, 750, 570, stroke=1, fill=0)
        
    doc.build(elements, onFirstPage=dodaj_borduru)
    buffer.seek(0)
    return buffer

# --- BAZA SCENARIJA ---

scenarios = [
    {"id": 1, "roles": [1, 2], "title": "CEO Fraud", "desc": "Hitan mail od direktora za uplatu 25.000 KM.", "opts": ["Uplati odmah", "Provjeri telefonom", "Traži pečat"], "correct": 1, "cost": 30000, "rep": 40},
    {"id": 2, "roles": [1, 2, 3, 4], "title": "USB Stik", "desc": "Pronađen USB 'Plate_2026' u hodniku.", "opts": ["Uključi da vidiš", "Ostavi na stolu", "Odnesi IT-u"], "correct": 2, "cost": 40000, "rep": 30}
]

# --- STREAMLIT UI ---

if 'ge_started' not in st.session_state:
    st.session_state.update({'ge_started': False, 'current_idx': 0, 'budget': 100000, 'reputation': 100, 'score': 0})

st.title("🛡️ CyberDefense: Simulacija")

if not st.session_state.ge_started:
    ime = st.text_input("Ime operativca:")
    uloga = st.selectbox("Sektor:", ["Menadžment", "Finansije", "IT Služba", "Administracija"])
    if st.button("Pokreni misiju"):
        st.session_state.update({'ime': ime, 'uloga': uloga, 'ge_started': True})
        st.rerun()
else:
    idx = st.session_state.current_idx
    if idx >= len(scenarios):
        st.success("🏁 Misija završena!")
        if 'titula' not in st.session_state: st.session_state.titula = generisi_ai_titulu(st.session_state.ime, st.session_state.uloga, st.session_state.score, len(scenarios))
        st.info(f"🏅 Tvoja titula: {st.session_state.titula}")
        pdf = generisi_pdf(st.session_state.ime, st.session_state.uloga, st.session_state.score, len(scenarios), st.session_state.budget, st.session_state.reputation, st.session_state.titula)
        st.download_button("🎓 Preuzmi Certifikat", data=pdf, file_name="Certifikat.pdf", mime="application/pdf")
    else:
        sc = scenarios[idx]
        st.subheader(sc["title"])
        st.write(sc["desc"])
        odgovor = st.radio("Tvoj izbor:", sc["opts"])
        if st.button("Potvrdi"):
            is_correct = (sc["opts"].index(odgovor) == sc["correct"])
            if is_correct: st.session_state.score += 1
            else: st.session_state.budget -= sc["cost"]
            st.session_state.current_idx += 1
            st.rerun()
