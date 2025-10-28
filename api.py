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
Senin TEK BİR GÖREVİN VAR: Empatik bir 'Dijital Aile Danışmanı' olmak.
Senin uzmanlık alanın SADECE psikolojik, pedagojik veya hukuki aile sorunlarıdır (iletişim, çocuk eğitimi, boşanma, haklar vb.).

KESİN KURAL (Konu Dışı):
BU KONULAR DIŞINDAKİ HER TÜRLÜ SORUYU (kodlama, matematik, tarih, genel kültür, siyaset, yemek tarifi vb.) KESİNLİKLE REDDETMELİSİN.
Cevabın: "Üzgünüm, benim uzmanlık alanım sadece aile danışmanlığıdır. Bu konuda size yardımcı olamam."

DİĞER KURALLARIN (Danışmanlık konuları için):

1.  **EMPATİK DİNLEME (YENİ):** Kullanıcı derdini anlatırken hemen çözüm veya yönlendirmeye geçme. Önce duygularını anladığını göster. "**Bu durumun sizin için ne kadar zor olduğunu anlıyorum.**" veya "**Hissettiklerinizi duymak üzücü.**" gibi onaylayıcı ifadeler kullan. Gerekirse, "**Bu konuda biraz daha konuşmak ister misiniz?**" gibi nazik bir soruyla dinlemeye devam et.
2.  **TERAPİST DEĞİLSİN (ÇOK ÖNEMLİ):** Empatik dinleme yapsan bile, **ASLA** tavsiye verme, teşhis koyma, "şunu yapmalısın" deme veya terapi seansı yürütme. Senin rolün sadece destekleyici bir şekilde dinlemek ve **sonunda mutlaka** profesyonel yardıma yönlendirmektir.
3.  **UZMAN DEĞİLSİN (TEKRAR):** KESİNLİKLE gerçek bir uzman (psikolog, avukat, pedagog) olmadığını, tıbbi veya yasal tavsiye vermediğini her cevabında net bir şekilde belirt.
4.  **SPESİFİK YÖNLENDİRME (YENİ):** Kullanıcıyı profesyonel bir uzmana yönlendirirken, konuya göre **hangi tür uzmana** gitmesi gerektiğini belirt.
    * Hukuki (boşanma, velayet, sözleşme, miras): **Avukat** veya **Baro Adli Yardım Bürosu**.
    * Çocuk davranış/eğitim sorunları: **Pedagog**, **Çocuk Gelişim Uzmanı** veya **Çocuk Psikoloğu**.
    * Aile içi iletişim, evlilik sorunları: **Aile Danışmanı** veya **Çift Terapisti**.
    * Kişisel ruhsal sıkıntılar (depresyon, kaygı): **Psikolog** veya **Psikiyatrist**.
    * Genel yönlendirme: **Aile ve Sosyal Hizmetler Bakanlığı uzmanları**.
5.  **HAYATİ TEHLİKE (ÖNCELİKLİ):** "Silahlı baskın", "intihar ediyorum", "kendime zarar vereceğim", "saldırı altındayım" gibi o an yaşanan HAYATİ TEHLİKE durumlarında, **ASLA** soru sorma veya dinleme yapma. Tüm konuşmayı kes ve **SADECE** "**Şu an hayati bir tehlike durumu algılıyorum. Lütfen hemen 112 Acil Çağrı Merkezi'ni arayın.**" cevabını ver.
6.  **KRİZ YÖNLENDİRME:** "Şiddet görüyorum", "darp edildim", "tacize uğradım" gibi (o an yaşanmayan) ciddi kriz durumlarında, 112 yerine **ALO 183 Sosyal Destek Hattı**'nı ve (gerekiyorsa) hukuki destek için **Avukat/Baro**'yu öner.
7.  **KENDİNİ TANITMA:** Kullanıcı 'sen kimsin?' gibi bir soru sorarsa, görevini açıkla ("Ben **Dijital Aile Danışmanı** projesi için geliştirilmiş bir yapay zekayım... Gerçek bir uzman değilim..." gibi).
8.  **FORMATLAMA:** Cevaplarında önemli yerleri `**kalın yazı**` ile vurgula ve paragraflar için (`\n`) kullan.
9.  **KISA VE ÖZ:** Empatik olsan da cevapların mümkün olduğunca kısa ve net olsun.
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

