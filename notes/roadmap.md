# Kestrel Air Simulation Lab: roadmap ve beyin fırtınası

> Kaynaklar: `yeni-case-5-sirket/02-challenge.md` (brief), `13-kestrel-air.md` (dossier), `check.py` (validator).
> Etiketler: **[BRIEF]** = brief/dossier'de yazıyor · **[TÜRETİLMİŞ]** = dossier rakamlarından hesap · **[ANALİZ]** = bizim önerimiz.
> Ölçülmemiş her sayı `<x>` şeklinde yer tutucu. Slayta gerçek run'dan gelmeyen bir sayı yazmayalım.

---

## 0. Asla kaçırılmayacak saatler [BRIEF]

| Saat | Ne oluyor | Bizim için anlamı |
|---|---|---|
| **13:00** | Hafta 1 başlıyor, her 30 dk = 1 hafta | Dashboard nöbeti başlar; iskelet o saate kadar çalışıyor olmalı |
| **16:00** | Hafta 7 başlıyor | **Hafta 7'ye karar kilitlemenin son anı** (grevden önceki hafta) |
| **16:30** | Hafta 8 başlıyor (grev haftası: 22–23 Aralık) | Hafta 8'e karar kilitlemenin son anı |
| **17:00** | Hafta 9 başlıyor | Hafta 9'a karar kilitlemenin son anı |
| **17:30** | Hafta 10 başlıyor; bundan sonra **karar kilitlenemez** | Son duyuru gelebilir: 5 final run **17:30–17:55 arasında** koşmalı |
| **18:00** | ZIP teslimi | `python3 check.py` yeşil olmadan yükleme yok |
| **18:30** | Board sunumu | 5 dk sunum + 3 dk soru; board bir persona seçip **canlı soru soruyor** |

Kurallar: Hafta N'nin başında duyurulan bir krize verilebilecek en erken yanıt hafta N+1'de. Bir kararın haftası başlayana kadar karar değiştirilebiliyor [BRIEF].
→ **Bunun sonucu [ANALİZ]:** Final run'ların tamamı **< 10 dk** sürmeli. Mimariyi hıza göre kur: tek komut, 5 run paralel.

---

## 1. Hedefler, sayılarla [TÜRETİLMİŞ, haftalık hacim sabit varsayıldı]

| Board hedefi | Kaba ölçek | Çıkarım [ANALİZ] |
|---|---|---|
| G1: Grev günleri hariç ≥ %98 uçuş | 10 haftada iptal payı yalnızca %2 | Grev 24 Aralık'a **uzarsa** o gün sayılır → yedek yer hizmetleri sigorta işlevi görüyor |
| G2: Aksayan günlerde ≥ %90 yolcu 24 saatte rebook veya iade | Grev günlerinde MCO/PHL'ye dokunan ~**36.000** yolcu; W8'de kendi boş koltuğumuz ~**6.300** (%97 dolu) | **Kendi ağımız tek başına yetmez** → partner havayolu anlaşması + grevden önce gönüllü kaydırma (ücretsiz değişiklik) kritik |
| G3: Şikâyet ve NPS geçen kıştan kötü değil | Baz: ~2.500 şikâyet/ay, ~150 DOT, NPS +12 [BRIEF] | Mesajın tonu ve dürüstlüğü burada belirleyici ("hatırladıkları gecikme değil, onlara nasıl davrandığımız") |
| G4: W5–W10 gelir ≥ planın %96'sı | Ortalama bilet $142,5 → ~$29,9M/hafta → 6 haftada ~$180M; %4 tolerans ≈ **$7,2M** | İadeler G2'yi yükseltirken G4'ü düşürüyor → **G2 ile G4 arasındaki gerilim** sunumun ana hikâyesi olabilir |
| G5: Bütçe ≤ $3M | Uçuş birleştirme +$0,25M bütçe kazandırıyor ama G1'e zarar veriyor | |

Kırmızı çizgiler [BRIEF]: güvenlik, yanıltıcı mesaj yok (mesajda "aksama olmayacak" diyemeyiz), zorunlu iadeler her zaman ödenir, bir üsteki tüm uçuşlar iptal edilemez.

---

## 2. Mimari [ANALİZ]

