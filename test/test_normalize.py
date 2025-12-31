# Each tuple: (input, expected_output)
tests_full_normalize = [
    (
        "Mahmudiye Mah. Caddebostan Cad. No:5/7 D:3 Sok. 2",
        "mahmudiye mah caddebostan cad no : 5 / 7 d : 3 sk 2",
    ),
    (
        "İNCİRLİ MH: 23. SOK-14, CADDESI_ 7 MAHALLESi 9",
        "incirli mah : 23 sk - 14 cad _ 7 mah 9",
    ),
    (
        "Atatürk MAHALLESİ: 10 sk. / cd. 5 sokagi-3",
        "atatürk mah : 10 sk / cad 5 sk - 3",
    ),
    (
        "Dr. Sadık AHmet Caddesı- No:12 Sokullu Sk:3 Mah.: 4",
        "dr sadık ahmet cad - no : 12 sokullu sk : 3 mah : 4",
    ),
    (
        "MAHL 7. CD / SOKAĞI 22, Mahalle 5",
        "mah 7 cad / sk 22 mah 5",
    ),
    (
        "İstiklal mahallesi. Cumhuriyet CADDE:45 sk-9 mh 1",
        "istiklal mah cumhuriyet cad : 45 sk - 9 mah 1",
    ),
    (
        "Cevizlik Mh. 15_Sok./ Caddesi: 120 Mahallesi:Atatürk",
        "cevizlik mah 15 _ sk / cad : 120 mah : atatürk",
    ),
    (
        "SOK:5; MAH-3. Cd 4 (Caddebostan değil) Mahallesi 7",
        "sk : 5 ; mah - 3 cad 4 ( caddebostan değil ) mah 7",
    ),
    (
        "Mahallesi:Atatürk Cd.No.12 Sokagi-3 MHL 2",
        "mah : atatürk cad no 12 sk - 3 mah 2",
    ),
    (
        "mhl. 2. Sokrates Sok. CADDESI/7 IŞIK MAHAL 4-6",
        "mah 2 sokrates sk cad / 7 ışık mah 4 - 6",
    ),
    (
        "MAH: Aydıntepe, Caddesi - 34 / SOK 9",
        "mah : aydıntepe cad - 34 / sk 9",
    ),
    (
        "Mahl 3 sk: 18; CADDESI: 200, mahallesi 1",
        "mah 3 sk : 18 ; cad : 200 mah 1",
    ),
    (
        "Mh 10 Sok-2 Cd:7 Mahallesi: Gazi",
        "mah 10 sk - 2 cad : 7 mah : gazi",
    ),
    (
        "Mahallesi: Güzelyurt / Caddesi_5 / Sokak-3",
        "mah : güzelyurt / cad _ 5 / sk - 3",
    ),
    (
        "MHL: 1, SOKAĞA 2, CD. 3 mahal 4",
        "mah : 1 sk 2 cad 3 mah 4",
    ),
    (
        "mahalle: Cumhuriyet; cadde- 10; sokak/ 2",
        "mah : cumhuriyet ; cad - 10 ; sk / 2",
    ),
    (
        "MAHALLesI 12 SOK: 3 CD: 5",
        "mah 12 sk : 3 cad : 5",
    ),
    (
        "mhl- 8 / sokak: 4 / caddesi 12 / mahal 1 \n Yeniköy apartmanı",
        "mah - 8 / sk : 4 / cad 12 / mah 1 yeniköy apartmanı",
    ),
    (
        "mh. 1 sk. 2 cd. 3 Mahallesi: 'Yeni'",
        "mah 1 sk 2 cad 3 mah : ' yeni '",
    ),
    (
        "Mahl: 9, Cad-7; Sok./11 Mahalle 3",
        "mah : 9 cad - 7 ; sk / 11 mah 3",
    ),
]

