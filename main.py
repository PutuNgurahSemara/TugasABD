import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Dashboard
st.title("Dashboard Donasi Lingkungan")

data = pd.DataFrame({
    "Kampanye": ["Mangrove Balikpapan", "Pantai Samboja", "Delta Mahakam"],
    "Donasi": [120, 85, 60],
    "Target": [150, 100, 90]
})

kampanye = st.selectbox("Pilih Kampanye:", data["Kampanye"])
row = data[data["Kampanye"] == kampanye].iloc[0]

st.metric("Donasi Saat Ini", f"Rp{row['Donasi']} juta", delta=row['Donasi'] - row['Target'])
st.progress(row['Donasi'] / row['Target'])

fig, ax = plt.subplots()
ax.bar(data["Kampanye"], data["Donasi"], color="green")
ax.set_ylabel("Donasi (juta)")
st.pyplot(fig)

st.image("peakpx.jpg", caption="Kegiatan Penanaman Mangrove di Balikpapan")
st.markdown("""
### Tujuan Program
Meningkatkan kesadaran masyarakat terhadap pentingnya ekosistem mangrove.
""")