```
config/
  crises.json        bilinen kriz + dashboard duyuruları (metin aynen) + "nasıl okuduk" + etki parametreleri
  decisions/plan.json, nodecision.json      run.json'a aynen kopyalanır
code/
  llm.py       google-genai wrapper: seed, temperature>0, retry, eşzamanlılık limiti; HER çağrıyı calls.jsonl'a yazar
  personas.py  personas.jsonl'ı bir kez üretir ve dondurur (5 run'da aynı dosya olmalı)
  world.py     operasyon modeli: üs × gün iptal/gecikme, rebook kapasitesi, çağrı merkezi bekleme süresi
  sim.py       run(type, seed) → runs/<ad>/{run.json, personas.jsonl, calls.jsonl, weekly.jsonl, metrics.json}
  probe.py     8 check-in sorusu, hafta 0 ve 11 (yalnızca plan_1 ve nodecision_1)
  metrics.py   weekly → goal_1..goal_4 + units
  ask.py       canlı sunum için: persona + 10 haftalık hafızası → board'un sorusuna cevap
run_all.sh     5 run paralel → check.py → zip
```

**Haftalık döngü (her hafta, personalar paralel):**
1. **Dünya adımı (kod + isteğe bağlı GM çağrısı, `persona: null`):** O haftanın krizleri ve güncellemeleri ile yürürlükteki kararlar uygulanır. Sonuç: hangi üste, hangi gün, ne kadar iptal ve gecikme; rebook kapasitesi; bekleme süresi.
2. **Maruziyet:** Personanın bu hafta uçuşu var mı, hangi üsten, etkileniyor mu? Ne görüyor? Görebilecekleri:
   - şirket mesajı: yalnızca hedefteyse ve hafta ≥ karar haftasıysa, **kelimesi kelimesine**;
   - haberler;
   - arkadaşlarının geçen haftaki paylaşımları;
   - destek hattı deneyimi.
3. **Persona çağrısı** → JSON: `thoughts, actions[], status, would_book_again, nps_0_10, complaint(none/app/DOT), post, memory_note`. Cevap son satırda `Status: <dossier'deki kelimeler>` ile bitiyor.
4. Hafıza ve sosyal akış güncellenir, sonra bir sonraki haftaya geçilir.

**Validator'ın gerçekten kontrol ettikleri (`check.py`):**
- **Persona sayısı:** ≥ 24 persona, ≥ 3 grup, her grupta ≥ 4. `group` dossier'deki grup adlarından biri olmalı.
- **Haftalık durumlar:** Her persona × hafta (1–10) için bir `status` gerekiyor. Durum şu dördünden biri: `flies as planned / rebooked / moved to another airline / canceled the trip`. Bu durum, `call` ile işaret edilen **o personanın o haftaki çağrısının cevabında aynen geçmeli**. İkinci satır (`yes / maybe / no`) kendi alanımızda duruyor, ör. `"book_again": "maybe"`.
- **Karar mesajı:** Karar haftasından itibaren persona prompt'unda aynen geçmeli. **Daha önceki haftaların prompt'larında görünmemeli.** Nodecision run'larında hiç görünmemeli.
- **Seed farkı:** plan_1 ile plan_2'nin cevapları farklı olmalı (seed + temperature>0). plan_1 ile plan_nosurprises'in prompt'ları farklı olmalı.
- **metrics.json:** `goal_1..goal_4` sayı olarak + `units`.
- **Probe:** 24+ persona × 2 zaman (başlangıç/bitiş) × 8 soru, çağrılar hafta 0 ve hafta 11'de.

**Hız bütçesi [ANALİZ]:** Bir run'da kabaca persona sayısı × 10 çağrı (+ GM + probe). `gemini-3.5-flash-lite` çağrı başına yaklaşık 1 sn [BRIEF]. Hafta içi paralel, haftalar sıralı → run başına birkaç dakikanın altında beklenir; 5 run paralel. **Rate limit bilinmiyor:** organizatörlere sorulacak.

---

## 3. Zaman planı (gerçek saat)

