import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import datetime
import os

# --- KONFIGURASI API ---
# Masukkan API Key kamu di sini atau gunakan environment variable
API_KEY = "AIzaSyARRFWJP3lut7i9T8L3lIJFfV_JE1zyr4k"
genai.configure(api_key=API_KEY)

# --- KONFIGURASI MODEL ---
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNGSI LOGIKA ---
def get_ai_analysis(image):
    """Mengirim gambar ke Gemini dan mendapatkan data nutrisi dalam format JSON"""
    prompt = """
    Analisis foto makanan ini. Berikan estimasi nutrisi dalam format JSON mentah (tanpa markdown, tanpa kata-kata lain).
    Format harus persis seperti ini:
    {
      "nama_makanan": "nama makanan",
      "kalori": 0,
      "protein": 0,
      "karbohidrat": 0,
      "lemak": 0
    }
    Jika ada beberapa makanan, totalkan semuanya. Jika bukan foto makanan, berikan nilai 0 pada semua angka.
    """
    response = model.generate_content([prompt, image])
    
    # Membersihkan response agar hanya mengambil JSON
    text_response = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(text_response)

def reset_hari_ini():
    """Menghapus data hari ini dan memulai hari baru"""
    st.session_state.log_makanan = []
    st.session_state.total_nutrisi = {"kalori": 0, "protein": 0, "karbo": 0, "lemak": 0}
    st.session_state.tanggal_aktif = str(datetime.date.today())
    st.success("Hari baru dimulai! Data telah direset.")

# --- INISIALISASI STATE ---
if 'log_makanan' not in st.session_state:
    st.session_state.log_makanan = []
if 'total_nutrisi' not in st.session_state:
    st.session_state.total_nutrisi = {"kalori": 0, "protein": 0, "karbo": 0, "lemak": 0}

# --- TAMPILAN UI (STREAMLIT) ---
st.set_page_config(page_title="AI Photo Calorie Tracker", layout="centered")

st.title("📸 AI Calorie Tracker")
st.subheader(f"Target Hari Ini: {datetime.date.today().strftime('%A, %d %B %Y')}")

# Sidebar untuk Kontrol
with st.sidebar:
    st.header("Kontrol")
    if st.button("🔄 Mulai / Ganti Hari Baru"):
        reset_hari_ini()
    
    st.divider()
    st.write("Aplikasi ini menggunakan AI untuk mengestimasi nutrisi dari foto. Pastikan pencahayaan foto jelas.")

# Layout Dashboard (4 Kolom)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Kalori", f"{st.session_state.total_nutrisi['kalori']} kcal")
col2.metric("Protein", f"{st.session_state.total_nutrisi['protein']}g")
col3.metric("Karbo", f"{st.session_state.total_nutrisi['karbo']}g")
col4.metric("Lemak", f"{st.session_state.total_nutrisi['lemak']}g")

st.divider()

# Input Foto
st.write("### 🍽️ Tambah Makanan")
img_file = st.camera_input("Ambil foto makanan") # Bisa pakai kamera HP/Laptop
# Atau jika ingin upload file:
# img_file = st.file_uploader("Atau upload foto", type=['jpg', 'png', 'jpeg'])

if img_file:
    img = Image.open(img_file)
    
    with st.spinner('AI sedang menganalisis makananmu...'):
        try:
            data = get_ai_analysis(img)
            
            # Tampilkan Hasil Analisis
            st.success(f"Terdeteksi: {data['nama_makanan']}")
            
            # Konfirmasi Tambah ke Database
            if st.button(f"Konfirmasi Tambah {data['kalori']} kkal"):
                # Update State
                st.session_state.log_makanan.append(data)
                st.session_state.total_nutrisi['kalori'] += data['kalori']
                st.session_state.total_nutrisi['protein'] += data['protein']
                st.session_state.total_nutrisi['karbo'] += data['karbohidrat']
                st.session_state.total_nutrisi['lemak'] += data['lemak']
                st.rerun() # Refresh tampilan
                
        except Exception as e:
            st.error(f"Gagal menganalisis gambar. Pastikan API Key benar. Error: {e}")

# Riwayat Hari Ini
st.divider()
st.write("### 📜 Riwayat Makan Hari Ini")
if not st.session_state.log_makanan:
    st.info("Belum ada makanan yang dicatat.")
else:
    for idx, item in enumerate(st.session_state.log_makanan):

        st.write(f"{idx+1}. **{item['nama_makanan']}** - {item['kalori']} kcal (P: {item['protein']}g, K: {item['karbohidrat']}g, L: {item['lemak']}g)")
