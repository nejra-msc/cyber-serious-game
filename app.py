import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os
from google import genai

# Podešavanje stranice za Serious Game atmosferu
st.set_page_config(page_title="CyberDefense: Personalizovana Simulacija", page_icon="🛡️", layout="centered")

# Inicijalizacija Gemini Klijenta
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
client = genai.Client(api_key=api_key) if api_key else None

def generisi_ai_feedback(scenario_naslov, scenario_opis, izabrani_odgovor, uloga, je_tacno):
    """Poziva Gemini AI za generisanje žive, taktičke analize odluke u realnom vremenu."""
    if not client:
        return "*(AI Mentor je trenutno u offline režimu. API ključ nije konfigurisan.)*"
        
    status_tekst = "izvrsnu i odbranu" if je_tacno else "katastrofalnu i rizičnu"
    
    prompt = f"""
    Djeluješ kao elitni AI Cyber Mentor u naprednoj taktičkoj simulaciji.
    Zaposlenik na poziciji '{uloga}' je donio {status_tekst} odluku u sljedećoj situaciji:
    
    Scenario: {scenario_naslov}
    Opis incidenta: {scenario_opis}
    Reakcija zaposlenika: {izabrani_odgovor}
    
    Napiši brzu, dinamičnu i motivišuću analizu (maksimalno 2-3 rečenice) na bosanskom jeziku. 
    Izbjegavaj dosadno spominjanje članova zakona. Umjesto toga, fokusiraj se na praktične taktičke posljedice za firmu i pohvali refleks zaposlenika ili ukaži na propust. 
    Obrati se direktno zaposleniku u drugom licu jednine ("Ti" ili "Vaš račun").
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"AI Mentor je uočio anomaliju u analizi: {str(e)}"

def generisi_ai_titulu(ime, uloga, bodovi, max_bodova, budzet, ugled):
    """Generiše unikatnu, epsku ili duhovitu vojnu/cyber titulu na osnovu stila igre zaposlenika."""
    if not client:
        return "Cyber Specijalista"
        
    prompt = f"""
    Zaposlenik {ime} na poziciji {uloga} je završio igru cyber simulacije sa rezultatom {bodovi}/{max_bodova}.
    Preostali budžet institucije je {budzet} KM, a konačni ugled je {ugled}%.
    
    Smisli jednu unikatnu, moćnu ili blago duhovitu titulu/čin od 2-4 riječi na bosanskom jeziku (npr. 'Neprobojni Štit Računovodstva', 'Digitalni Čuvar Kapije', 'Cyber General Krajine', 'Naivni Kliker na Linkove').
    Vrati ISKLJUČIVO tu titulu, bez ikakvog drugog teksta ili navodnika.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except:
        return "Sertifikovani Cyber Odbrambeni Specijalista"

