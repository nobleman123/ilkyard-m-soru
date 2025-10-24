# questions.py
# Sağladığınız 22211745_SORU_BANKASI_2.pdf dosyasından alınan sorular ve cevap anahtarı.

def get_all_questions():
    """
    PDF'ten çıkarılan tüm soruları konu başlıklarıyla birlikte döndürür.
    Siz buraya PDF'teki 317 sorunun tamamını ekleyebilirsiniz.
    """
    return [
        {
            "id": 1,
            "topic": "Genel İlk Yardım Bilgileri",
            "question": "İlk yardımın tanımı nedir?",
            "options": {
                "A": "Hastanede yapılan müdahaledir.",
                "B": "Olay yerinde ilaç vererek yapılan müdahaledir.",
                "C": "Hastanedeki hekimler tarafından yapılan ilk müdahaledir.",
                "D": "Olay yerinde, hastanın sağlık durumunun daha da kötüleşmesini engellemek amacıyla ilaçsız olarak yapılan müdahaledir."
            },
            "correct_answer": "D",
            "difficulty": "kolay"
        },
        {
            "id": 3,
            "topic": "Genel İlk Yardım Bilgileri",
            "question": "Aşağıdakilerden hangisi ilk yardımın temel uygulamalarından değildir?",
            "options": {
                "A": "Koruma",
                "B": "Bildirme",
                "C": "Kayıt tutma",
                "D": "Kurtarma"
            },
            "correct_answer": "C",
            "difficulty": "kolay"
        },
        {
            "id": 28,
            "topic": "Hasta/Yaralının ve Olay Yerinin Değerlendirilmesi",
            "question": "Erişkin bir insanda dakikadaki normal nabız sayısı kaçtır?",
            "options": {
                "A": "50-80 arası",
                "B": "60-100 arası",
                "C": "110-130 arası",
                "D": "60-150 arası"
            },
            "correct_answer": "B",
            "difficulty": "orta"
        },
        {
            "id": 65,
            "topic": "Temel Yaşam Desteği (TYD)",
            "question": "Yetişkin bir hastada temel yaşam desteği uygulaması sırasında yapılması gereken kalp masajı ve soluk sayısı ne olmalıdır?",
            "options": {
                "A": "1 kalp masajı - 5 soluk",
                "B": "30 kalp masajı - 2 soluk",
                "C": "10 kalp masajı - 1 soluk",
                "D": "5 kalp masajı - 2 soluk"
            },
            "correct_answer": "B",
            "difficulty": "orta"
        },
        {
            "id": 77,
            "topic": "Temel Yaşam Desteği (TYD)",
            "question": "Yetişkinlerde dış kalp masajı sırasında göğüs kemiği kaç santimetre aşağıya çökmelidir?",
            "options": {
                "A": "3 cm",
                "B": "5 cm",
                "C": "6 cm",
                "D": "7 cm"
            },
            "correct_answer": "B",
            "difficulty": "orta"
        },
        {
            "id": 150,
            "topic": "Kanamalarda İlk Yardım",
            "question": "Kanama, kalp atımları ile uyumlu olarak kesik kesik ve fışkırır tarzda akıyorsa ne çeşit bir kanamadır?",
            "options": {
                "A": "Toplardamar kanaması",
                "B": "Atardamar kanaması",
                "C": "Dış kanama",
                "D": "Doğal deliklerden olan kanama"
            },
            "correct_answer": "B",
            "difficulty": "zor"
        },
         {
            "id": 154,
            "topic": "Kanamalarda İlk Yardım",
            "question": "İç kanamalarda ilk yardımda aşağıdakilerden hangisinin uygulanması sakıncalıdır?",
            "options": {
                "A": "Ağızdan sıvı verilerek kayıp önlenir",
                "B": "Şok pozisyonu verilir.",
                "C": "Hastanın üzeri örtülerek sıcak tutulur.",
                "D": "Hasta hareket ettirilmez."
            },
            "correct_answer": "A",
            "difficulty": "zor"
        }
        # ... Buraya PDF'teki diğer 300+ soruyu ekleyin ...
    ]
