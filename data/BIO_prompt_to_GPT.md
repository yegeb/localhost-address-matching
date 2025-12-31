<file name=0 path=BIO_prompt_to_GPT.md># 📍 2️⃣ Adres Etiket Seti

Aşağıdaki etiketler adres bileşenlerini sınıflandırmak için kullanılacaktır:

## 🏘 Mahalle / Cadde / Sokak
- **MAHALLE** → Mahalle adı
- **CADDE** → Cadde adı
- **SOKAK** → Sokak adı
- **BULVAR** → Bulvar adı

## 🏢 Bina / Daire Bilgileri
- **BINA_NO** → Bina numarası
- **KAT** → Kat numarası
- **DAIRE_NO** → Daire numarası
- **BINA_ADI** → Bina adı
- **SITE_ADI** → Site adı

## 📮 Konum / Bölge
- **POSTA_KODU** → Posta kodu
- **ILCE** → İlçe adı
- **IL** → İl adı
- **TARIF** → Adres ile ilgili sözel tarif

## ❓ Belirlenememiş
- **O** → Belirlenememiş / diğer kelimeler için kullanılan etiket


## 3️⃣ Örnek Adres ve BIO Etiketleri



```
Turunç mah. Cumhuriyet cad. No 30/C , Berber Salonu 1.2.3 TURUNÇ MARMARİS Muğla,194426,D
Turunç B-MAHALLE
mah I-MAHALLE
Cumhuriyet B-CADDE
cad I-CADDE
No B-BINA_NO
30 I-BINA_NO
/ I-BINA_NO
C I-BINA_NO
Berber B-TARIF
Salonu I-TARIF
1 O
2 O
3 O
TURUNÇ B-MAHALLE
MARMARİS B-ILCE
Muğla B-IL

ESKİÇEŞME MAH ESKİÇEŞME MAH ERGÜN SOYKAN CAD NO:9/2 MUĞLA / BODRUM EV,511804,D
ESKİÇEŞME B-MAHALLE
MAH I-MAHALLE
ESKİÇEŞME B-MAHALLE
MAH I-MAHALLE
ERGÜN B-CADDE
SOYKAN I-CADDE
CAD I-CADDE
NO B-BINA_NO
: I-BINA_NO
9 I-BINA_NO
/ B-DAIRE_NO
2 I-DAIRE_NO
MUĞLA B-IL
/ O
BODRUM B-ILCE
EV O

BAĞBAŞI / PAMUKKALE / DenizliBağbaşı mah vatan cad 1095 şok no 4 pamukkale DenizliSinan Özkan,411713,D
BAĞBAŞI B-MAHALLE
/ O
PAMUKKALE B-ILCE
/ O
DenizliBağbaşı B-MAHALLE
mah I-MAHALLE
vatan B-CADDE
cad I-CADDE
1095 B-SOKAK
şok I-SOKAK
no B-BINA_NO
4 I-BINA_NO
pamukkale B-ILCE
Denizli B-IL
Sinan B-TARIF
Özkan I-TARIF

ADNAN SÜVARI MAH POLAT CADDESI NO:206/a ISYERI KONYALI,389782,D
ADNAN B-MAHALLE
SÜVARI I-MAHALLE
MAH I-MAHALLE
POLAT B-CADDE
CADDESI I-CADDE
NO B-BINA_NO
: I-BINA_NO
206 I-BINA_NO
/ I-BINA_NO
a I-BINA_NO
ISYERI B-TARIF
KONYALI I-TARIF

ATATÜRK MAH Barbaros caddesi numara 72 daire 3 BORNOVA,457467,D
ATATÜRK B-MAHALLE
MAH I-MAHALLE
Barbaros B-CADDE
caddesi I-CADDE
numara B-BINA_NO
72 I-BINA_NO
daire B-DAIRE_NO
3 I-DAIRE_NO
BORNOVA B-ILCE

Ahmet çavuş mahallesi hayıtlı mahallesi barış caddesi no 33c No33c,116408,D
Ahmet B-MAHALLE
çavuş I-MAHALLE
mahallesi I-MAHALLE
hayıtlı B-MAHALLE
mahallesi I-MAHALLE
barış B-CADDE
caddesi I-CADDE
no B-BINA_NO
33c I-BINA_NO
No B-BINA_NO
33c I-BINA_NO

orta mahalle Selanik CAD tenekeci Tahsin apt no 7 Kat 3,5735,D
orta B-MAHALLE
mahalle I-MAHALLE
Selanik B-CADDE
CAD I-CADDE
tenekeci B-BINA_ADI
Tahsin I-BINA_ADI
apt I-BINA_ADI
no B-BINA_NO
7 I-BINA_NO
Kat B-KAT
3 I-KAT

Dumlupınar Mah. Kıbrıs Cad. Buca İnci Özer Tırnaklı Fen Lisesi Blok No 1/C,165418,D
Dumlupınar B-MAHALLE
Mah. I-MAHALLE
Kıbrıs B-CADDE
Cad. I-CADDE
Buca B-ILCE
İnci B-BINA_ADI
Özer I-BINA_ADI
Tırnaklı I-BINA_ADI
Fen I-BINA_ADI
Lisesi I-BINA_ADI
Blok I-BINA_ADI
No B-BINA_NO
1 I-BINA_NO
/ I-BINA_NO
C I-BINA_NO

MENDERES MAH.	ERDEM Caddesi NO 125 D.6 BUCA İzmir,433410,D
MENDERES B-MAHALLE
MAH. I-MAHALLE
ERDEM B-CADDE
Caddesi I-CADDE
NO B-BINA_NO
125 I-BINA_NO
D B-DAIRE_NO
6 I-DAIRE_NO
BUCA B-ILCE
İzmir B-IL

Dalyan Mah. Gulpinar Cad. Jazz Bar No:28 Ortaca Mugla Ortaca Ortaca,241972,D
Dalyan B-MAHALLE
Mah. I-MAHALLE
Gulpinar B-CADDE
Cad. I-CADDE
Jazz B-TARIF
Bar I-TARIF
No B-BINA_NO
: I-BINA_NO
28 I-BINA_NO
Ortaca B-ILCE
Mugla B-IL
Ortaca B-ILCE
Ortaca I-ILCE

ÇAMLARALTI MAH. HÜSEYİN YILMAZ CAD. NO:55 / 55D PAMUKKALE/DENİZLİ.,692366,D
ÇAMLARALTI B-MAHALLE
MAH. I-MAHALLE
HÜSEYİN B-CADDE
YILMAZ I-CADDE
CAD. I-CADDE
NO B-BINA_NO
: I-BINA_NO
55 I-BINA_NO
/ I-BINA_NO
55D I-BINA_NO
PAMUKKALE B-ILCE
/ O
DENİZLİ B-IL

Denizli Buldan yenicekent mah İnönü cad No 4,440344,D
Denizli B-IL
Buldan B-ILCE
yenicekent B-MAHALLE
mah I-MAHALLE
İnönü B-CADDE
cad I-CADDE
No B-BINA_NO
4 I-BINA_NO

30 Ağustos Mh. 2. caddesi yenice yasam 2 sitesi no18 daire18 MENEMEN İZMİR,573015,D
30 B-MAHALLE
Ağustos I-MAHALLE
Mh. I-MAHALLE
2 B-CADDE
caddesi I-CADDE
yenice B-SITE_ADI
yasam I-SITE_ADI
2 I-SITE_ADI
sitesi I-SITE_ADI
no B-BINA_NO
18 I-BINA_NO
daire B-DAIRE_NO
18 I-DAIRE_NO
MENEMEN B-ILCE
İZMİR B-IL

ÖLÜ DENİZ CADDESİ TAŞ YAKA MAH. ERASTA AVM.KAT:1 NO:36 İPEKYOL MAĞAZASI ,793111,D
ÖLÜ B-CADDE
DENİZ I-CADDE
CADDESİ I-CADDE
TAŞ B-MAHALLE
YAKA I-MAHALLE
MAH. I-MAHALLE
ERASTA B-TARIF
AVM I-TARIF
KAT B-KAT
: I-KAT
1 I-KAT
NO B-BINA_NO
: I-BINA_NO
36 I-BINA_NO
İPEKYOL B-TARIF
MAĞAZASI I-TARIF

Fatih caddesi  Çeltikçi mahallesi no:46/A,227782,D
Fatih B-CADDE
caddesi I-CADDE
Çeltikçi B-MAHALLE
mahallesi I-MAHALLE
no B-BINA_NO
: I-BINA_NO
46 I-BINA_NO
/ I-BINA_NO
A I-BINA_NO

Turabiye mahallesi turabiye caddesi no 86 kat.3 daire 16 ev,260966,D
Turabiye B-MAHALLE
mahallesi I-MAHALLE
turabiye B-CADDE
caddesi I-CADDE
no B-BINA_NO
86 I-BINA_NO
kat B-KAT
3 I-KAT
daire B-DAIRE_NO
16 I-DAIRE_NO
ev O

FEVZİ ÇAKMAK MAHALLESİ YILDIRIM BEYAZIT  CADDESİ NO:7/2 YENİFOÇA,365231,D
FEVZİ B-MAHALLE
ÇAKMAK I-MAHALLE
MAHALLESİ I-MAHALLE
YILDIRIM B-CADDE
BEYAZIT I-CADDE
CADDESİ I-CADDE
NO B-BINA_NO
: I-BINA_NO
7 I-BINA_NO
/ B-DAIRE_NO
2 I-DAIRE_NO
YENİFOÇA B-ILCE

TORBA MAH KAYNAR CADDESİ NO:11 DBTH IŞIL CLUP BODRUM / MUĞLA,564553,D
TORBA B-MAHALLE
MAH I-MAHALLE
KAYNAR B-CADDE
CADDESİ I-CADDE
NO B-BINA_NO
: I-BINA_NO
11 I-BINA_NO
DBTH B-BINA_ADI
IŞIL I-BINA_ADI
CLUP I-BINA_ADI
BODRUM B-ILCE
/ O
MUĞLA B-IL

Turgutreis mahallesi Bahçelievler Caddesi şehit Kenan Aybey cad. no 6  Bina: 6 Kat: 1 Daire: 1 Bodrum - MUĞLA,454455,D
Turgutreis B-MAHALLE
mahallesi I-MAHALLE
Bahçelievler B-CADDE
Caddesi I-CADDE
şehit B-CADDE
Kenan I-CADDE
Aybey I-CADDE
cad. I-CADDE
no B-BINA_NO
6 I-BINA_NO
Bina B-BINA_NO
: I-BINA_NO
6 I-BINA_NO
Kat B-KAT
: I-KAT
1 I-KAT
Daire B-DAIRE_NO
: I-DAIRE_NO
1 I-DAIRE_NO
Bodrum B-ILCE
- O
MUĞLA B-IL

Müskebi Mah. Atatürk Cad. No:16/2-2,749469,D
Müskebi B-MAHALLE
Mah. I-MAHALLE
Atatürk B-CADDE
Cad. I-CADDE
No B-BINA_NO
: I-BINA_NO
16 I-BINA_NO
/ I-BINA_NO
2-2 I-BINA_NO

Kasımpaşa mahallesi Şehit Fatih Yalçın caddesi Ak Apartmanı no 10-12 kat 1 daire 2 Menderes ,148555,D
Kasımpaşa B-MAHALLE
mahallesi I-MAHALLE
Şehit B-CADDE
Fatih I-CADDE
Yalçın I-CADDE
caddesi I-CADDE
Ak B-BINA_ADI
Apartmanı I-BINA_ADI
no B-BINA_NO
10-12 I-BINA_NO
kat B-KAT
1 I-KAT
daire B-DAIRE_NO
2 I-DAIRE_NO
Menderes B-ILCE

Turan Mahallesi Buldan Caddesi no:27/A Atcalı Yapı Market TURAN SARAYKÖY Denizli,639371,D
Turan B-MAHALLE
Mahallesi I-MAHALLE
Buldan B-CADDE
Caddesi I-CADDE
no B-BINA_NO
: I-BINA_NO
27 I-BINA_NO
/ I-BINA_NO
A I-BINA_NO
Atcalı B-BINA_ADI
Yapı I-BINA_ADI
Market I-BINA_ADI
TURAN B-MAHALLE
SARAYKÖY B-ILCE
Denizli B-IL


```