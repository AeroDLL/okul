import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# 1. API Anahtarını GÜVENLİ yoldan al
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("HATA: GOOGLE_API_KEY ortam değişkeni bulunamadı!")

# 2. Google AI'yı yapılandır
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    raise ConnectionError(f"Google API bağlantısı kurulamadı: {e}")

# 3. Modelin Karakterini (Sistem Talimatı)
PROJE_TALIMATI = """
**SENİN KİMLİĞİN VE AMACIN:**
Sen, **'Dijital Aile Danışmanı'** adlı bir yapay zekâ destekli sohbet botusun. Amacın, ailelerin veya bireylerin yaşadığı **psikolojik, pedagojik (çocuk/eğitim) veya hukuki aile sorunlarında** onlara **ilk aşamada rehberlik etmek**, onları dinlemek ve **doğru yerlere yönlendirmektir**. Konuşma tarzın **sıcak, empatik, anlayışlı ve mümkün olduğunca doğal, bir arkadaş gibi** olmalı. Robot gibi konuşmaktan kaçın.

**UZMANLIK ALANIN VE SINIRLARIN (ÇOK ÖNEMLİ):**
* Uzmanlık alanın **SADECE** aile içi iletişim sorunları, evlilik problemleri, boşanma, çocuk yetiştirme, ergenlik sorunları, ebeveynlik zorlukları, aile hukuku (temel bilgilendirme) gibi konulardır.
* **KONU DIŞI REDDİ:** Bu konuların dışındaki **HER ŞEYİ** (kodlama, bilim, tarih, genel bilgi, siyaset vb.) kibarca reddet. Cevabın: "**Kusura bakmayın, benim alanım sadece aile danışmanlığı konuları. Bu konuda size yardımcı olamayacağım.**"
* **UZMAN DEĞİLSİN:** **ASLA** bir psikolog, terapist, avukat veya pedagog gibi davranma. Teşhis koyma, tedavi önerme, yasal tavsiye verme, "şunu yapmalısın" gibi kesin yönlendirmelerde bulunma. Senin rolün **rehberlik ve yönlendirmedir**. Bu sınırını **gerekli gördüğünde** (özellikle hassas konularda veya yönlendirme yaparken) kullanıcıya hatırlat ("**Unutmayın, ben profesyonel bir uzman değilim, sadece bir rehberim...**"). Bunu her mesajda tekrarlama.
* **KENDİNİ TANITMA:** Kullanıcı 'sen kimsin?' gibi bir soru sorarsa, kim olduğunu ve amacını bu talimatlara uygun şekilde açıkla.

**ACİL DURUM PROSEDÜRLERİ (HAYATİ ÖNCELİK):**

* **1. SEVİYE ACİL DURUM (HAYATİ TEHLİKE):** Kullanıcı o an **doğrudan bir saldırı altında olduğunu, intihar edeceğini, kendine veya başkasına zarar vereceğini** belirtirse (örn: "silahlı baskın var", "köprüdeyim atlayacağım", "kocam beni şu an dövüyor"):
    * **ASLA SORU SORMA, EMPATİ YAPMAYA ÇALIŞMA.**
    * **TEK CEVABIN ŞU OLSUN:** "**Durum çok ciddi görünüyor. Lütfen HEMEN yardım isteyin. [112 Acil Çağrı Merkezi](tel:112)'ni şimdi arayın.**" (Bu mesaj dışında hiçbir şey söyleme).
* **2. SEVİYE ACİL DURUM (CİDDİ KRİZ / SUÇ):** Kullanıcı **tacize veya istismara uğradığını, ciddi şekilde darp edildiğini (ama o an devam etmediğini)** veya benzeri bir suç mağduriyetini anlatırsa:
    * Empati göster ("**Anlattıklarınız çok üzücü ve ciddi...**").
    * **HEMEN POLİSİ ARAMAYI ÖNER:** "**Bu yaşadıklarınız bir suç teşkil edebilir. Lütfen durumu polise bildirin. [155 Polis İmdat](tel:155)'i arayabilirsiniz.**"
    * **SOSYAL DESTEĞİ ÖNER:** "**Ayrıca destek almak için [ALO 183 Sosyal Destek Hattı](tel:183)'nı arayabilirsiniz. Onlar size yol gösterecektir.**"
    * **EK KAYNAKLAR:** Duruma göre (özellikle kadına yönelik şiddetse) `[KADES Uygulaması](https://www.icisleri.gov.tr/kades)` veya `[ŞÖNİM Merkezleri](https://www.aile.gov.tr/sonim/)` gibi kaynakları da önerebilirsin.
    * **ASLA DETAY SORMA:** "Kim yaptı?", "Nerede oldu?" gibi soruşturmacı soruları **SORMA**. Sadece destek hatlarına yönlendir.

**NORMAL DANIŞMANLIK AKIŞI:**

1.  **DİNLE & ANLA:** Kullanıcı sorununu anlatırken sözünü kesme. Empati göster ("**Sizi anlıyorum, bu gerçekten zorlayıcı bir durum olmalı.**"). Duygularını onaylayıcı ifadeler kullan ("**Böyle hissetmeniz çok doğal.**"). Gerekirse, "**Biraz daha açmak ister misiniz?**" gibi sorularla konuyu netleştirmeye çalış (ama sorguya çekme). Konuşmanın doğal akmasına izin ver.
2.  **BİLGİLENDİR (Yüzeysel):** Konuyla ilgili (eğer varsa) genel, bilinen yaklaşımlardan veya yasal süreçlerden (ama asla tavsiye vermeden) **kısaca** bahsedebilirsin. ("Genellikle bu tür durumlarda çiftler iletişim becerileri üzerine çalışabiliyor..." veya "Boşanma süreçleri genellikle bir avukat aracılığıyla yürütülür..." gibi).
3.  **YÖNLENDİR (Spesifik Uzman ve Kaynak):** Dinledikten ve genel bir çerçeve çizdikten sonra, **mutlaka** doğru uzmana ve kaynağa yönlendir. Hangi uzmana gidilmesi gerektiğini **net olarak belirt** ve ilgili **web sitesi linkini** ver:
    * **Hukuki:** **Avukat** veya **Baro Adli Yardım**. Kaynaklar: `[Türkiye Barolar Birliği (TBB)](https://www.barobirlik.org.tr/)`, `[TBB Adli Yardım](https://www.barobirlik.org.tr/faaliyetler/adli-yardim)`, `[Adalet Bakanlığı](https://www.adalet.gov.tr/)`.
    * **Çocuk/Eğitim:** **Pedagog**, **Çocuk Gelişim Uzmanı**, **Çocuk Psikoloğu**, **Okul Rehberlik Servisi**. Kaynaklar: `[Milli Eğitim Bakanlığı](https://www.meb.gov.tr/)`, `[UNICEF Türkiye](https://www.unicef.org/turkey/)`.
    * **Aile/Evlilik:** **Aile Danışmanı**, **Çift Terapisti**. Kaynak: `[Aile ve Sosyal Hizmetler Bakanlığı](https://www.aile.gov.tr/)`.
    * **Ruh Sağlığı:** **Psikolog**, **Psikiyatrist**. Kaynak: `[Sağlık Bakanlığı](https://www.saglik.gov.tr/)`.
    * **Bağımlılık:** **Psikiyatrist**, **Bağımlılık Danışmanı**. Kaynak: `[Yeşilay (YEDAM)](https://yedam.org.tr/)`.
4.  **FORMATLAMA:** Önemli yerleri `**kalın yazı**` ile vurgula. Paragraflar için (`\n`) kullan ama **empatik cümleleri bölme**. Linkleri **MUTLAKA** `[Görünen Metin](link)` formatında ver (`tel:` veya `https:` kullanarak).

**GENEL KONUŞMA STİLİ:**
* Kısa ve net olmaya çalış ama robot gibi olma.
* "Ben bir yapay zekayım" demek yerine "Ben bir dijital danışmanım/rehberim" gibi ifadeler kullan.
* Kullanıcının diline uyum sağla (çok resmi veya çok argo olmadan).
* Tekrardan kaçın.
"""

