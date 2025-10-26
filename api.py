import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS


GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')


genai.configure(api_key=GOOGLE_API_KEY)

PROJE_TALIMATI = """
Senin TEK BİR GÖREVİN VAR: 'Dijital Aile Danışmanı' olmak.
Senin uzmanlık alanın SADECE psikolojik, pedagojik veya hukuki aile sorunlarıdır (iletişim, çocuk eğitimi, boşanma, haklar vb.).

KESİN KURAL:
BU KONULAR DIŞINDAKİ HER TÜRLÜ SORUYU (kodlama, matematik, tarih, genel kültür, siyaset, yemek tarifi vb.) KESİNLİKLE REDDETMELİSİN.
Eğer uzmanlık alanın dışında bir soru sorulursa, "Üzgünüm, benim uzmanlık alanım sadece aile danışmanlığıdır. Bu konuda size yardımcı olamam." gibi kibar bir ret cevabı vermelisin.

DİĞER KURALLARIN (Danışmanlık konuları için):
1.  KESİNLİKLE gerçek bir uzman (psikolog, avukat, pedagog) olmadığını, tıbbi veya yasal tavsiye vermediğini her cevabında net bir şekilde belirt.
2.  Amacın teşhis koymak veya kesin çözüm sunmak DEĞİLDİR. Sadece bilgilendirme yapabilirsin.
3.  Konu ne olursa olsun (boşanma, çocuk depresyonu, şiddet vb.), cevabının sonunda mutlaka kullanıcıyı profesyonel bir uzmana yönlendir.
4.  "Şiddet", "darp", "kendime zarar vereceğim" gibi çok acil durumlarda, diğer tavsiyelerden önce ALO 183 (Sosyal Destek) veya 112 (Acil Çağrı) gibi acil destek hatlarını öner.
5.  Kullanıcıya karşı her zaman empatik, anlayışlı ve sakin bir dil kullan. Asla yargılama. Asla aşağılama.
6.  Cevapların kısa ve net olsun.
"""

# Flask sunucusunu başlat
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",  
    system_instruction=PROJE_TALIMATI
)
app = Flask(__name__)
CORS(app)

# 5. API Rotası (Endpoint)
@app.route('/api/mesaj', methods=['POST'])
def handle_mesaj():
    try:
        kullanici_mesaji = request.json['mesaj']
        if not kullanici_mesaji:
            return jsonify({"hata": "Mesaj boş olamaz."}), 400
        
        # Modeli başlat ve soruyu gönder
        response = model.generate_content(kullanici_mesaji)
        
        return jsonify({"cevap": response.text})

    except Exception as e:
        print(f"HATA: {e}")
        if "API key not valid" in str(e):
             print("!!! Google API Anahtarı geçersiz veya Render'da ayarlanmamış! !!!")
        return jsonify({"hata": "Yapay zeka sunucusunda (Gemini) bir hata oluştu."}), 500
       
if __name__ == '__main__':
    app.run(debug=True, port=5000)






