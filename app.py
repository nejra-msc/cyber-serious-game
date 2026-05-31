import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# Podešavanje stranice
st.set_page_config(page_title="NIS2 Cyber Serious Game", page_icon="🛡️", layout="centered")

# Baza scenarija
scenarios = [
    {
        "id": 1, "roles": [1, 2],
        "title": "Scenario 1: Hitni e-mail od direktora (CEO Fraud)",
        "desc": "Na vaš službeni e-mail stiže hitan zahtjev od generalnog direktora. Traži se hitna isplata 25.000 KM na novi račun inostranog dobavljača zbog iznenadnog sudskog poravnanja. Naglašeno je da je stvar povjerljiva i da je direktor na sastanku. Šta radite?",
        "opts": [
            "Odmah prosljeđujem e-mail kolegama u računovodstvu uz nalog da se izvrši uplata.",
            "Zovem direktora na telefon ili odlazim do njegove kancelarije da potvrdim identitet i zahtjev.",
            "Odgovaram na e-mail i tražim skeniranu odluku sa pečatom ustanove."
        ],
        "correct": 1, "cost": 30000, "rep": 40,
        "feedback": "Empirijski podaci iz vaše ustanove pokazuju dramatičan rizik: čak 56.5% zaposlenika pravi fatalnu grešku prosljeđivanja ovog maila unutar sistema! Provjera nezavisnim kanalom (uživo ili fiksni telefon) je jedini NIS2 usklađen odgovor."
    },
    {
        "id": 2, "roles": [1, 2, 3, 4],
        "title": "Scenario 2: Pronalazak neoznačenog USB stika",
        "desc": "U hodniku ili zajedničkoj kuhinji javne ustanove pronalazite USB stik na kojem flomasterom piše 'Plate_2026'. Koji je vaš sljedeći korak?",
        "opts": [
            "Ubacujem ga u svoj službeni računar u Safe Mode okruženju da vidim čiji je.",
            "Ostavljam ga na vidljivom mjestu na recepciji ili u kuhinji da ga vlasnik sam uzme.",
            "Odnosim stik direktno IT službi ili osobi zaduženoj za bezbjednost, bez spajanja na mrežu."
        ],
        "correct": 2, "cost": 40000, "rep": 30,
        "feedback": "U vašoj ustanovi 65.2% zaposlenika ispravno postupa i odnosi stik u IT. Ipak, preostalih 34.8% koji bi ga ostavili na stolu ili uključili predstavljaju otvoren ulaz za ransomware napade koji kriptuju servere."
    },
    {
        "id": 3, "roles": [1, 2, 4],
        "title": "Scenario 3: Lažni SMS o dostavi paketa (Smishing)",
        "desc": "Dobijate SMS: 'Vaš paket je zadržan u skladištu zbog nedostatka broja ulice. Kliknite na link-dostava.cc da ažurirate adresu i platite taksu od 1.50 KM.' Kako reagujete?",
        "opts": [
            "Kliknem na link i unesem podatke sa kartice jer često privatno ili poslovno naručujem.",
            "Ne klikam na link, brišem poruku odmah i blokiram pošiljaoca.",
            "Prosjeđujem SMS kolegama kroz interne Viber ili WhatsApp grupe da provjerim."
        ],
        "correct": 1, "cost": 15000, "rep": 20,
        "feedback": "Čak 34.8% zaposlenika u anketi pokazuje ranjivost na ovaj napad kroz klikanje ili dijeljenje kroz nezaštićene chat kanale. Brisanje i blokada štite finansijska sredstva i podatke ustanove."
    },
    {
        "id": 4, "roles": [3],
        "title": "Scenario 4: Detekcija anomalija na mrežnom serveru",
        "desc": "Kao IT administrator primjećujete ogroman, neobjašnjiv skok odlaznog mrežnog saobraćaja u 02:00 ujutro sa glavnog servera baza podataka prema nepoznatoj stranoj IP adresi. Šta radite?",
        "opts": [
            "Sačekaću jutarnji sastanak u 08:00 da to prijavim rukovodiocu IT sektora.",
            "Odmah pokrećem proceduru izolacije servera (izvlačenje mrežnog kabla) i aktiviram Incident Response plan.",
            "Restartujem server putem udaljenog pristupa i pratim hoće li se stanje stabilizovati."
        ],
        "correct": 1, "cost": 50000, "rep": 50,
        "feedback": "Usklađenost sa NIS2 direktivom nalaže hitno provođenje faze suzbijanja (Containment). Svako odlaganje ili puki restart omogućava potpunu eksfiltraciju povjerljivih podataka građana."
    },
    {
        "id": 5, "roles": [1, 2, 3, 4],
        "title": "Scenario 5: Sumnjivo ponašanje i usporavanje računara",
        "desc": "Vaš računar odjednom ekstremno usporava rad, kursor se na ekranu pomijera sam od sebe, a komandna linija (CMD) se na sekundu sama upalila i ugasila. Šta radite?",
        "opts": [
            "Isključujem mrežni kabal iz zida (ili gasim Wi-Fi) i odmah telefonom obavještavam IT podršku.",
            "Pretražujem internet i instaliram neki besplatni antivirusni alat da skenira sistem.",
            "Nastavljam sa radom, vjerovatno sistem vrši redovna ažuriranja u pozadini."
        ],
        "correct": 0, "cost": 25000, "rep": 25,
        "feedback": "Svega 47.8% zaposlenika u vašoj ustanovi ispravno izoluje uređaj iz mreže. Fizičko isključenje sprječava širenje malicioznog koda na ostale računare unutar institucije."
    },
    {
        "id": 6, "roles": [1, 4],
        "title": "Scenario 6: Fizički neovlašten pristup (Tailgating)",
        "desc": "Nosite gomilu fascikli u osigurani dio arhive ustanove. Nepoznata osoba bez vidljive identifikacione kartice ide tik iza vas i hvata vrata koja ste vi otvorili. Kako reagujete?",
        "opts": [
            "Zahvalim se i pustim osobu da prođe sa mnom jer je očigledno zaposlenik čim je tu.",
            "Spuštam fascikle, zatvaram vrata i ljubazno zamolim osobu da pokaže ID karticu ili da se javi na recepciju.",
            "Ubrzavam korak i pravim se da ne primjećujem ko je iza mene."
        ],
        "correct": 1, "cost": 10000, "rep": 35,
        "feedback": "Odlično! Čak 78.3% ispitanika u vašoj firmi ispravno prepoznaje opasnost od Tailgating-a. Kontrola fizičkog pristupa je ključna komponenta informacione bezbjednosti."
    },
    {
        "id": 7, "roles": [1, 2, 3, 4],
        "title": "Scenario 7: Pravila kreiranja bezbjedne lozinke",
        "desc": "Sistem vas obavještava da je istekla lozinka za pristup aplikacijama ustanove. Koji metod je prema važećim standardima najbezbjedniji?",
        "opts": [
            "Kratka lozinka od 6 karaktera ali sa mnogo specijalnih znakova (npr. 'P@$w1!').",
            "Dugačka fraza (Passphrase) sastavljena od 4 nasumične riječi (npr. 'KafaKnjigaKrajinaZima2026').",
            "Kombinacija imena odjeljenja i tekuće godine radi lakšeg pamćenja."
        ],
        "correct": 1, "cost": 10000, "rep": 15,
        "feedback": "Svega 21.7% ispitanika prepoznaje prednost dugih fraza. Dužina lozinke pruža znatno veću matematičku otpornost na Brute-Force napade nego sama kompleksnost."
    },
    {
        "id": 8, "roles": [1, 3],
        "title": "Scenario 8: Rad na daljinu (Remote Work) i bezbjednost",
        "desc": "Za vikend morate hitno od kuće pristupiti informacionom sistemu ustanove da završite izvještaj. Na koji način to činite?",
        "opts": [
            "Pristupam sa privatnog kućnog računara jer na njemu imam instaliran licenciran antivirus.",
            "Koristim službeni laptop spojen direktno na kućni Wi-Fi bez ikakvih dodatnih bezbjednosnih koraka.",
            "Koristim isključivo službeni laptop ustanove uz obavezno pokretanje enkriptovanog VPN tunela."
        ],
        "correct": 2, "cost": 20000, "rep": 30,
        "feedback": "Oko 60.9% zaposlenih ispravno prepoznaje važnost VPN-a. Uz upotrebu privatnih neprovjerenih uređaja (BYOD) u javnim institucijama predstavlja ogroman i po NIS2 kažnjiv rizik."
    }
]

