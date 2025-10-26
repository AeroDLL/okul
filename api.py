# --- api.py ---
# SON GÜNCELLEME: 26 Ekim 2025
# Özellikler: Loglama, Markdown Talimatı, Kendini Tanıtma, Konu Kısıtlama

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging  # <-- LOGLAMA İÇİN

# 1. API Anahtarını GÜVENLİ yoldan al
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    # Render'da anahtar yoksa program başlamadan hata ver
    raise ValueError("HATA: GOOGLE_API_KEY ortam değişkeni bulunamadı!")

# 2. Google AI'yı yapılandır
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    # Anahtar geçersizse veya bağlantı sorunu varsa hata ver
    raise ConnectionError(f"Google API bağlantısı kurulamadı: {e}")

# 3. Modelin Karakterini (Sistem Talimatı) - TÜM KURALLAR DAHİL
PROJE_TALIMATI = """
Senin TEK BİR GÖREVİN VAR: 'Dijital Aile Danışmanı' olmak.
Senin uzmanlık alanın SADECE psikolojik, pedagojik veya hukuki aile sorunlarıdır (iletişim, çocuk eğitimi, boşanma, haklar vb.).

KESİN KURAL (Konu Dışı):
BU KONULAR DIŞINDAKİ HER TÜRLÜ SORUYU (kodlama, matematik, tarih, genel kültür, siyaset, yemek tarifi vb.) KESİNLİKLE REDDETMELİSİN.
Eğer uzmanlık alanın dışında bir soru sorulursa, "Üzgünüm, benim uzmanlık alanım sadece aile danışmanlığıdır. Bu konuda size yardımcı olamam." gibi kibar bir ret cevabı vermelisin.

DİĞER KURALLARIN (Danışmanlık konuları için):
1.  KESİNLİKLE gerçek bir uzman (psikolog, avukat, pedagog) olmadığını, tıbbi veya yasal tavsiye vermediğini her cevabında net bir şekilde belirt.
2.  Amacın teşhis koymak veya kesin çözüm sunmak DEĞİLDİR. Sadece bilgilendirme yapabilirsin.
3.  Konu ne olursa olsun, cevabının sonunda mutlaka kullanıcıyı profesyonel bir uzmana yönlendir.
4.  HAYATİ TEHLİKE KURALI: "Silahlı baskın", "intihar ediyorum", "kendime zarar vereceğim", "saldırı altındayım" gibi o an yaşanan HAYATİ TEHLİKE durumlarında, ASLA soru sorma. Tüm empatik konuşmayı bırak ve SADECE "**Şu an hayati bir tehlike durumu algılıyorum. Lütfen hemen 112 Acil Çağrı Merkezi'ni arayın.**" cevabını ver.
5.  KRİZ YÖNLENDİRME KURALI: "Şiddet görüyorum", "darp edildim", "tacize uğradım" gibi (o an yaşanmayan) ciddi kriz durumlarında, 112 yerine **ALO 183 Sosyal Destek Hattı**'nı ve hukuki destek için Baroları öner.
6.  KENDİNİ TANITMA KURALI: Eğer kullanıcı sana 'sen kimsin?', 'ne iş yaparsın?' veya 'hakkında bilgi ver' gibi kendini tanıtmanı isteyen bir soru sorarsa, ona görevini açıkla. ("Ben **Dijital Aile Danışmanı** projesi için geliştirilmiş bir yapay zekayım. Amacım aile içi psikolojik, pedagojik ve hukuki konularda ilk aşama rehberlik etmektir. Ancak **gerçek bir uzman değilim**..." gibi).
7.  Kullanıcıya karşı her zaman empatik, anlayışlı ve sakin bir dil kullan. Asla yargılama.
8.  Cevapların kısa ve özet olsun.
9.  FORMATLAMA KURALI: Cevaplarında önemli yerleri vurgulamak için Markdown formatında `**kalın yazı**` kullan ve yeni satırlar için (`\n`) kullan.
"""

# 4. Modeli ve Flask sunucusunu başlat
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=PROJE_TALIMATI
    )
except Exception as e:
    # Model adı yanlışsa veya izin yoksa hata ver
    raise ValueError(f"Google Modeli başlatılamadı: {e}")


app = Flask(__name__)
CORS(app) # Geliştirme için şimdilik tüm originlere izin ver

# --- LOGLAMA SEVİYESİNİ AYARLA ---
app.logger.setLevel(logging.INFO)
# Render logları stdout'a (standart çıktı) yazdığı için ek bir handler gerekmez.
# ----------------------------------

# 5. API Rotası (Endpoint)
@app.route('/api/mesaj', methods=['POST'])
def handle_mesaj():
    kullanici_mesaji = "" # Hata durumunda loglamak için dışarıda tanımla
    try:
        data = request.get_json()
        if not data or 'mesaj' not in data:
             app.logger.warning("Geçersiz istek: JSON veya 'mesaj' alanı eksik.")
             return jsonify({"hata": "Geçersiz istek formatı."}), 400

        kullanici_mesaji = data['mesaj'].strip() # Boşlukları temizle
        if not kullanici_mesaji:
            app.logger.warning("Boş mesaj alındı.")
            return jsonify({"hata": "Mesaj boş olamaz."}), 400
        
        # --- KULLANICI SORUSUNU LOGLA ---
        app.logger.info(f"KULLANICI SORUSU: {kullanici_mesaji}")
        # --------------------------------
        
        response = model.generate_content(kullanici_mesaji)
        
        # --- BOTUN CEVABINI LOGLA ---
        # response.text yerine daha güvenli bir şekilde alalım
        try:
            bot_cevabi = response.text
        except ValueError:
            # Model bazen güvenlik nedeniyle boş cevap verebilir
            bot_cevabi = "[Model güvenlik nedeniyle cevap vermedi]"
            app.logger.warning("Model güvenlik nedeniyle boş cevap döndü.")
        except AttributeError:
             bot_cevabi = "[Cevap formatı beklenenden farklı]"
             app.logger.warning("Model cevabının formatı beklenenden farklı.")
             
        app.logger.info(f"BOT CEVABI: {bot_cevabi}")
        # ------------------------------
        
        return jsonify({"cevap": bot_cevabi})

    except Exception as e:
        # --- HATAYI DAHA DETAYLI LOGLA ---
        app.logger.error(f"HATA OLUŞTU! Gelen Mesaj: '{kullanici_mesaji}' | Hata: {str(e)}")
        # ---------------------------------
        
        # Kullanıcıya daha genel bir hata mesajı verelim
        return jsonify({"hata": "Yapay zeka sunucusunda bir sorun oluştu. Lütfen daha sonra tekrar deneyin."}), 500
       
# Gunicorn veya başka bir WSGI sunucusu kullanıldığında bu kısım çalışmaz.
# Sadece yerel test ('python api.py') için kullanılır.
if __name__ == '__main__':
    # Debug=True YEREL GELİŞTİRME içindir, Render'da Gunicorn bunu geçersiz kılar.
    app.run(debug=True, port=5000)
