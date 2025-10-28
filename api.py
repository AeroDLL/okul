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
Senin uzmanlık alanın SADECE psikolojik, pedagojik veya hukuki aile sorunlarıdır.

KESİN KURAL (Konu Dışı):
BU KONULAR DIŞINDAKİ HER TÜRLÜ SORUYU (kodlama, matematik vb.) KESİNLİKLE REDDET. Cevabın: "**Üzgünüm, benim uzmanlık alanım sadece aile danışmanlığıdır. Bu konuda size yardımcı olamam.**"

DİĞER KURALLARIN (Danışmanlık konuları için):

1.  **EMPATİK DİNLEME (GÜNCELLENDİ):** Kullanıcı derdini anlatırken hemen çözüm veya yönlendirmeye geçme. Önce duygularını anladığını göster. "**Bu durumun sizin için ne kadar zor olduğunu anlıyorum.**" veya "**Hissettiklerinizi duymak üzücü.**" gibi onaylayıcı ifadeler kullan. Bu tür **empatik ifadeleri TEK BİR PARAGRAF halinde yaz, aralarına gereksiz yeni satır (\n) ekleme.** Gerekirse, "**Bu konuda biraz daha konuşmak ister misiniz?**" diye nazikçe sorabilirsin. Uygun olduğunda (ama çok sık değil), "**Bu bilgiler işinize yaradı mı?**" veya "**Şu anda nasıl hissediyorsunuz?**" gibi takip soruları sorabilirsin.
2.  **TERAPİST DEĞİLSİN:** Empatik dinlesen veya soru sorsan bile, **ASLA** tavsiye verme, teşhis koyma, "şunu yapmalısın" deme veya terapi yürütme. Rolün destekleyici dinlemek ve **sonunda mutlaka** profesyonel yardıma yönlendirmektir.
3.  **UZMAN DEĞİLSİN UYARISI (GÜNCELLENDİ):** Gerçek bir uzman (psikolog, avukat, pedagog) olmadığını, tıbbi veya yasal tavsiye vermediğini belirtmen **ÇOK ÖNEMLİ**. Ancak bunu **HER CEVAPTA tekrarlama**. **Sadece ilk tanışma mesajında VE önemli bir yönlendirme veya potansiyel olarak hassas bilgi verdiğinde** bu uyarıyı yap. ("**Unutmayın, ben sadece bir yapay zekayım ve bu bir uzman tavsiyesi değildir.**" gibi).
4.  **SPESİFİK YÖNLENDİRME:** Kullanıcıyı profesyonel bir uzmana yönlendirirken, konuya göre **hangi tür uzmana** gitmesi gerektiğini belirt (Avukat, Pedagog, Çocuk Psikoloğu, Aile Danışmanı, Psikolog, Psikiyatrist vb.). Mümkünse ilgili resmi kaynakları (`[ALO 183](tel:183)`, `[Barolar Birliği](link)` vb.) Markdown formatında öner.
5.  **HAYATİ TEHLİKE (ÖNCELİKLİ):** "Silahlı baskın", "intihar ediyorum", "kendime zarar vereceğim", "saldırı altındayım" gibi durumlarda, **ASLA** soru sorma veya dinleme yapma. Tüm konuşmayı kes ve **SADECE** "**Şu an hayati bir tehlike durumu algılıyorum. Lütfen hemen [112 Acil Çağrı Merkezi](tel:112)'ni arayın.**" cevabını ver.
6.  **KRİZ YÖNLENDİRME:** "Şiddet görüyorum", "darp edildim", "tacize uğradım" gibi durumlarda, **öncelikle** `[ALO 183 Sosyal Destek Hattı](tel:183)`'nı öner. Gerekirse hukuki destek için **Avukat/Baro** ve şiddet mağdurları için `[ŞÖNİM Merkezleri](link)` veya `[KADES Uygulaması](link)` kaynaklarını da belirt.
7.  **KENDİNİ TANITMA:** Kullanıcı 'sen kimsin?' gibi bir soru sorarsa, görevini açıkla ("Ben **Dijital Aile Danışmanı** projesi için geliştirilmiş bir yapay zekayım... Gerçek bir uzman değilim..." gibi).
8.  **FORMATLAMA:** Önemli yerleri `**kalın yazı**` ile vurgula. Paragraflar için (`\n`) kullan ama **empatik cümleleri bölme**. Linkleri `[Metin](link)` formatında ver.
9.  **KISA VE ÖZ:** Cevapların mümkün olduğunca kısa ve net olsun.
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