def generisi_pdf(ime, uloga, bodovi, max_bodova, budzet, ugled, odgovori):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom stilovi bez čudnih karaktera radi izbjegavanja grešaka u ReportLab-u
    naslov_stil = ParagraphStyle('NaslovStil', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), spaceAfter=15)
    podnaslov_stil = ParagraphStyle('PodnaslovStil', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0F172A'), spaceBefore=10, spaceAfter=10)
    tekst_stil = ParagraphStyle('TekstStil', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
    
    elements = []
    elements.append(Paragraph("IZVJESTAJ O REZULTATIMA CYBER OBUKE (NIS2)", naslov_stil))
    elements.append(Spacer(1, 10))
    
    podaci = [
        [Paragraph("<b>Zaposlenik:</b>", tekst_stil), Paragraph(ime, tekst_stil)],
        [Paragraph("<b>Odjeljenje:</b>", tekst_stil), Paragraph(uloga, tekst_stil)],
        [Paragraph("<b>Rezultat:</b>", tekst_stil), Paragraph(f"{bodovi} od {max_bodova} tacnih odgovora", tekst_stil)],
        [Paragraph("<b>Preostali budzet:</b>", tekst_stil), Paragraph(f"{budzet:,} KM", tekst_stil)],
        [Paragraph("<b>Konacni ugled:</b>", tekst_stil), Paragraph(f"{ugled}%", tekst_stil)]
    ]
    
    t = Table(podaci, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("METRIKA PO SCENARIJIMA", podnaslov_stil))
    for i, ans in enumerate(odgovori):
        elements.append(Paragraph(f"<b>{i+1}. {ans['naslov']}</b>", tekst_stil))
        elements.append(Paragraph(f"Status odluke: {ans['status']}", tekst_stil))
        elements.append(Paragraph(f"Izabrani odgovor: {ans['izbor']}", tekst_stil))
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

st.title("🛡️ Adaptivni NIS2 Cyber Serious Game")
st.caption("Personalizovana obuka i evaluacija zrelosti javnih institucija")

if not st.session_state.ge_started:
    st.subheader("Inicijalizacija obuke zaposlenika")
    ime = st.text_input("Ime i prezime zaposlenika:", placeholder="Npr. Nejra Skenderović")
    uloga = st.selectbox("Sistematizacija radnog mjesta:", [
        "Menadžment i upravljanje",
        "Finansije, računovodstvo i pravni poslovi",
        "IT služba i tehnička podrška",
        "Opća administracija i logistika"
    ])
    
    if st.button("Pokreni personalizovani trening 🚀", use_container_width=True):
        if ime.strip() == "":
            st.error("Molimo unesite ime i prezime!")
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
        st.subheader("🏁 Trening simulacija završena!")
        
        is_win = st.session_state.budget > 0 and st.session_state.reputation > 0
        if is_win:
            st.success(f"Zaposlenik **{st.session_state.ime}** je uspješno završio obuku!")
            if st.session_state.score == len(filtered):
                st.balloons()
                st.warning("🏆 NAGRADA: Zlatni NIS2 Certifikat cyber izvrsnosti!")
            else:
                st.info("🥈 NAGRADA: Srebrni NIS2 Certifikat o obuci.")
        else:
            st.error("🚨 KRITIČAN INCIDENT - GAME OVER! Ustanova je pretrpjela krah sistema.")
            
        st.metric("Konačni Budžet", f"{st.session_state.budget:,} KM")
        st.metric("Konačni Ugled Ustanove", f"{st.session_state.reputation}%")
        st.metric("Tačni Odgovori", f"{st.session_state.score} / {len(filtered)}")
        
        # Generisanje PDF-a
        pdf_data = generisi_pdf(
            st.session_state.ime, st.session_state.uloga, 
            st.session_state.score, len(filtered),
            st.session_state.budget, st.session_state.reputation,
            st.session_state.user_answers
        )
        
        st.download_button(
            label="📥 Preuzmi službeni PDF izvještaj za Direktora",
            data=pdf_data,
            file_name=f"NIS2_Izvjestaj_{st.session_state.ime.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        if st.button("Pokreni ponovo 🔄"):
            st.session_state.clear()
            st.rerun()
            
    else:
        # Dashboard
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 BUDŽET", f"{st.session_state.budget:,} KM")
        col2.metric("📈 UGLED", f"{st.session_state.reputation}%")
        col3.metric("📊 PROGRES", f"{idx + 1} / {len(filtered)}")
        
        sc = filtered[idx]
        st.write("---")
        st.subheader(sc["title"])
        st.info(sc["desc"])
        
        form = st.form(key=f"sc_form_{idx}")
        odgovor = form.radio("Izaberite vašu reakciju:", sc["opts"])
        potvrdi = form.form_submit_button("Potvrdi odluku 📝")
        
        if potvrdi:
            chosen_idx = sc["opts"].index(odgovor)
            is_correct = (chosen_idx == sc["correct"])
            
            status = "TAČNO" if is_correct else "NETAČNO"
            st.session_state.user_answers.append({
                "naslov": sc["title"],
                "izbor": odgovor,
                "status": status
            })
            
            if is_correct:
                st.session_state.score += 1
                st.success(f"**Odluka je ispravna!** \n\n 🤖 CyberMentor: {sc['feedback']}")
            else:
                st.session_state.budget -= sc["cost"]
                st.session_state.reputation -= sc["rep"]
                st.error(f"**Kritičan propust!** \n\n 🤖 CyberMentor: {sc['feedback']}")
                
            st.session_state.current_idx += 1
            st.button("Nastavi dalje ➡️")