import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os
from google import genai

# Podešavanje stranice
st.set_page_config(page_title="NIS2 Cyber Compliance Simulation", page_icon="🛡️", layout="wide")

# Custom CSS za "Cyber/Corporate" izgled
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { border: 1px solid #3b82f6; color: #3b82f6; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Inicijalizacija Gemini Klijenta
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
client = genai.Client(api_key=api_key) if api_key else None

def generisi_ai_feedback(scenario_naslov, scenario_opis, izabrani_odgovor, uloga, je_tacno):
    if not client:
        return "*(AI Mentor offline - API ključ nedostaje)*"
    
    status_tekst = "usklađenu (compliant)" if je_tacno else "neusklađenu i rizičnu"
    prompt = f"""
    Djeluješ kao NIS2 Compliance Officer. Zaposlenik ('{uloga}') je donio {status_tekst} odluku.
    Scenario: {scenario_naslov}. Situacija: {scenario_opis}. Odgovor: {izabrani_odgovor}.
    Napiši kratku, oštru analizu (max 2 rečenice) na bosanskom jeziku. 
    Objasni uticaj na bezbjednost informacija prema NIS2 direktivi.
    """
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"AI analiza trenutno nedostupna: {str(e)}"

# Baza scenarija (Ozbiljniji naslovi)
scenarios = [
    {"id": 1, "roles": [1, 2], "title": "INCIDENT #001: CEO Fraud & Financial Exposure", "desc": "Zahtjev za hitnom uplatom od 25.000 KM.", "opts": ["Delegiraj računovodstvu", "Direktna verifikacija sa direktorom", "Zahtijevaj formalni pečat"], "correct": 1, "cost": 30000, "rep": 40},
    {"id": 2, "roles": [1, 2, 3, 4], "title": "INCIDENT #002: Unknown Hardware Vector", "desc": "Pronađen USB stik 'Plate_2026' u kuhinji.", "opts": ["Analiza u Safe Mode", "Ostavljanje na recepciji", "Predaja IT bezbjednosnom timu"], "correct": 2, "cost": 40000, "rep": 30},
    {"id": 3, "roles": [1, 2, 4], "title": "INCIDENT #003: Smishing Attack Simulation", "desc": "SMS notifikacija o neuspjeloj dostavi paketa.", "opts": ["Klikni na link", "Blokiraj i obriši", "Proslijedi timu na provjeru"], "correct": 1, "cost": 15000, "rep": 20},
    {"id": 4, "roles": [3], "title": "INCIDENT #004: Network Anomaly Detection", "desc": "Neobjašnjiv skok saobraćaja u 02:00.", "opts": ["Čekaj jutro", "Izolacija servera (Incident Response)", "Restart sistema"], "correct": 1, "cost": 50000, "rep": 50},
    {"id": 5, "roles": [1, 2, 3, 4], "title": "INCIDENT #005: Compromised Workstation", "desc": "Sumnjivo ponašanje kursora i CMD-a.", "opts": ["Isključi mrežu i zovi IT", "Skeniraj besplatnim AV", "Ignoriši - 'sistemsko ažuriranje'"], "correct": 0, "cost": 25000, "rep": 25}
]

def generisi_pdf(ime, uloga, bodovi, max_bodova, budzet, ugled, odgovori):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = [Paragraph("NIS2 AUDIT & COMPLIANCE REPORT", getSampleStyleSheet()['Title'])]
    
    data = [["Kategorija", "Detalji"], ["Zaposlenik", ime], ["Rezultat", f"{bodovi}/{max_bodova}"], ["Status", "Završeno"]]
    t = Table(data, colWidths=[150, 250])
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    for ans in odgovori:
        elements.append(Paragraph(f"<b>{ans['naslov']}</b>", getSampleStyleSheet()['Heading3']))
        elements.append(Paragraph(f"Odgovor: {ans['izbor']}<br/>Analiza: {ans['ai_feedback']}", getSampleStyleSheet()['Normal']))
        elements.append(Spacer(1, 10))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Session State
if 'ge_started' not in st.session_state:
    st.session_state.update({'ge_started': False, 'idx': 0, 'budget': 100000, 'rep': 100, 'score': 0, 'answers': []})

st.title("🛡️ NIS2 Compliance Simulation: Executive Dashboard")

if not st.session_state.ge_started:
    ime = st.text_input("Ime i prezime:")
    uloga = st.selectbox("Pozicija:", ["Menadžment", "Finansije", "IT Sektor", "Administracija"])
    if st.button("Započni simulaciju"):
        st.session_state.update({'ime': ime, 'uloga': uloga, 'ge_started': True})
        st.rerun()
else:
    filtered = scenarios
    idx = st.session_state.idx
    
    if st.session_state.budget <= 0 or st.session_state.rep <= 0 or idx >= len(filtered):
        st.subheader("🏁 Simulacija završena")
        st.metric("Konačni nivo zrelosti", f"{int((st.session_state.score/len(filtered))*100)}%")
        
        if st.download_button("📥 Preuzmi certifikat", data=generisi_pdf(st.session_state.ime, st.session_state.uloga, st.session_state.score, len(filtered), st.session_state.budget, st.session_state.rep, st.session_state.answers), file_name="NIS2_Cert.pdf"):
            pass
    else:
        sc = filtered[idx]
        col1, col2 = st.columns([1, 2])
        col1.metric("Budžet", f"{st.session_state.budget} KM")
        col2.metric("Ugled", f"{st.session_state.rep}%")
        
        st.progress((idx)/len(filtered), text="Napredak kroz audite")
        st.subheader(sc["title"])
        st.info(sc["desc"])
        
        if f"choice_{idx}" not in st.session_state:
            with st.form(f"form_{idx}"):
                ans = st.radio("Vaša odluka:", sc["opts"])
                if st.form_submit_button("Potvrdi odluku"):
                    is_correct = (sc["opts"].index(ans) == sc["correct"])
                    feedback = generisi_ai_feedback(sc["title"], sc["desc"], ans, st.session_state.uloga, is_correct)
                    st.session_state[f"choice_{idx}"] = {"ans": ans, "is_correct": is_correct, "fb": feedback}
                    if not is_correct:
                        st.session_state.budget -= sc["cost"]
                        st.session_state.rep -= sc["rep"]
                    else:
                        st.session_state.score += 1
                    st.session_state.answers.append({"naslov": sc["title"], "izbor": ans, "ai_feedback": feedback})
                    st.rerun()
        else:
            res = st.session_state[f"choice_{idx}"]
            color = "green" if res["is_correct"] else "red"
            st.markdown(f"**STATUS:** :{color}[{'USKLAĐENO' if res['is_correct'] else 'NEUSKLAĐENO'}]")
            st.write(f"**AI Mentor:** {res['fb']}")
            if st.button("Nastavi na sljedeći incident ➡️"):
                st.session_state.idx += 1
                st.rerun()