# Each tuple: (input, expected_output) for PUNCTUATION-ONLY pipeline
tests_punct_only = [
    (
        "Mahmudiye Mah. Caddebostan Cad. No:5/7 D:3 Sok. 2",
        "Mahmudiye Mah Caddebostan Cad No : 5 / 7 D : 3 Sok 2",
    ),
    (
        "İNCİRLİ MH: 23. SOK-14, CADDESI_ 7 MAHALLESi 9",
        "İNCİRLİ MH : 23 SOK - 14 CADDESI _ 7 MAHALLESi 9",
    ),
    (
        "Atatürk MAHALLESİ: 10 sk. / cd. 5 sokagi-3",
        "Atatürk MAHALLESİ : 10 sk / cd 5 sokagi - 3",
    ),
    (
        "Dr. Sadık AHmet Caddesı- No:12 Sokullu Sk:3 Mah.: 4",
        "Dr Sadık AHmet Caddesı - No : 12 Sokullu Sk : 3 Mah : 4",
    ),
    (
        "MAHL 7. CD / SOKAĞI 22, Mahalle 5",
        "MAHL 7 CD / SOKAĞI 22 Mahalle 5",
    ),
    (
        "İstiklal mahallesi. Cumhuriyet CADDE:45 sk-9 mh 1",
        "İstiklal mahallesi Cumhuriyet CADDE : 45 sk - 9 mh 1",
    ),
    (
        "Cevizlik Mh. 15_Sok./ Caddesi: 120 Mahallesi:Atatürk",
        "Cevizlik Mh 15 _ Sok / Caddesi : 120 Mahallesi : Atatürk",
    ),
    (
        "SOK:5; MAH-3. Cd 4 (Caddebostan değil) Mahallesi 7",
        "SOK : 5 ; MAH - 3 Cd 4 ( Caddebostan değil ) Mahallesi 7",
    ),
    (
        "Mahallesi:Atatürk Cd.No.12 Sokagi-3 MHL 2",
        "Mahallesi : Atatürk Cd No 12 Sokagi - 3 MHL 2",
    ),
    (
        "mhl. 2. Sokrates Sok. CADDESI/7 IŞIK MAHAL 4-6",
        "mhl 2 Sokrates Sok CADDESI / 7 IŞIK MAHAL 4 - 6",
    ),
    (
        "MAH: Aydıntepe, Caddesi - 34 / SOK 9",
        "MAH : Aydıntepe Caddesi - 34 / SOK 9",
    ),
    (
        "Mahl 3 sk: 18; CADDESI: 200, mahallesi 1",
        "Mahl 3 sk : 18 ; CADDESI : 200 mahallesi 1",
    ),
    (
        "Mh 10 Sok-2 Cd:7 Mahallesi: Gazi",
        "Mh 10 Sok - 2 Cd : 7 Mahallesi : Gazi",
    ),
    (
        "Mahallesi: Güzelyurt / Caddesi_5 / Sokak-3",
        "Mahallesi : Güzelyurt / Caddesi _ 5 / Sokak - 3",
    ),
    (
        "MHL: 1, SOKAĞA 2, CD. 3 mahal 4",
        "MHL : 1 SOKAĞA 2 CD 3 mahal 4",
    ),
    (
        "mahalle: Cumhuriyet; cadde- 10; sokak/ 2",
        "mahalle : Cumhuriyet ; cadde - 10 ; sokak / 2",
    ),
    (
        "MAHALLesI 12 SOK: 3 CD: 5",
        "MAHALLesI 12 SOK : 3 CD : 5",
    ),
    (
        "mhl- 8 / sokak: 4 / caddesi 12 / mahal 1",
        "mhl - 8 / sokak : 4 / caddesi 12 / mahal 1",
    ),
    (
        "mh. 1 sk. 2 cd. 3 Mahallesi: 'Yeni'",
        "mh 1 sk 2 cd 3 Mahallesi : ' Yeni '",
    ),
    (
        "Mahl: 9, Cad-7; Sok./11 Mahalle 3",
        "Mahl : 9 Cad - 7 ; Sok / 11 Mahalle 3",
    ),
]


# tests/test_normalizer.py
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Optional quick checker:
from src.address_matching import AddressNormalizer
n = AddressNormalizer()

def test_normalize(n: AddressNormalizer):
    print("--- TEST NORMALIZE FULL ---")
    for i, (inp, exp) in enumerate(tests_full_normalize, 1):
        out = n.normalize(inp, True)
        print(f"{i:02d}. {'OK' if out == exp else 'FAIL'}")
        if out != exp:
            print("   inp:", inp)
            print("   out:", out)
            print("   exp:", exp)
    print()        

def test_normalize_punctuation_only(n: AddressNormalizer):
    print("--- TEST NORMALIZE PUNCTUATION ONLY ---")
    for i, (inp, exp) in enumerate(tests_punct_only, 1):
        out = n.normalize_punctuation_only(inp)
        print(f"{i:02d}. {'OK' if out == exp else 'FAIL'}")
        if out != exp:
            print("   inp:", inp)
            print("   out:", out)
            print("   exp:", exp)
    print()

test_normalize(n)
test_normalize_punctuation_only(n)