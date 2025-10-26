import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

# --- AYARLAR ---
# 1. Adım: Hugging Face Token'ını buraya yapıştır
HF_TOKEN = "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"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

# 2. Adım: API istemcisini başlat
client = InferenceClient(model=MODEL_NAME, token=HF_TOKEN)

# 3. Adım: Projenin "Karakteri" (System Prompt)
PROJE_TALIMATI = """Sen 'Dijital Aile Danışmanı' adlı bir okul projesi için geliştirilmiş bir yapay zeka sohbet botusun.
Görevin, ailelerin karşılaştığı psikolojik, pedagojik veya hukuki sorunlarda 'ilk aşamada' rehberlik etmektir.

Senin 3 KESİN KURALIN var:
1. KESİNLİKLE gerçek bir uzman (psikolog, avukat, pedagog) olmadığını, tıbbi veya yasal tavsiye vermediğini her cevabında açıkça belirt.
2. Amacın teşhis koymak veya kesin çözüm sunmak DEĞİLDİR. Sadece bilgilendirir ve genel bakış açıları sunarsın.
3. Her cevabının sonunda, konuya uygun profesyonel bir uzmana (avukat, psikolog, aile danışmanı vb.) başvurmalarını TAVSİYE ET.

Empatik, anlayışlı ve sakin bir dil kullan. Cevapların kısa ve özet olsun.
"""

# 4. Adım: Flask API Sunucusu
app = Flask(__name__)
CORS(app)

# 5. Adım: "BEYİN" FONKSİYONU
def get_ai_response(user_message):
    
    messages = [
        {"role": "system", "content": PROJE_TALIMATI},
        {"role": "user", "content": user_message}
    ]
    
    try:
        # Hata veren 'text_generation' yerine 'chat_completion' kullanıyoruz
        response = client.chat_completion(
            messages=messages,
            #
            # --- HATA BURADAYDI, DÜZELTTİM ---
            max_tokens=512,  # 'max_new_tokens' yerine 'max_tokens' olmalı
            # ----------------------------------
            #
            temperature=0.7,
            top_p=0.9,
        )
        
        ai_cevabi = response.choices[0].message.content
        return ai_cevabi.strip()

    except Exception as e:
        print(f"Hata: {e}")
        if "is currently loading" in str(e):
            return "Model şu anda sunucuda yükleniyor. Lütfen 1 dakika sonra tekrar deneyin."
        return "Üzgünüm, yapay zeka modelinde bir hata oluştu."

# 6. Adım: API Rota (Endpoint)
@app.route('/api/mesaj', methods=['POST'])
def handle_mesaj():
    kullanici_mesaji = request.json['mesaj']
    if not kullanici_mesaji:
        return jsonify({"hata": "Mesaj boş olamaz."}), 400
    
    ai_cevabi = get_ai_response(kullanici_mesaji)
    
    return jsonify({"cevap": ai_cevabi})
       
if __name__ == '__main__':
    app.run(debug=True, port=5000)