# Baza scenarija (Zadržavamo strukturu, ali feedback prepuštamo vještačkoj inteligenciji)
scenarios = [
    {
        "id": 1, "roles": [1, 2],
        "title": "Incident 1: Hitni e-mail od direktora (CEO Fraud)",
        "desc": "Na vaš službeni e-mail stiže hitan zahtjev od generalnog direktora. Traži se hitna isplata 25.000 KM na novi račun inostranog dobavljača zbog iznenadnog sudskog poravnanja. Naglašeno je da je stvar povjerljiva i da je direktor na sastanku. Šta radite?",
        "opts": [
            "Odmah prosljeđujem e-mail kolegama u računovodstvu uz nalog da se izvrši uplata.",
            "Zovem direktora na telefon ili odlazim do njegove kancelarije da potvrdim identitet i zahtjev.",
            "Odgovaram na e-mail i tražim skeniranu odluku sa pečatom ustanove."
        ],
        "correct": 1, "cost": 30000, "rep": 40
    },
    {
        "id": 2, "roles": [1, 2, 3, 4],
        "title": "Incident 2: Pronalazak neoznačenog USB stika",
        "desc": "U hodniku ili zajedničkoj kuhinji javne ustanove pronalazite USB stik na kojem flomasterom piše 'Plate_2026'. Koji je vaš sljedeći korak?",
        "opts": [
            "Ubacujem ga u svoj službeni računar u Safe Mode okruženju da vidim čiji je.",
            "Ostavljam ga na vidljivom mjestu na recepciji ili u kuhinji da ga vlasnik sam uzme.",
            "Odnosim stik direktno IT službi ili osobi zaduženoj za bezbjednost, bez spajanja na mrežu."
        ],
        "correct": 2, "cost": 40000, "rep": 30
    },
    {
        "id": 3, "roles": [1, 2, 4],
        "title": "Incident 3: Lažni SMS o dostavi paketa (Smishing)",
        "desc": "Dobijate SMS: 'Vaš paket je zadržan u skladištu zbog nedostatka broja ulice. Kliknite na link-dostava.cc da ažurirate adresu i platite taksu od 1.50 KM.' Kako reagujete?",
        "opts": [
            "Kliknem na link i unesem podatke sa kartice jer često privatno ili poslovno naručujem.",
            "Ne klikam na link, brišem poruku odmah i blokiram pošiljaoca.",
            "Prosljeđujem SMS kolegama kroz interne Viber ili WhatsApp grupe da provjerim."
        ],
        "correct": 1, "cost": 15000, "rep": 20
    },
    {
        "id": 4, "roles": [3],
        "title": "Incident 4: Detekcija anomalija na mrežnom serveru",
        "desc": "Kao IT administrator primjećujete ogroman, neobjašnjiv skok odlaznog mrežnog saobraćaja u 02:00 ujutro sa glavnog servera baza podataka prema nepoznatoj stranoj IP adresi. Šta radite?",
        "opts": [
            "Sačekaću jutarnji sastanak u 08:00 da to prijavim rukovodiocu IT sektora.",
            "Odmah pokrećem proceduru izolacije servera (izvlačenje mrežnog kabla) i aktiviram Incident Response plan.",
            "Restartujem server putem udaljenog pristupa i pratim hoće li se stanje stabilizovati."
        ],
        "correct": 1, "cost": 50000, "rep": 50
    },
    {
        "id": 5, "roles": [1, 2, 3, 4],
        "title": "Incident 5: Sumnjivo ponašanje i usporavanje računara",
        "desc": "Vaš računar odjednom ekstremno usporava rad, kursor se na ekranu pomijera sam od sebe, a komandna linija (CMD) se na sekundu sama upalila i ugasila. Šta radite?",
        "opts": [
            "Isključujem mrežni kabal iz zida (ili gasim Wi-Fi) i odmah telefonom obavještavam IT podršku.",
            "Pretražujem internet i instaliram neki besplatni antivirusni alat da skenira sistem.",
            "Nastavljam sa radom, vjerovatno sistem vrši redovna ažuriranja u pozadini."
        ],
        "correct": 0, "cost": 25000, "rep": 25
    },
    {
        "id": 6, "roles": [1, 4],
        "title": "Incident 6: Fizički neovlašten pristup (Tailgating)",
        "desc": "Nosite gomilu fascikli u osigurani dio arhive ustanove. Nepoznata osoba bez vidljive identifikacione kartice ide tik iza vas i hvata vrata koja ste vi otvorili. Kako reagujete?",
        "opts": [
            "Zahvalim se i pustim osobu da prođe sa mnom jer je očigledno zaposlenik čim je tu.",
            "Spuštam fascikle, zatvaram vrata i ljubazno zamolim osobu da pokaže ID karticu ili da se javi na recepciju.",
            "Ubrzavam korak i pravim se da ne primjećujem ko je iza mene."
        ],
        "correct": 1, "cost": 10000, "rep": 35
    },
    {
        "id": 7, "roles": [1, 2, 3, 4],
        "title": "Incident 7: Pravila kreiranja bezbjedne lozinke",
        "desc": "Sistem vas obavještava da je istekla lozinka za pristup aplikacijama ustanove. Koji metod je prema važećim standardima najbezbjedniji?",
        "opts": [
            "Kratka lozinka od 6 karaktera ali sa mnogo specijalnih znakova (npr. 'P@$w1!').",
            "Dugačka fraza (Passphrase) sastavljena od 4 nasumične riječi (npr. 'KafaKnjigaKrajinaZima2026').",
            "Kombinacija imena odjeljenja i tekuće godine radi lakšeg pamćenja."
        ],
        "correct": 1, "cost": 10000, "rep": 15
    },
    {
        "id": 8, "roles": [1, 3],
        "title": "Incident 8: Rad na daljinu (Remote Work) i bezbjednost",
        "desc": "Za vikend morate hitno od kuće pristupiti informacionom sistemu ustanove da završite izvještaj. Na koji način to činite?",
        "opts": [
            "Pristupam sa privatnog kućnog računara jer na njemu imam instaliran licenciran antivirus.",
            "Koristim službeni laptop spojen direktno na kućni Wi-Fi bez ikakvih dodatnih bezbjednosnih koraka.",
            "Koristim isključivo službeni laptop ustanove uz obavezno pokretanje enkriptovanog VPN tunela."
        ],
        "correct": 2, "cost": 20000, "rep": 30
    }
]

