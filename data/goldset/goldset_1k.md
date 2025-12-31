# 1) Birbirini dışlayan (mutually-exclusive) sınıflar — toplam **250**
Aşağıdaki sınıflar **öncelik sırasına** göre atanır (A en güçlü koşul). Her kayıt sadece **bir** sınıfa girer.

| Kod | Tanım (güncel)                                                   | Önerilen Adet |
|-----|------------------------------------------------------------------|--------------:|
| **A** | Tam çekirdek adres (mahalle + cadde/sokak + numara)               | **80** |
| **B** | Mahalle yok, ancak yol + numara var                               | **30** |
| **C** | Cadde eksik (cadde yok, sokak/bulvar var)                         | **24** |
| **D** | Sokak eksik (sokak yok, cadde/bulvar var)                         | **22** |
| **E** | Bina/Daire numarası yok (mahalle + yol var, numara yok)           | **22** |
| **F** | Site/Bina adı ağırlıklı                                           | **24** |
| **G** | Bulvar içeren (geniş kapsam, artan kayıtlar)                      | **12** |
| **H** | Sadece mahalle + numara (cadde/sokak yok)                         | **12** |
| **I** | Yalnızca il + ilçe ağırlıklı (çok eksik)                          | **12**  |
| **J** | Diğer düzensiz/istisnai örnekler (kurum adı vb.)                  | **12**  |
| **Toplam** |                                                              | **250** |



> Not: Sınıf ataması **öncelik**le yapılır (ör. A → değilse B → değilse C …). Böylece çakışmalar engellenir.

---

# 2) Örtüşebilen özellik sayımları (aynı kayıt birden çok özelliğe girebilir)

| Özellik                                                | Hedef adet (250’de) |
|--------------------------------------------------------|--------------------:|
| **Bina numarası (BINA_NO) içeren**                     | **160** |
| **Daire numarası (DAIRE_NO) içeren**                   | **60** |
| **Posta kodu (5 hane) içeren**                         | **95** |
| **Site/Bina adı (apt./blok/site/işhanı) içeren**       | **60** |
| **Bulvar içeren**                                      | **20** |
| **Kat bilgisi (Kat 3 vb.) içeren**                     | **35** |
| **Mahalle içeren**                                     | **~178** |
| **Yol adı (cadde/sokak/bulvar) içeren**                | **~183** |
| **Hem mahalle hem yol adı içeren**                     | **A+B = 113** |

> Tutarlılık için: G sınıfındaki 22 kaydın **~8**’inde bina/daire no olsun; H sınıfındaki 15 kaydın **~4**’ünde bina_no bulunabilir. Böylece toplamlar yukarıdaki hedeflerle uyumlu kalır.

---

# 3) Benzersiz isim çeşitliliği kotaları (250’lik set içinde)
Modelin genellemesini yükseltmek için **aynı adı tekrar etmeyin**; aşağıdaki **minimum benzersiz** sayıları hedefleyin:

| Alan                              | 250’de benzersiz hedef |
|-----------------------------------|-----------------------:|
| **Mahalle adı**                   | **≥ 90** |
| **Yol adı toplamı** *(cadde+sokak+bulvar)* | **≥ 140** |
| **İl**                            | **≥ 18** |
| **İlçe**                          | **≥ 24** |
| **Posta kodu**                    | **≥ 60** |

> 1000 kayıt için yaklaşıksal ölçek: mahalle **≥ 360**; yol adı **≥ 560**; il **≥ 30–35**; ilçe **≥ 90–100**; posta kodu **≥ 240**.

---

# 4) Pratik uygulama notları
- **Örnek seçimi**: Kayıtları seçerken önce sınıf hedeflerini doldurun (A→H). Sonra **benzersiz ad** kotalarını tamamlayın.  
- **Tutarlılık**: Etiket yönergesini kısa yazın (ad mı + tür mü birlikte span? baştan karar).  
- **Doğrulama**: Her 50 etiketten sonra hızlı istatistik alın; hangi sınıf/özellik/benzersiz kota geride kalmış, tamamlayın.  
- **Ölçekleme**: 4 annotator için bu tabloyu **4×** çoğaltıp tek bir “1000 kayıt hedef tablosu” yapabilirsiniz.

# 📌 BIO Etiketleme Standardı (Adres Verisi İçin)

**BIO** formatı, her bir token’ın (kelime/parça) hangi varlığa ait olduğunu ve bu varlığın nerede başladığını/nerede devam ettiğini gösterir.

- **B-<LABEL>** → *Begin*: Varlığın ilk token’ı (başlangıcı)  
- **I-<LABEL>** → *Inside*: Varlığın devamı (başlangıçtan sonra gelen token)  
- **O** → *Outside*: Herhangi bir varlığa ait olmayan token  

---

## 1️⃣ Temel Kurallar

1. **Her varlık (entity) B- ile başlar.**  
   Örn: “Adnan Menderes Caddesi” →  
   - `B-CADDE` (Adnan)  
   - `I-CADDE` (Menderes)  
   - `I-CADDE` (Caddesi)  

2. **Aynı varlık devam ediyorsa I- ile gider.**  
   Örn: “No: 15” →  
   - `B-BINA_NO` (No)  
   - `I-BINA_NO` (15)  

3. **O ile işaretlenenler, hiçbir hedef varlığa ait değildir.**  
   - Noktalama işaretleri, bağlaçlar, serbest kelimeler vb.  

4. **Farklı varlıklar arka arkaya gelirse, her biri B- ile başlar.**  
   Örn: “Adnan Menderes Caddesi 15” →  
   - `B-CADDE` (Adnan)  
   - `I-CADDE` (Menderes)  
   - `I-CADDE` (Caddesi)  
   - `B-BINA_NO` (15)  

5. **Tek kelimelik varlıklar da B- ile başlar (I- olmaz).**  
   Örn: “Muğla” (İl) →  
   - `B-IL` (Muğla)  

---

## 2️⃣ Adres Etiket Seti

Senin tanımladığın bileşenlere göre etiket seti:

> MAHALLE, CADDE, SOKAK, BULVAR, BINA_NO, DAIRE_NO, KAT, BINA_ADI, SITE_ADI, POSTA_KODU, ILCE, IL, TARIF, O


---

## 3️⃣ Örnek Adres ve BIO Etiketleri

Adres:  

> Akarca Mah. Adnan Menderes Cad. No: 15 Muğla Fethiye


Tokenlar ve Etiketler:

| Token    | Etiket     |
|----------|------------|
| Akarca   | B-MAHALLE  |
| Mah.     | I-MAHALLE  |
| Adnan    | B-CADDE    |
| Menderes | I-CADDE    |
| Cad.     | I-CADDE    |
| No       | B-BINA_NO  |
| :        | I-BINA_NO  |
| 15       | I-BINA_NO  |
| Muğla    | B-IL       |
| Fethiye  | B-ILCE     |