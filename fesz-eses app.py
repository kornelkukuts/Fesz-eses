import math
import csv
import io
import streamlit as st

st.set_page_config(
    page_title="Feszültségesés Kalkulátor",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Feszültségesés Kalkulátor")
st.markdown("Számítsd ki a vezetékek feszültségesését és teljesítményveszteségét az alábbi paraméterek megadásával.")

with st.form("feszultseg_form"):
    st.subheader("Paraméterek megadása")
    
    hossz = st.number_input("Vezeték hossza (m, egyirányú):", min_value=0.1, value=10.0, step=1.0)
    aram = st.number_input("Áramerősség (A):", min_value=0.1, value=16.0, step=1.0)
    keresztmetszet = st.number_input("Keresztmetszet (mm²):", min_value=0.1, value=1.5, step=0.5)
    rendszer_fesz = st.number_input("Névleges feszültség (V):", min_value=1.0, value=400.0, step=1.0)
    cos_phi = st.number_input("Teljesítménytényező (cos φ):", min_value=0.01, max_value=1.0, value=0.95, step=0.01)
    
    col1, col2 = st.columns(2)
    with col1:
        anyag = st.radio("Vezető anyaga:", ["CU", "AL"], index=0)
    with col2:
        fazis = st.radio("Rendszer típusa:", ["3 fázis (4 vezetékes)", "1 fázis"], index=0)
        
    submitted = st.form_submit_button("Számítás", type="primary")

if submitted:
    try:
        # Anyagellenállás fajlagos értéke
        rho = 0.0283 if anyag == "AL" else 0.0175
        anyag_nev = "AL" if anyag == "AL" else "CU"

        if fazis == "3 fázis (4 vezetékes)":
            dU = (math.sqrt(3) * hossz * aram * rho * cos_phi) / keresztmetszet
            veszteseg_teljesitmeny = (aram ** 2) * (3 * rho * hossz / keresztmetszet)
        else:
            dU = (2 * hossz * aram * rho * cos_phi) / keresztmetszet
            veszteseg_teljesitmeny = (aram ** 2) * (2 * rho * hossz / keresztmetszet)

        szazalek = (dU / rendszer_fesz) * 100.0
        feszultseg_utan = rendszer_fesz - dU

        st.markdown("---")
        st.subheader("Eredmények")

        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="Esett feszültség (dU)", value=f"{dU:.3f} V")
            st.metric(label="Százalékos esés", value=f"{szazalek:.2f}%")
        with col_res2:
            st.metric(label="Feszültség esés után", value=f"{feszultseg_utan:.3f} V")
            st.metric(label="Veszteség teljesítmény", value=f"{veszteseg_teljesitmeny:.2f} W")
        with col_res3:
            st.metric(label="Vezető / Rendszer", value=f"{anyag_nev} | {fazis}")

        if szazalek > 3.0:
            st.warning("⚠️ Figyelem: A feszültségesés meghaladja a 3%-os ajánlott határt!")
        else:
            st.success("✅ A feszültségesés a megengedett határon belül van.")

        # CSV adatok előkészítése letöltéshez
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["Paraméter / Eredmény", "Érték", "Mértékegység"])
        writer.writerow(["Vezeték hossza", str(hossz).replace(".", ","), "m"])
        writer.writerow(["Áramerősség", str(aram).replace(".", ","), "A"])
        writer.writerow(["Keresztmetszet", str(keresztmetszet).replace(".", ","), "mm2"])
        writer.writerow(["Névleges feszültség", str(rendszer_fesz).replace(".", ","), "V"])
        writer.writerow(["Teljesítménytényező (cos phi)", str(cos_phi).replace(".", ","), "-"])
        writer.writerow(["Vezető anyaga", anyag_nev, "-"])
        writer.writerow(["Rendszer típusa", fazis, "-"])
        writer.writerow(["Esett feszültség (dU)", f"{dU:.3f}".replace(".", ","), "V"])
        writer.writerow(["Feszültség esés után", f"{feszultseg_utan:.3f}".replace(".", ","), "V"])
        writer.writerow(["Százalékos esés", f"{szazalek:.2f}".replace(".", ","), "%"])
        writer.writerow(["Veszteség teljesítmény", f"{veszteseg_teljesitmeny:.2f}".replace(".", ","), "W"])

        csv_data = output.getvalue().encode("utf-8-sig")

        st.download_button(
            label="📥 Eredmények mentése CSV-be",
            data=csv_data,
            file_name="feszultsegeses_eredmenyek.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Hiba történt a számítás során: {e}")