def generisi_pdf(ime, uloga, bodovi, max_bodova, budzet, ugled, odgovori, ai_titula):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    naslov_stil = ParagraphStyle('NaslovStil', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), spaceAfter=15)
    podnaslov_stil = ParagraphStyle('PodnaslovStil', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0F172A'), spaceBefore=10, spaceAfter=10)
    tekst_stil = ParagraphStyle('TekstStil', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
    
    elements = []
    elements.append(Paragraph("TAKTIČKI IZVJEŠTAJ SA CYBERDEFENSE SIMULACIJE", naslov_stil))
    elements.append(Spacer(1, 10))
    
    podaci = [
        [Paragraph("<b>Operativac:</b>", tekst_stil), Paragraph(ime, tekst_stil)],
        [Paragraph("<b>Sektor odbrane:</b>", tekst_stil), Paragraph(uloga, tekst_stil)],
        [Paragraph("<b>AI Cyber Titula:</b>", tekst_stil), Paragraph(f"<b>{ai_titula}</b>", tekst_stil)],
        [Paragraph("<b>Uspješnost presretanja:</b>", tekst_stil), Paragraph(f"{bodovi} od {max_bodova} incidenata", tekst_stil)],
        [Paragraph("<b>Sačuvani budžet:</b>", tekst_stil), Paragraph(f"{budzet:,} KM", tekst_stil)],
        [Paragraph("<b>Konačni integritet (Ugled):</b>", tekst_stil), Paragraph(f"{ugled}%%", tekst_stil)]
    ]
    
    t = Table(podaci, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("DETALJNA ANALIZA CYBER INCIDENATA", podnaslov_stil))
    for i, ans in enumerate(odgovori):
        elements.append(Paragraph(f"<b>{i+1}. {ans['naslov']}</b>", tekst_stil))
        elements.append(Paragraph(f"Status: {ans['status']}", tekst_stil))
        elements.append(Paragraph(f"Izbor operativca: {ans['izbor']}", tekst_stil))
        elements.append(Paragraph(f"<b>Taktički osvrt AI Mentora:</b> {ans['ai_feedback']}", tekst_stil))
        elements.append(Spacer(1, 10))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Inicijalizacija session_state-a
if 'ge_started' not in st.session_state:
    st.session_state.ge_started = False
    st.session_state.current_idx = 0
    st.session_state.budget = 100000
    st.session_state.reputation = 100
    st.session_state.score = 0
    st.session_state.user_answers = []

st.title("🛡️ CyberDefense: Taktika i Simulacija Prijetnji")
st.caption("Personalizovani Serious Game trening za jačanje odbrambenih refleksa institucije")

with st.sidebar:
    st.subheader("⚡ Odbrambeni AI Sistem")
    if client:
        st.success("AI CyberMentor je aktivan i analizira tvoje korake! 🧠")
    else:
        st.warning("AI je u offline modu. Provjerite Secrets.")

if not st.session_state.ge_started:
    st.subheader("Kreiraj svoj profil operativca")
    ime = st.text_input("Unesi svoje ime operativca:", placeholder="Npr. Nejra Skenderović")
    uloga = st.selectbox("Izaberi svoj sektor djelovanja:", [
        "Menadžment i upravljanje",
        "Finansije, računovodstvo i pravni poslovi",
        "IT služba i tehnička podrška",
        "Opća administracija i logistika"
    ])
    
    if st.button("Pokreni misiju i uđi u simulaciju 🚀", use_container_width=True):
        if ime.strip() == "":
            st.error("Identifikacija je obavezna! Unesite ime.")
        else:
            st.session_state.ime = ime
            st.session_state.uloga = uloga
            role_map = {"Menadžment i upravljanje": 1, "Finansije, računovodstvo i pravni poslovi": 2, "IT služba i tehnička podrška": 3, "Opća administracija i logistika": 4}
            st.session_state.role_id = role_map[uloga]
            st.session_state.filtered = [s for s in scenarios if st.session_state.role_id in s["roles"]]
            st.session_state.ge_started = True
            st.rerun()

else:
    filtered = st.session_state.filtered
    idx = st.session_state.current_idx
    
    if st.session_state.budget <= 0 or st.session_state.reputation <= 0 or idx >= len(filtered):
        st.subheader("🏁 Simulacija završena!")
        
        is_win = st.session_state.budget > 0 and st.session_state.reputation > 0
        
        # Generisanje jedinstvene AI titule na osnovu rezultata igre
        if 'ai_titula' not in st.session_state:
            with st.spinner("🧠 AI evaluira tvoj stil odbrane i kuje tvoju unikatnu titulu..."):
                st.session_state.ai_titula = generisi_ai_titulu(
                    st.session_state.ime, st.session_state.uloga,
                    st.session_state.score, len(filtered),
                    st.session_state.budget, st.session_state.reputation
                )

        if is_win:
            st.balloons()
            st.success(f"Čestitamo operativcu **{st.session_state.ime}**! Uspješno ste neutralisali prijetnje.")
            st.info(f"🏅 Dodijeljena Vam je AI Cyber Titula: **{st.session_state.ai_titula}**")
        else:
            st.error(f"🚨 KRAH SISTEMA! Vaša institucija je pretrpjela masovnu eksfiltraciju podataka. AI Titula: **{st.session_state.ai_titula}**")
            
        # Prikaz gejmifikovanih završnih metrika
        c1, c2, c3 = st.columns(3)
        c1.metric("Preostali novac", f"{st.session_state.budget:,} KM")
        c2.metric("Integritet firme", f"{st.session_state.reputation}%")
        c3.metric("Neutralisano", f"{st.session_state.score} / {len(filtered)}")
        
        pdf_data = generisi_pdf(
            st.session_state.ime, st.session_state.uloga, 
            st.session_state.score, len(filtered),
            st.session_state.budget, st.session_state.reputation,
            st.session_state.user_answers, st.session_state.ai_titula
        )
        
        st.download_button(
            label="📥 Preuzmi taktički izvještaj za Rukovodstvo (PDF)",
            data=pdf_data,
            file_name=f"CyberDefense_Izvjestaj_{st.session_state.ime.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        if st.button("Pokreni novu simulaciju 🔄"):
            st.session_state.clear()
            st.rerun()
            
    else:
        # Dinamički indikatori (Health Bars)
        st.write("### Stanje sistema ustanove")
        
        # Određivanje boja za budžet i ugled na osnovu kritičnosti (Gamification)
        b_color = "green" if st.session_state.budget > 50000 else "orange" if st.session_state.budget > 20000 else "red"
        r_color = "green" if st.session_state.reputation > 60 else "orange" if st.session_state.reputation > 30 else "red"
        
        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; margin-bottom: 20px;'>
            <div style='padding: 10px; border-radius: 5px; background-color: #f0f2f6; width: 30%; text-align: center; border-left: 5px solid {b_color};'>
                <b>💰 BUDŽET:</b> {st.session_state.budget:,} KM
            </div>
            <div style='padding: 10px; border-radius: 5px; background-color: #f0f2f6; width: 30%; text-align: center; border-left: 5px solid {r_color};'>
                <b>📈 INTEGRITET:</b> {st.session_state.reputation}%
            </div>
            <div style='padding: 10px; border-radius: 5px; background-color: #f0f2f6; width: 30%; text-align: center; border-left: 5px solid #1E3A8A;'>
                <b>📊 INCIDENT:</b> {idx + 1} / {len(filtered)}
            </div>
        </div>
        """, unsafe_html=True)
        
        sc = filtered[idx]
        st.write("---")
        st.subheader(sc["title"])
        st.warning(sc["desc"])
        
        if f"potvrđeno_{idx}" not in st.session_state:
            with st.form(key=f"sc_form_{idx}"):
                odgovor = st.radio("Izaberi tvoju trenutnu odbrambenu reakciju:", sc["opts"])
                potvrdi = st.form_submit_button("Aktiviraj odluku 📡")
                
                if potvrdi:
                    chosen_idx = sc["opts"].index(odgovor)
                    is_correct = (chosen_idx == sc["correct"])
                    
                    with st.spinner("📡 AI Mentor vrši forenziku tvoje odluke..."):
                        ai_comment = generisi_ai_feedback(sc["title"], sc["desc"], odgovor, st.session_state.uloga, is_correct)
                    
                    st.session_state[f"odgovor_{idx}"] = odgovor
                    st.session_state[f"is_correct_{idx}"] = is_correct
                    st.session_state[f"ai_comment_{idx}"] = ai_comment
                    st.session_state[f"potvrđeno_{idx}"] = True
                    
                    status = "USPJEŠNO ODBRANJENO" if is_correct else "PROPUST U ODBRANI"
                    st.session_state.user_answers.append({
                        "naslov": sc["title"],
                        "izbor": odgovor,
                        "status": status,
                        "ai_feedback": ai_comment
                    })
                    
                    if is_correct:
                        st.session_state.score += 1
                    else:
                        st.session_state.budget -= sc["cost"]
                        st.session_state.reputation -= sc["rep"]
                    st.rerun()
        else:
            odgovor = st.session_state[f"odgovor_{idx}"]
            is_correct = st.session_state[f"is_correct_{idx}"]
            ai_comment = st.session_state[f"ai_comment_{idx}"]
            
            st.radio("Tvoja izabrana reakcija:", sc["opts"], index=sc["opts"].index(odgovor), disabled=True)
            
            if is_correct:
                st.success(f"💥 **Sjajan refleks! Napad je neutralisan.** \n\n 🤖 **AI CyberMentor:** {ai_comment}")
            else:
                st.error(f"⚠️ **Sistem probijen! Pretrpljena je šteta.** \n\n 🤖 **AI CyberMentor:** {ai_comment}")
                
            if st.button("Nastavi na sljedeći incident ➡️"):
                st.session_state.current_idx += 1
                st.rerun()
