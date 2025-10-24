# streamlit_app.py
import streamlit as st
import google.generativeai as genai
import random
import pandas as pd
from questions import get_all_questions # Diğer dosyadan soruları içe aktar

# --- SAYFA YAPILANDIRMASI ---
# Gönderdiğiniz HTML'deki Kızılay logosunu ve başlığını kullanalım
st.set_page_config(
    page_title="İlk Yardım Test Platformu",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Turkish_Red_Crescent_logo.svg/1200px-Turkish_Red_Crescent_logo.svg.png",
    layout="wide"
)

# --- CSS İLE ARAYÜZÜ GÜZELLEŞTİRME ---
# Gönderdiğiniz HTML'deki renk paletine benzer bir stil
st.markdown("""
<style>
    /* Kızılay Kırmızı Renkleri */
    .stApp {
        background-color: #f5f5f5;
    }
    .stButton > button {
        background-color: #d32f2f;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #b71c1c;
        color: white;
    }
    .stRadio > div {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        background-color: white;
    }
    [data-testid="stSidebar"] {
        background-color: white;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- YAN ÇUBUK (SIDEBAR) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Turkish_Red_Crescent_logo.svg/1200px-Turkish_Red_Crescent_logo.svg.png", width=100)
st.sidebar.title("İlk Yardım Platformu")

# --- API ANAHTARI VE MODEL YAPILANDIRMASI ---
try:
    # St.secrets'tan API anahtarını okumayı dene (Streamlit Cloud için)
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    # Lokal'de çalışıyorsa kenar çubuğundan al
    GEMINI_API_KEY = st.sidebar.text_input("Gemini API Anahtarınız:", type="password", help="API anahtarınızı Google AI Studio'dan alabilirsiniz.")

if not GEMINI_API_KEY:
    st.sidebar.warning("Lütfen devam etmek için Gemini API anahtarınızı girin.")
    st.info("Lütfen teste başlamak için sol kenar çubuğuna Gemini API anahtarınızı girin.")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # !!! HATA DÜZELTMESİ BURADA !!!
    # 'gemini-1.5-flash' yerine evrensel olarak kullanılabilen 'gemini-pro' modelini kullanıyoruz.
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"API Anahtarı yapılandırılırken bir hata oluştu: {e}")
    st.stop()


# --- YARDIMCI FONKSİYONLAR ---

def get_explanation(question_data):
    """
    Yapay zekadan sorunun açıklamasını alır.
    """
    question = question_data['question']
    correct_key = question_data['correct_answer']
    correct_option_text = question_data['options'][correct_key]

    prompt = f"""
    Bir ilk yardım eğitmeni olarak, aşağıdaki soruyu ve doğru cevabını açıklayın:

    Soru: {question}
    Doğru Cevap: ({correct_key}) {correct_option_text}

    Açıklama: Lütfen bu sorunun doğru cevabının neden '{correct_option_text}' olduğunu kısaca ve net bir şekilde Türkçe açıkla. 
    Açıklamanı doğrudan yap, 'Elbette, işte açıklama:' gibi girizgahlar kullanma.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hata durumunda kullanıcıya daha net bir mesaj göster
        st.error(f"Yapay zeka açıklaması alınamadı: {e}")
        return "Açıklama getirilirken bir sorun oluştu. Lütfen API anahtarınızı veya model adınızı kontrol edin."

def initialize_session_state():
    """ Streamlit session state'i başlatır. """
    if 'all_questions' not in st.session_state:
        st.session_state.all_questions = get_all_questions()
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'show_explanation' not in st.session_state:
        st.session_state.show_explanation = False

# --- UYGULAMA ARAYÜZÜ ---

# Session state'i başlat
initialize_session_state()

# Ana başlık
st.title("🤖 Kızılay İlk Yardım Test Platformu")
st.markdown("Bilginizi ölçün, eksiklerinizi görün ve kendinizi geliştirin.")

# --- 1. ARAYÜZ: TEST SEÇİMİ (Ana Sayfa) ---
if not st.session_state.quiz_active:
    
    st.header("Test Ayarları")
    st.markdown("Lütfen bir konu, zorluk seviyesi ve soru sayısı seçin.")

    all_questions = st.session_state.all_questions
    
    # Konuları ve zorlukları dinamik olarak al
    topics = ["Tüm Konular (Karma)"] + sorted(list(set(q["topic"] for q in all_questions)))
    difficulties = ["Tüm Seviyeler"] + sorted(list(set(q["difficulty"] for q in all_questions)))
    
    col1, col2 = st.columns(2)
    with col1:
        selected_topic = st.selectbox("Bir konu seçin:", topics)
        num_questions = st.slider(
            "Soru Sayısı:", 
            min_value=3, 
            max_value=20, 
            value=5, 
            step=1
        )
    with col2:
        selected_difficulty = st.selectbox("Bir zorluk seviyesi seçin:", difficulties)
        
    if st.button("Teste Başla", type="primary", use_container_width=True):
        # Soruları filtrele
        available_questions = all_questions
        if selected_topic != "Tüm Konular (Karma)":
            available_questions = [q for q in available_questions if q["topic"] == selected_topic]
        if selected_difficulty != "Tüm Seviyeler":
            available_questions = [q for q in available_questions if q["difficulty"] == selected_difficulty]
        
        # Yeterli soru yoksa, mevcut olan kadarını al
        if not available_questions:
            st.error("Bu kriterlere uygun soru bulunamadı. Lütfen seçiminizi değiştirin.")
        else:
            num_questions = min(num_questions, len(available_questions))
            st.session_state.selected_questions = random.sample(available_questions, num_questions)
            
            # Testi başlatmak için state'leri sıfırla
            st.session_state.quiz_active = True
            st.session_state.current_question_index = 0
            st.session_state.user_answers = []
            st.session_state.show_explanation = False
            st.rerun()

# --- 2. ARAYÜZ: TEST ÇÖZME ---
elif st.session_state.current_question_index < len(st.session_state.selected_questions):
    
    q_index = st.session_state.current_question_index
    question = st.session_state.selected_questions[q_index]
    total_questions = len(st.session_state.selected_questions)
    
    # Soru ilerlemesini göster
    st.progress((q_index + 1) / total_questions, text=f"Soru {q_index + 1} / {total_questions}")
    
    # Zorluk seviyesine göre renkli etiket
    difficulty_color = {"kolay": "green", "orta": "orange", "zor": "red"}
    st.markdown(f"**Konu:** {question['topic']} | **Zorluk:** <span style='color:{difficulty_color.get(question['difficulty'], 'black')};'>**{question['difficulty'].upper()}**</span>", unsafe_allow_html=True)
    
    st.divider()
    
    # Soru metni
    st.subheader(f"{question['question']}")

    # Seçenekler
    options_list = list(question['options'].items())
    user_choice_key = st.radio(
        "Cevabınızı seçin:",
        [f"{key}) {value}" for key, value in options_list],
        key=f"q_{question['id']}",
        disabled=st.session_state.show_explanation,
        index=None # Başlangıçta hiçbir şey seçili olmasın
    )
    
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        # "Cevabı Kontrol Et" butonu
        if st.button("Cevabı Kontrol Et", disabled=st.session_state.show_explanation or user_choice_key is None):
            user_selected_key = user_choice_key.split(')')[0]
            is_correct = (user_selected_key == question['correct_answer'])
            
            st.session_state.user_answers.append({
                "question_id": question['id'],
                "question_text": question['question'],
                "topic": question['topic'],
                "user_answer": user_selected_key,
                "user_answer_text": question['options'][user_selected_key],
                "correct_answer": question['correct_answer'],
                "correct_answer_text": question['options'][question['correct_answer']],
                "is_correct": is_correct
            })
            
            st.session_state.show_explanation = True
            st.rerun()

    with col2:
        # "Sonraki Soru" butonu (sadece açıklama gösteriliyorsa aktif)
        if st.session_state.show_explanation:
            st.button("Sonraki Soru" if q_index < total_questions - 1 else "Testi Bitir", type="primary", on_click=lambda: (
                st.session_state.update(
                    current_question_index=st.session_state.current_question_index + 1,
                    show_explanation=False
                )
            ), use_container_width=True)

    # Cevap kontrol edildikten sonra gösterilecekler
    if st.session_state.show_explanation:
        last_answer = st.session_state.user_answers[-1]
        
        if last_answer['is_correct']:
            st.success(f"**Doğru!** 🥳")
        else:
            st.error(f"**Yanlış!** 😕 Doğru cevap: **{last_answer['correct_answer']}) {last_answer['correct_answer_text']}**")

        # Yapay zekadan açıklama al ve göster
        with st.spinner("Yapay zeka cevabı açıklıyor..."):
            explanation = get_explanation(question)
            st.info(f"**Yapay Zeka Açıklaması:**\n{explanation}")

# --- 3. ARAYÜZ: TEST SONUÇLARI ---
else:
    st.balloons()
    st.header("🎉 Testi Tamamladınız!")
    
    total_questions = len(st.session_state.selected_questions)
    correct_answers = sum(1 for answer in st.session_state.user_answers if answer['is_correct'])
    score = (correct_answers / total_questions) * 100

    # PDF'teki başarı puanına göre seviye belirle
    level = "Başarılı (85+ Puan)" if score >= 85 else "Geliştirilmeli (<85 Puan)"
        
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Toplam Puan", value=f"{score:.1f}%")
    col2.metric(label="Sonuç", value=f"{correct_answers} / {total_questions}")
    col3.metric(label="Seviyeniz", value=level)
    
    st.divider()
    
    # "hangi konularda eksik onu tespit et"
    st.subheader("Konu Performans Analiziniz")
    
    df = pd.DataFrame(st.session_state.user_answers)
    
    # Konulara göre başarıyı hesapla
    topic_performance = df.groupby('topic')['is_correct'].mean().reset_index()
    topic_performance['Başarı Yüzdesi'] = topic_performance['is_correct'] * 100
    
    st.dataframe(
        topic_performance[['topic', 'Başarı Yüzdesi']],
        column_config={
            "topic": "Konu",
            "Başarı Yüzdesi": st.column_config.ProgressColumn(
                "Başarı Yüzdesi",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Hatalı cevapların özeti
    wrong_answers = [a for a in st.session_state.user_answers if not a['is_correct']]
    if wrong_answers:
        st.divider()
        st.subheader("Gözden Geçirmeniz Gereken Sorular")
        for answer in wrong_answers:
            with st.expander(f"❌ **Soru:** {answer['question_text']}"):
                st.error(f"**Sizin Cevabınız:** {answer['user_answer']}) {answer['user_answer_text']}")
                st.success(f"**Doğru Cevap:** {answer['correct_answer']}) {answer['correct_answer_text']}")

    st.divider()
    # Yeniden Başla Butonu
    if st.button("Yeni Teste Başla", type="primary"):
        # Tüm state'i sıfırla
        st.session_state.quiz_active = False
        st.session_state.current_question_index = 0
        st.session_state.selected_questions = []
        st.session_state.user_answers = []
        st.session_state.show_explanation = False
        st.rerun()