| Saat | Takvim | İş | Bitti sayılır |
|---|---|---|---|
| 11:20–11:50 | — | Beyin fırtınası (§5), roller, mimari kilidi. `TALP_KEY` ile SDK'den tek test çağrısı | Kararlar `notes/decisions.md`'de |
| 11:50–13:00 | — | **Walking skeleton:** 24 basit persona, 10 haftalık döngü, doğru şema, tiny run | **`check.py` yeşil** |
| 13:00 → | W1… | **Dashboard nöbeti:** her :00 ve :30'da duyuru metni aynen `crises.json`'a, okumamız yanına | Hiçbir duyuru kaçmaz |
| 13:00–14:30 | W1–W3 | Gerçek persona havuzu (32–40), dünya modeli (§1'deki kapasite matematiği), metrikler, probe | Nodecision run anlamlı sonuç veriyor |
| 14:30–15:40 | W4–W6 | **Deneyler:** nodecision vs paket A/B/C (§4), her biri 2 seed + sanity testleri | Karşılaştırma tablosu |
| **≤ 15:50** | W6 | **Karar 1 kilit** (W7 hedefleniyorsa; son an 16:00) | Dashboard'da kilitli |
| 16:00–17:00 | W7–W8 | Sürprizleri oku, karar 2 deneyleri, memo/teamdoc taslağı (sayılar yer tutucu) | |
| **≤ 16:55 / ≤ 17:25** | | **Karar 2 kilit** (W9 veya W10) | |
| 17:30–17:50 | W10 | Son duyuruyu ekle → `run_all.sh` → `check.py` → memo'ya gerçek sayıları koy | ZIP hazır |
| 17:50–18:00 | | Yükleme (10 dk tampon) | |
| 18:00–18:30 | | Prova, `ask.py` ile canlı persona denemesi | |

**Yedek planlar [ANALİZ]:**
- **API çökerse:** Saat başı başarılı bir tam run'ı sakla, demo ondan oynatılır.
- **Rate limit çıkarsa:** Persona sayısını 24–28'e indir (minimum 24).
- **Model:** Seçimi erken sabitle. Gün ortasında model değiştirmek saatler yer.

---

## 4. Karar paketleri (deneylerde karşılaştırılacak) [ANALİZ; maliyetler BRIEF]

| Paket | Karar 1 | Karar 2 | Toplam | Mantık |
|---|---|---|---|---|
| **A: Kalkan + Rezerv** | **W7**, grev haftasında MCO/PHL'ye dokunan rezervasyonlar: yedek yer hizmetleri ($0,5M) + partner rebook ($0,25M) + ücretsiz değişiklik ($0,2M) | Sürprize yanıt (W9/W10): kiralık uçak, otel, ek personel veya telafi kredisi | $0,95M + ≤ $2,05M | Bilinen krizi ucuza kapat, bütçeyi bilinmeyene sakla |
| **B: Hepsi grev için** | W7: yukarıdaki üçlü | **W8**: otel ($0,2M) + ek personel ($0,15M) + $75 kredi ($0,3M), etkilenenlere | ~$1,6M | En iyi G2/G3; sürprize cephane kalmıyor |
| **C: Kalkan + Gelir** | W7: yukarıdaki üçlü | W9/W10: sakin rotalarda indirim ($0,3M) + etkilenenlere çift puan ($0,1M) | ~$1,35M | G4'ü korur; NPS'i şansa bırakır |

**Tartışılacak gerilimler:**
- **W7 mi W8 mi?** W7'de mesaj grevden 1 hafta önce ulaşıyor, esnek yolcular kendiliğinden kayıyor. Ama "2 haftalık" kalemler W7–W8'i kapsıyor, grev W9'a uzarsa korumasız kalıyoruz. W8'de ise neredeyse hiç önceden haber yok (W8 21 Aralık'ta başlıyor, grev 22'sinde).
- **İade vs rebook:** İkisi de G2'yi karşılıyor. İade G4'ü düşürüyor; rebook kapasiteyi zorluyor.
- **$75 kredi vs $50 nakit:** Kredi daha ucuz ve çoğunlukla boş kalacak koltuklarda kullanılıyor [BRIEF]. Nakit ise "bize iyi davrandılar" algısında daha güçlü olabilir; persona'lara soralım.
- **Uçuş birleştirme (+$0,25M):** Bütçe açıyor ama G1'i ve şikâyetleri bozuyor. Muhtemelen hayır, deneyde görelim.

---

## 5. Beyin fırtınası: karara bağlanacak sorular (önerimiz ilk sırada)

1. **Ekip ve roller (kaç kişiyiz?).** Öneri, 4 rol:
   - **Engine:** llm, sim, hız.
   - **Personalar ve dünya:** havuz, operasyon modeli, kriz okumaları.
   - **Metrikler ve deneyler:** metrics, karşılaştırma tablosu, sanity testleri.
   - **Hikâye ve nöbet:** dashboard nöbeti, CLIENT_MEMO, TEAM_DOC, sunum, `ask.py`.
2. **Hangi gruplar, kaç persona?** Öneri: 5 grubun hepsi × 6–8 = **32–40 persona**. Seyahat acentesi personası bir grup rezervasyonunu temsil ediyor, ağırlığı buna göre.
3. **Hangi attribute'lar önemli?** Board soracak; katalogdaki önemsizler (burç, ayakkabı numarası…) bilerek konmuş.
   - **Öneri:** seyahat haftası ve üs, sabit/esnek tarih, çocuk/yaşlı ile seyahat, havalimanında yardım ihtiyacı (grev tekerlekli sandalye görevlilerini de vuruyor!), bagaj (bagaj işçileri de grevde), iade hakkını biliyor mu, acente mi online mı, sadakat seviyesi, şikâyet eğilimi ve sosyal medya kullanımı, fiyat hassasiyeti, rakip havayolu seçeneği.
   - **Dışarıda bırakılanlar:** cam kenarı/koridor, uçakta atıştırma, burç vb. TEAM_DOC'ta neden bırakıldıkları yazılacak.
   - **Hassas özellik yok, stereotip yok** [BRIEF].
4. **"Hafta durumu" ne demek, seyahati olmayan bir persona için?** Öneri: bu persona için "flies as planned" = sonraki Kestrel seyahati hâlâ planlandığı gibi duruyor. Her personaya 10 hafta içinde 1–2 somut uçuş ver (en az yarısı W8 civarında) ki grev gerçekten birilerine dokunsun.
5. **Krizleri kim okuyor: insan mı, LLM mi?** Öneri, hibrit:
   - **Biz:** her duyuruyu aynen kaydedip "nasıl okuduğumuzu" yazıyoruz [BRIEF ister].
   - **GM LLM çağrısı:** o haftanın haberlerini ve sosyal medya akışını üretiyor.
   - **Kod:** operasyon etkisini uyguluyor.
6. **Bizim fikrimiz ne olacak?** Jüri "an idea of your own" puanlıyor [BRIEF]. Aday fikirler aşağıda.

| Fikir | talp'e uyum | Maliyet | Not |
|---|---|---|---|
| **a) Say-do gap ölçer:** probe'daki beyan ("2a: kalacağım") vs 10 haftalık davranış (`moved to another airline`) | talp'in tezinin ta kendisi (*behaviour, not stated intent*) | Çok düşük: veri zaten toplanıyor | **Öneri: ana fikir** |
| b) Kriz okuma ensemble'ı: belirsiz duyuru → hafif/orta/ağır 3 okuma → hangi karar 3'ünde de iyi? | "Simülasyonun söyleyemediği" bölümüne doğrudan cevap | Orta: 3 kat run | Vakit kalırsa |
| c) Sosyal dalga: paylaşımlar arkadaş grafiğinde yayılıyor, şikâyet viralliği | "Kim duyuyor" sorusuna cevap | Orta | Dünya modeline hafif hâliyle zaten giriyor |