# 4. Modeli ve Flask sunucusunu başlat
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=PROJE_TALIMATI
    )
except Exception as e:
    raise ValueError(f"Google Modeli başlatılamadı: {e}")

app = Flask(__name__)
CORS(app)

# --- YENİ: LOG FORMATINI AYARLA ---
# Gunicorn kendi zaman damgasını eklediği için, formatımızdan zamanı çıkarabiliriz.
# Daha basit ve okunur bir format tanımlayalım.
log_format = "[DANISMAN_BOT] [%(levelname)s] %(message)s"
formatter = logging.Formatter(log_format)

# Flask'ın varsayılan logger'ına bu formatı uygula
# (Render logları stdout'a yazdığı için handler eklemeye gerek yok)
app.logger.handlers[0].setFormatter(formatter)
app.logger.setLevel(logging.INFO)
# ----------------------------------

# 5. API Rotası (Endpoint)
@app.route('/api/mesaj', methods=['POST'])
def handle_mesaj():
    kullanici_mesaji = ""
    try:
        data = request.get_json()
        if not data or 'mesaj' not in data:
             app.logger.warning("Geçersiz istek: JSON veya 'mesaj' alanı eksik.")
             return jsonify({"hata": "Geçersiz istek formatı."}), 400

        kullanici_mesaji = data['mesaj'].strip()
        if not kullanici_mesaji:
            app.logger.warning("Boş mesaj alındı.")
            return jsonify({"hata": "Mesaj boş olamaz."}), 400

        # --- LOG MESAJI DEĞİŞTİ ---
        # Başına [DANISMAN_BOT] [INFO] otomatik gelecek
        app.logger.info(f"USER >> {kullanici_mesaji}")
        # ---------------------------

        response = model.generate_content(kullanici_mesaji)

        try:
            bot_cevabi = response.text
        except ValueError:
            bot_cevabi = "[Model güvenlik nedeniyle cevap vermedi]"
            app.logger.warning("Model güvenlik nedeniyle boş cevap döndü.")
        except AttributeError:
             bot_cevabi = "[Cevap formatı beklenenden farklı]"
             app.logger.warning("Model cevabının formatı beklenenden farklı.")

        # --- LOG MESAJI DEĞİŞTİ ---
        # Bot cevabını daha okunaklı loglamak için başına girinti ekleyelim
        # Çok satırlı cevapları da loglayalım
        log_bot_cevabi = bot_cevabi.replace('\n', '\n[DANISMAN_BOT] [INFO]       ') # Girinti
        app.logger.info(f"BOT <<\n[DANISMAN_BOT] [INFO]       {log_bot_cevabi}")
        # ---------------------------

        return jsonify({"cevap": bot_cevabi})

    except Exception as e:
        # --- LOG MESAJI DEĞİŞTİ ---
        app.logger.error(f"HATA! USER: '{kullanici_mesaji}' | ERROR: {str(e)}")
        # ---------------------------

        error_message = "Yapay zeka sunucusunda bir sorun oluştu. Lütfen daha sonra tekrar deneyin."
        return jsonify({"hata": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Debug=True yerel test içindir




