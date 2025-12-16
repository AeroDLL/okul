🤖 Dijital Aile Danışmanı (v1.6)

"Aile içi iletişim, pedagojik destek ve hukuki rehberlik için yapay zeka destekli ilk adım asistanınız."

Bu proje, ailelerin ve bireylerin karşılaştığı psikolojik, pedagojik ve temel hukuki sorunlarda (boşanma, çocuk gelişimi, iletişim problemleri vb.) ilk aşama rehberlik sağlamak, onları dinlemek ve doğru uzmanlara yönlendirmek amacıyla geliştirilmiş akıllı bir sohbet botudur.

🌟 Öne Çıkan Özellikler

Bu proje, standart bir sohbet botundan fazlasını sunmak için geliştirilmiştir:

🧠 Akıllı ve Empatik Yapay Zeka

Hafızalı Sohbet: Bot, konuşma geçmişini hatırlar ve bağlama uygun cevaplar verir.

Empatik Yaklaşım: Kullanıcıyı yargılamadan dinler, duygusal destek dili kullanır.

Konu Filtreleme: Sadece aile danışmanlığı konularında hizmet verir, konu dışı soruları (kodlama, siyaset vb.) kibarca reddeder.

🛡️ Güvenlik ve Kriz Yönetimi

Acil Durum Protokolü: "Şiddet", "intihar", "saldırı" gibi hayati tehlike içeren durumları tespit eder.

Otomatik Yönlendirme: Kriz anında empatiyi kesip doğrudan 112 Acil, 155 Polis veya ALO 183 Sosyal Destek hatlarına yönlendirir.

Spesifik Uzman Önerisi: Soruna göre Avukat, Pedagog, Psikolog veya Aile Danışmanı gibi doğru uzmanlık alanını belirtir.

🎨 Modern Kullanıcı Arayüzü (v1.6)

Karanlık Mod (Dark Mode): Göz yormayan gece modu desteği (🌙/☀️).

Gerçekçi Etkileşim: "Yazıyor..." animasyonu ve mesaj zaman damgaları.

Kullanıcı Dostu Araçlar:

📋 Mesaj Kopyalama

🗑️ Sohbeti Temizleme

🖱️ Otomatik Aşağı Kaydırma Butonu

🔒 Mesaj gönderilirken kilitlenen giriş alanı

Akıllı Popup: Sürüm notlarını ve özellikleri gösteren bilgilendirme penceresi.

🛠️ Teknolojiler

Backend: Python (Flask)

AI Model: Google Gemini 1.5 Pro (Generative AI)

Frontend: HTML5, CSS3, Vanilla JavaScript

Sunucu: Gunicorn (Production Ready)

🚀 Kurulum (Kendi Bilgisayarınızda Çalıştırma)

Projeyi yerel ortamınızda geliştirmek veya çalıştırmak için şu adımları izleyin:

1. Projeyi Klonlayın

git clone [https://github.com/AeroDLL/okul.git](https://github.com/AeroDLL/okul.git)
cd okul


2. Gerekli Kütüphaneleri Yükleyin

Python'un yüklü olduğundan emin olun ve bağımlılıkları yükleyin:

pip install -r requirements.txt


3. API Anahtarını Ayarlayın

Proje Google Gemini API kullanır. Kendi anahtarınızı almanız gerekir (Ücretsizdir).

Google AI Studio adresinden bir API anahtarı alın.

Proje klasöründe .env adında yeni bir dosya oluşturun.

İçine şu satırı ekleyin ve anahtarınızı yapıştırın:

GOOGLE_API_KEY=BURAYA_API_ANAHTARINIZI_YAPISTIRIN


4. Uygulamayı Başlatın

python api.py


Terminalde Running on http://127.0.0.1:5000 yazısını gördüğünüzde, tarayıcınızdan bu adrese giderek botu kullanabilirsiniz.

⚠️ Yasal Uyarı

Bu proje bir okul projesi kapsamında geliştirilmiştir. Dijital Aile Danışmanı:

Gerçek bir psikolog, doktor veya avukat değildir.

Tıbbi teşhis koyamaz veya yasal tavsiye veremez.

Verdiği bilgiler sadece rehberlik ve bilgilendirme amaçlıdır.

Ciddi psikolojik sorunlar, şiddet veya hukuki anlaşmazlıklarda lütfen mutlaka gerçek bir uzmana veya resmi kurumlara başvurunuz.

Yapımcı: Emirhan Bıçakcı ✨
