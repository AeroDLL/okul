# --- api.py ---
# SON GÜNCELLEME: 29 Ekim 2025 (v1.3 - Nihai Talimatlar + Loglama Düzeltmesi)
# Özellikler: Doğal Konuşma, Acil Numaraları Direkt Aratma, Spesifik Kaynak Önerileri,
#            Konu Kısıtlama, Empatik Dinleme & Duygu Takibi, Loglama, İstemci Hata Loglama

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

# 3. Modelin Karakterini (Sistem Talimatı) - NIHAI SÜRÜM v1.3
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

1.  **DİNLE & ANLA (DUYGU TAKİBİ İLE):** Kullanıcı sorununu anlatırken sözünü kesme. Empati göster ("**Sizi anlıyorum, bu gerçekten zorlayıcı bir durum olmalı.**"). Duygularını onaylayıcı ifadeler kullan ("**Böyle hissetmeniz çok doğal.**"). Bu tür **empatik ifadeleri TEK BİR PARAGRAF halinde yaz, aralarına gereksiz yeni satır (\n) ekleme.** Gerekirse, "**Biraz daha açmak ister misiniz?**" gibi sorularla konuyu netleştirmeye çalış (ama sorguya çekme). **Uygun olduğunda (örn: birkaç cevap verdikten sonra), kullanıcıya "**Bu bilgiler işinize yaradı mı?**" veya "**Şu anda nasıl hissediyorsunuz?**" gibi kısa, empatik bir takip sorusu sorabilirsin. Ancak bunu çok sık yapma ve asla ısrarcı olma.** Konuşmanın doğal akmasına izin ver.
2.  **BİLGİLENDİR (Yüzeysel):** Konuyla ilgili (eğer varsa) genel, bilinen yaklaşımlardan veya yasal süreçlerden (ama asla tavsiye vermeden) **kısaca** bahsedebilirsin.
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
* Tekrardan kaçın (özellikle "uzman değilim" uyarısını).
"""

# 4. Modeli ve Flask sunucusunu başlat
# ÖNEMLİ: Model adının, Google Projenizde ETKİN olan ve çalışan bir model olduğundan emin olun!
# Daha önce 'gemini-1.5-pro' veya 'gemini-1.0-pro' çalışmıştı.
# 'gemini-2.5-flash' hata veriyorsa, aşağıdaki satırı çalışan modelle değiştirin.
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro", # <-- ÇALIŞAN MODELİ BURAYA YAZIN (örn: gemini-1.5-pro veya gemini-1.0-pro)
        system_instruction=PROJE_TALIMATI
    )
except Exception as e:
    raise ValueError(f"Google Modeli başlatılamadı: {e}. Model adı doğru mu ve Google projenizde etkin mi?")

app = Flask(__name__)
CORS(app)

# --- LOG FORMATINI AYARLA ---
log_format = "[DANISMAN_BOT] [%(levelname)s] %(message)s"
formatter = logging.Formatter(log_format)
app.logger.handlers[0].setFormatter(formatter)
app.logger.setLevel(logging.INFO)
# ----------------------------------

# 5. API Rotası (Endpoint) - /api/mesaj
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

        app.logger.info(f"USER >> {kullanici_mesaji}")

        response = model.generate_content(kullanici_mesaji)

        try:
            # Cevabı alırken güvenlik bloklamasını kontrol et
            if not response.parts:
                 bot_cevabi = "[Model güvenlik nedeniyle veya başka bir sebeple cevap vermedi]"
                 # Güvenlik geri bildirimini logla (daha detaylı bilgi için)
                 app.logger.warning(f"Model boş cevap döndü. Sebep: {response.prompt_feedback}")
            else:
                 bot_cevabi = response.text
        except ValueError as ve: # Özellikle güvenlik bloklaması bu hatayı verebilir
            bot_cevabi = "[İçerik güvenlik politikaları nedeniyle engellendi]"
            app.logger.warning(f"Model (ValueError) güvenlik nedeniyle cevap vermedi: {ve}")
        except AttributeError:
             bot_cevabi = "[Cevap formatı beklenenden farklı]"
             app.logger.warning("Model cevabının formatı beklenenden farklı.")
        except Exception as inner_e: # Beklenmedik diğer hatalar
             bot_cevabi = "[Modelden cevap alınırken bir hata oluştu]"
             app.logger.error(f"Model.generate_content sonrası hata: {inner_e}")


        log_bot_cevabi = bot_cevabi.replace('\n', '\n[DANISMAN_BOT] [INFO]       ')
        app.logger.info(f"BOT <<\n[DANISMAN_BOT] [INFO]       {log_bot_cevabi}")

        return jsonify({"cevap": bot_cevabi})

    except Exception as e:
        app.logger.error(f"HATA! USER: '{kullanici_mesaji}' | ERROR: {str(e)}")
        error_message = "Yapay zeka sunucusunda bir sorun oluştu. Lütfen daha sonra tekrar deneyin."
        return jsonify({"hata": error_message}), 500

# 6. API Rotası (Endpoint) - /api/log_error (İstemci Hataları İçin)
@app.route('/api/log_error', methods=['POST'])
def log_client_error():
    try:
        error_data = request.get_json()
        # --- DÜZELTME: 'error' yerine 'message' kontrolü ---
        if error_data and 'message' in error_data:
        # --------------------------------------------------
            app.logger.error(f"[CLIENT_ERROR] Tarayıcı Hatası: {error_data.get('message', 'Mesaj yok')} | Detay: {error_data.get('details', 'Detay yok')}")
            return jsonify({"status": "error logged"}), 200
        else:
            app.logger.warning("[CLIENT_ERROR] Geçersiz hata loglama isteği alındı.")
            return jsonify({"status": "invalid error data"}), 400
    except Exception as e:
        app.logger.error(f"[LOG_ENDPOINT_ERROR] Hata loglarken hata oluştu: {str(e)}")
        return jsonify({"status": "logging failed"}), 500

# Bu kısım sadece 'python api.py' ile çalıştırıldığında kullanılır.
if __name__ == '__main__':
    # Render'da Gunicorn kullanıldığı için debug=False yapmak daha doğrudur.
    # Ancak yerel test için True bırakılabilir.
    app.run(debug=True, port=5000)