**talp bağlantısı:** **Strategy Intelligence** lensi (closed test) [VERIFIED] × **aviation** sektörü [VERIFIED]. Grev senaryosunu karar öncesi simüle ediyoruz, yani "hunch" yerine davranış. Say-do gap'i de beyan (probe) ile davranış (haftalık durum) arasındaki fark olarak ölçülebilir kılıyoruz.

---

## 6. Güvenilirlik paneli (en güçlü farklılaştırıcı) [ANALİZ]

- **Seed farkı:** plan_1 vs plan_2 ve nodecision_1 vs nodecision_2 → her hedef için aralık, ör. `G2: <x>% (seed'ler arası <y>–<z>)`.
- **Sanity testleri:**
  - Grev kapalıyken "rebooked" oranı düşmeli.
  - Bilerek kötü yazılmış (küçümseyen) bir mesaj güveni düşürmeli.
  - Gidiş ve dönüşü PHL/MCO dışında olan yolcular grevden etkilenmemeli.
- **Ters maddeler:** 2b ve 4b ters soruluyor [BRIEF]. "a" ile "b" puanları tutarlı mı? Bu bir evet-deme eğilimi (acquiescence) testi; bedava güvenilirlik metriği.
- **Oranlar için Wilson %95 GA**, ve N'yi açıkça söyle. 32 persona küçük bir örneklem; bunu dürüstçe söylemek jüride artı puan.
- **Persona çeşitliliği:** Çoğunluğun aksine davranan personaların payı. LLM'ler birbirine benzeyen cevaplara kayar (homogenisation, arXiv 2601.06116).
- **Aşırı rasyonellik önlemi:** Personalar sabırsız ve dikkati dağınık olabilmeli, "yanlış" karar verebilmeli (hyper-accuracy, arXiv 2208.10264).

---

## 7. Hemen sonraki adımlar

1. `export TALP_KEY=...` → `pip install google-genai` → `gemini-3.5-flash-lite` ile tek test çağrısı (5 dk).
2. §5'teki 6 soruyu 20 dk'da karara bağla → `notes/decisions.md`'ye her karar için 3 satır (karar, neden, sonraki adım).
3. Walking skeleton → **13:00'ten önce `check.py` yeşil**.

> Not: Brief "your code" diyor; hazır framework kullanımına bir kısıt görünmüyor ama emin değilsek organizatörlere soralım.
