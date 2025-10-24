# app.py
import streamlit as st
import google.generativeai as genai
import random
import pandas as pd
from questions import get_all_questions # Diğer dosyadan soruları içe aktar

# --- YAPAY ZEKA AYARLARI ---
# Kullanıcının kendi API anahtarını girmesi için bir alan
# BU ANAHTARI GİT'E VEYA PUBLIC REPO'LARA YÜKLEMEYİN!
try:
    # St.secrets'tan API anahtarını okumayı dene (Streamlit Cloud için)
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    # Lokal'de çalışıyorsa kenar çubuğundan al
    GEMINI_API_KEY = st.sidebar.text_input("Gemini API Anahtarınız:", type="password")

if not GEMINI_API_KEY:
    st.info("Lütfen devam etmek için kenar çubuğuna Gemini API anahtarınızı girin.")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Anahtarı yapılandırılırken bir hata oluştu: {e}")
    st.stop()


# --- YARDIMCI FONKSİYONLAR ---

def get_explanation(question, correct_option_text, user_answer_text):
    """
    Yapay zekadan sorunun açıklamasını alır.
    """
    prompt = f"""
    Aşağıdaki ilk yardım sorusu için bir açıklama yap:

    Soru: {question['question']}
    Doğru Cevap: ({question['correct_answer']}) {correct_option_text}
    Kullanıcının Cevabı: {user_answer_text}

    Açıklama: Lütfen bu sorunun doğru cevabının neden '{correct_option_text}' olduğunu ve kullanıcının cevabı yanlışsa neden yanlış olduğunu kısaca ve net bir şekilde Türkçe açıkla. 
    Açıklamanı doğrudan yap, 'Elbette, işte açıklama:' gibi girizgahlar kullanma.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Açıklama getirilirken bir hata oluştu: {e}"

def initialize_session_state():
    """
    Streamlit session state'i başlatır.
    """
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

# Sayfa başlığı ve ayarları
st.set_page_config(page_title="İlk Yardım Soru Robotu", layout="centered")
st.title("🤖 İlk Yardım Soru Robotu")

# Session state'i başlat
initialize_session_state()

# --- 1. ARAYÜZ: TEST SEÇİMİ (Ana Sayfa) ---
if not st.session_state.quiz_active:
    
    st.subheader("Teste Başlamaya Hazır Mısınız?")
    st.markdown("Lütfen bir konu seçin ve testteki soru sayısını belirleyin.")

    all_questions = st.session_state.all_questions
    # Konuları dinamik olarak al
    topics = ["Tüm Konular (Karma)"] + sorted(list(set(q["topic"] for q in all_questions)))
    
    selected_topic = st.selectbox("Bir konu seçin:", topics)
    
    num_questions = st.slider(
        "Kaç soru çözmek istersiniz?", 
        min_value=5, 
        max_value=20, # Performans için makul bir sınır
        value=10, 
        step=1
    )

    if st.button("Teste Başla", type="primary"):
        # Seçilen konuya göre soruları filtrele
        if selected_topic == "Tüm Konular (Karma)":
            available_questions = all_questions
        else:
            available_questions = [q for q in all_questions if q["topic"] == selected_topic]
        
        # Yeterli soru yoksa, mevcut olan kadarını al
        num_questions = min(num_questions, len(available_questions))
        
        # Soruları karıştır ve seç
        st.session_state.selected_questions = random.sample(available_questions, num_questions)
        
        # Testi başlatmak için state'leri sıfırla
        st.session_state.quiz_active = True
        st.session_state.current_question_index = 0
        st.session_state.user_answers = []
        st.session_state.show_explanation = False
        st.rerun() # Sayfayı yeniden çalıştırarak test arayüzüne geç

# --- 2. ARAYÜZ: TEST ÇÖZME ---
elif st.session_state.current_question_index < len(st.session_state.selected_questions):
    
    # Mevcut soruyu al
    q_index = st.session_state.current_question_index
    question = st.session_state.selected_questions[q_index]
    
    total_questions = len(st.session_state.selected_questions)
    
    # Soru ilerlemesini göster
    st.progress((q_index + 1) / total_questions)
    st.subheader(f"Soru {q_index + 1} / {total_questions}")
    st.markdown(f"**Konu:** {question['topic']}")
    st.markdown(f"---")
    
    # Soru metni
    st.markdown(f"### {question['question']}")

    # Seçenekleri oluştur
    # (A, B, C, D) sırasını korumak için
    options_list = list(question['options'].items())
    
    # 'key' parametresi, soru değiştiğinde radio butonunun sıfırlanmasını sağlar
    user_choice_key = st.radio(
        "Cevabınızı seçin:",
        [f"{key}) {value}" for key, value in options_list],
        key=f"q_{question['id']}",
        disabled=st.session_state.show_explanation # Cevap verildiğinde seçenekleri kilitle
    )
    
    # Kullanıcının seçtiği harfi (A, B, C, D) al
    user_selected_key = user_choice_key.split(')')[0]

    # "Cevabı Kontrol Et" butonu
    if st.button("Cevabı Kontrol Et", disabled=st.session_state.show_explanation):
        # Cevabı kaydet
        is_correct = (user_selected_key == question['correct_answer'])
        st.session_state.user_answers.append({
            "question_id": question['id'],
            "question_text": question['question'],
            "topic": question['topic'],
            "user_answer": user_selected_key,
            "correct_answer": question['correct_answer'],
            "is_correct": is_correct
        })
        
        st.session_state.show_explanation = True # Açıklama gösterme modunu aç
        st.rerun() # Geri bildirimi göstermek için sayfayı yeniden yükle

    # Cevap kontrol edildikten sonra gösterilecekler
    if st.session_state.show_explanation:
        correct_key = question['correct_answer']
        correct_answer_text = question['options'][correct_key]
        user_answer_text = question['options'][user_selected_key]

        if st.session_state.user_answers[-1]['is_correct']:
            st.success(f"**Doğru!** 🥳")
        else:
            st.error(f"**Yanlış!** 😕 Doğru cevap: **{correct_key}) {correct_answer_text}**")

        # Yapay zekadan açıklama al ve göster
        with st.spinner("Yapay zeka cevabı açıklıyor..."):
            explanation = get_explanation(question, correct_answer_text, user_answer_text)
            st.info(explanation)
        
        # Sonraki soru butonu
        if st.button("Sonraki Soru", type="primary"):
            st.session_state.current_question_index += 1
            st.session_state.show_explanation = False # Açıklama modunu kapat
            st.rerun() # Bir sonraki soru için yeniden yükle

# --- 3. ARAYÜZ: TEST SONUÇLARI ---
else:
    st.balloons()
    st.subheader("🎉 Testi Tamamladınız!")
    
    total_questions = len(st.session_state.selected_questions)
    correct_answers = sum(1 for answer in st.session_state.user_answers if answer['is_correct'])
    score = (correct_answers / total_questions) * 100

    # PDF'teki başarı puanına göre seviye belirle [kaynak: 1716]
    if score >= 85:
        level = "Başarılı (85+ Puan)"
        st.success(f"**Toplam Puanınız: {score:.1f}%**")
    else:
        level = "Geliştirilmeli (<85 Puan)"
        st.warning(f"**Toplam Puanınız: {score:.1f}%**")
        
    st.metric(label="Seviyeniz", value=level)
    st.metric(label="Sonuç", value=f"{correct_answers} / {total_questions} Doğru")
    
    st.markdown("---")
    
    # İsteğiniz: "hangi konularda eksik onu tespit et"
    st.subheader("Konu Performans Analiziniz")
    
    df = pd.DataFrame(st.session_state.user_answers)
    
    # Konulara göre başarıyı hesapla
    topic_performance = df.groupby('topic')['is_correct'].mean() * 100
    topic_performance = topic_performance.reset_index()
    topic_performance.columns = ['Konu', 'Başarı Yüzdesi']
    
    st.dataframe(topic_performance.style.format({'Başarı Yüzdesi': '{:.1f}%'}))
    
    # Grafiksel gösterim
    st.bar_chart(topic_performance.set_index('Konu'))
    
    # Hatalı cevapların özeti
    wrong_answers = df[df['is_correct'] == False]
    if not wrong_answers.empty:
        st.markdown("---")
        st.subheader("Gözden Geçirmeniz Gereken Sorular")
        for _, row in wrong_answers.iterrows():
            with st.expander(f"❌ **Soru:** {row['question_text']}"):
                st.write(f"**Sizin Cevabınız:** {row['user_answer']}")
                st.write(f"**Doğru Cevap:** {row['correct_answer']}")

    # Yeniden Başla Butonu
    if st.button("Yeni Teste Başla"):
        # Tüm state'i sıfırla
        st.session_state.quiz_active = False
        st.session_state.current_question_index = 0
        st.session_state.selected_questions = []
        st.session_state.user_answers = []
        st.session_state.show_explanation = False
        st.rerun()
