# Örnek şirket raporu: kriz nasıl çözüldü, müşteri nasıl davrandı

> Amaç: Kestrel'in 22–23 Aralık taşeron grevine karar verirken, benzer bir krizi yaşamış gerçek bir şirketin **ne yaptığını** ve **müşterilerin nasıl davrandığını** kanıta dayandırmak.
> Araştırma tarihi: 2026-10-24. Kestrel kurgusal [BRIEF]; gerçek veriyi yalnızca davranış kalibrasyonu, sanity sınırı ve TEAM_DOC alıntısı için kullanıyoruz.
> Kaynak etiketi: **[RESMİ]** DOT/devlet · **[HABER]** · **[AKADEMİK]** hakemli · **[ANKET]** · **[ANALİZ]** bizim çıkarımımız · **[AÇIK]** bulunamadı.

---

## 0. Özet (önce bunu oku)

**Örnek şirket = Southwest Airlines, Aralık 2022 tatil krizi.** Kestrel'in krizine en yakın gerçek olay: yılın en yoğun haftasında, yer operasyonu çöktüğü için binlerce iptal. Yapısal ikiz ise **Frontier** (ULCC, Orlando+Philly, tek tip filo — bkz. [kestrel-real-world-grounding.md](kestrel-real-world-grounding.md) §1).

Üç cümlelik ders:
1. **Marka düştü ama çökmedi; ~2 ayda toparlandı.** Simülasyonda müşterilerin yarısı bir haftada kaçıyorsa model yanlış (brief de bunu söylüyor).
2. **Müşterileri kaybettiren kriz değil, kötü toparlanmaydı** — yavaş iade, hatalardan haberdar etmeme. Southwest'in $140M'lık DOT cezası iptaller için değil, **iade sürecini beceremediği** için [RESMİ].
3. **Hız ve sahiplenme, parayla verilen tazminattan daha çok sadakat kazandırıyor** [AKADEMİK]. Kestrel için kritik, çünkü grev bir **taşeronun** — "kimi suçluyorlar" davranışı belirliyor.

**Kestrel'e doğrudan etkisi:** proaktif + hızlı + açık bir karar, pahalı bir karardan daha iyi puan alır. İki kararımızdan en az biri "hız/iletişim/yeniden rezervasyon kapasitesi"ne gitmeli; salt nakit/kredi dağıtmak ikinci planda.

---

## 1. Southwest nasıl çözdü (toparlanma oyun kitabı)

| Ne yaptı | Detay | Kaynak | Kestrel karşılığı (menüden) |
|---|---|---|---|
| **Başka havayolundaki bileti bile geri ödedi** | Etkilenen yolcunun cebinden çıkan masrafı, rakip havayolundan aldığı bilet dahil karşıladı | [HABER/RESMİ] [DOT](https://www.transportation.gov/briefing-room/dot-penalizes-southwest-airlines-140-million-2022-holiday-meltdown) | "Rebooking deal with a partner airline" + "Goodwill" |
| **Geciken (iptal değil) yolculara 25.000 puan** | Sadece gecikme yaşayana jest; etkilenen ~2M'ye goodwill | [HABER] [CNBC](https://www.cnbc.com/2023/01/25/southwest-airlines-tries-to-improve-its-system-after-holiday-meltdown.html) | "Double loyalty points" ($0.1M) — ucuz ama herkese aynı etkiyi yapmaz |
| **Yemek/otel/yer ulaşımı geri ödemesi** | Krizden *önce* (Eyl 2022) müşteri hizmeti planını değiştirdi: havayolu kaynaklı aksamada bunları karşılıyor | [RESMİ] DOT | Kestrel'de bu zaten "business as usual" (3 saatten uzun gecikmede yemek, gecelik otel) |
| **>$600M iade/geri ödeme, toplam ~$1.1 milyar maliyet** | İade + geri ödeme + operasyon + kaybedilen satış, birkaç aya yayıldı | [HABER] [KERA](https://www.keranews.org/news/2023-01-06/southwests-strong-2022-rebound-soured-by-holiday-debacle), [CBS](https://www.cbsnews.com/texas/news/southwest-starts-on-reputation-repair-after-cancellations/) | Bizim bütçemiz $3M — ölçek bambaşka; ders **oran**, rakam değil |
| **Nerede başarısız oldu** | Binlerce yolcuya iade geç yapıldı; iade talebindeki hatayı yolcuya **haber vermedi** → $140M ceza | [RESMİ] DOT | **Ders:** "Extra airport and call-center staff" ($0.15M) + hakları açıkça söyleyen mesaj, cezadan korur |

**CEO Bob Jordan:** *"Goodwill'i bankadan çektik... güveni onarmak için işimiz var, ama müşterilerimiz çok sadık."* Bir analist: kriz *"markaya zarar verdi ama yok etmedi"* [HABER, CBS].

**Grevin tam mekaniği için (airline-caused değil, contractor-caused):** Finnair, Helsinki yer hizmetleri grevinde (May 2024) şu oyun kitabını kullandı [HABER, [Finnair](https://www.finnair.com/se-en/flight-information/archived-travel-information/effects-of-helsinki-airport-ground-handling-staff-s-walkout-on-our-flights-on-06-may-2024-3389540)]:
- Yeniden rezervasyonu self-servis "Manage Booking"e taşıdı; alternatif yoksa çağrı merkezi devrede.
- **Oteli yolcu kendi ayırsın, sonra makul masrafı geri alsın** (otel kıtken çağrı merkezi tıkanmasın diye).
- Bagaj gecikmesini önceden duyurdu; **"ilacınızı el bagajına alın"** dedi; SMS/e-posta ile bagaj takibi sözü verdi.

→ Kestrel'in grev mesajı bu kalıbı izleyebilir: *ne biliniyor, ne bilinmiyor, ne yapmalısın, hakkın ne.*

---

## 2. Müşteriler nasıl davrandı (kalibrasyon için)

| Davranış | Rakam | Kaynak | Simülasyona etki |
|---|---|---|---|
| **Marka toparlanma süresi** | Talep ~2 ay zayıf, Mart 2023'te rekor çeyrek | [HABER] KERA/CBS | Kayıp **geçici**: kriz sonrası dip var ama kalıcı kaçış yok |
| **Mevcut müşteri sadakati** | Southwest marka skoru 25→0'a düştü; ama **mevcut** müşteri memnuniyeti görece sabit; eski müşteride değerlendirme %53→%46 | [ANKET] YouGov (grounding §... [field-research.md](field-research.md)) | Düşüş **kademeli ve sınırlı**; en çok "eski/potansiyel" müşteride |
| **Geri dönen yolcu oranı** | Krizden etkilenenlerin yalnızca **%25'inin** Southwest'te gelecekte bileti vardı | [HABER] earnings call | "Would book again" doğrudan vurulanlarda sert düşer, ama… |
| **…çoğunluk zaten vurulmaz** | J.D. Power: yolcuların <%10'u sorun yaşıyor; "kötü" diyenin sadece %4'ü "kesin tekrar uçarım" (vs %81 "mükemmel") | [ANKET] J.D. Power (grounding §5) | Sert düşüş **yalnızca** doğrudan etkilenen tabakada; model bunu tabaka tabaka ayırmalı |
| **Söz-eylem açığı (say-do gap)** | Aksaklık sonrası %34 "bir daha seçmem" der; tekrarlı sorunda %65. Ama bu **beyan**, gerçek davranış daha düşük | [TİCARİ] Qualtrics/Sungard (field-research §1) | **talp'in tam konusu:** personalar "no" dese de gerçekte dönebilir; probe ile davranışı ölç, beyanı değil |
| **Hak bilgisi** | ABD'li yolcuların ~%7'si haklarını tam biliyor | [TİCARİ] AirHelp | Mesajda hakkı açıkça söylemek güven kazandırır; `knows_refund_rights` düşük tutuldu (doğru) |

**Sanity sınırı (ANALİZ):** En kötü ABD tatil krizi (Southwest) bile ~2 ay sürdü, kalıcı değil. Kestrel'in krizi daha küçük (48 saat, taşeron, yedek personel var). `nodecision` koşusunda bile toplam müşteri kaybı tek haneli yüzdede kalmalı; aksi halde model şişiyor.

---

## 3. Hangi çözüm işe yarıyor (servis toparlama bilimi)

Hakemli çalışmaların ortak bulgusu [AKADEMİK]:

- **Sahiplenme + düzeltme + tazminat + özür + yazılı takip** — en etkili beş hamle (Leow, 387 anket, [Salford](https://salford-repository.worktribe.com/output/1410723)).
- **Sadakate bağlanan tek kaldıraç: HIZ** (Tran 2024, [Cogent B&M](https://doaj.org/article/dfe0d0a797f44c52b4b7c35e853080bf)). Özür ve nezaket memnuniyeti artırır ama sadakati asıl hız belirliyor.
- **Suçu kim atfediyor, hangi tazminatın işe yarayacağını değiştiriyor** (Huang & Qu). **Kestrel için kilit:** grev taşeronun. Persona "Kestrel'i mi, taşeronu mu, sendikayı mı suçluyor?" — mesaj Kestrel sahiplenince mi, yoksa sebebi taşerona yıkınca mı daha iyi çalışıyor? Bu, "kendi fikrimiz" için güçlü bir deney.
- **Somut vs soyut zihin:** somut düşünen yolcu **voucher/kredi**'ye, soyut düşünen **puan/mil**'e daha iyi tepki veriyor (eHotelier). → Menüdeki "$75 kredi vs $50 nakit vs double points" seçimi persona tipine göre farklı sonuç verebilir.
- **Kusur havayolununsa** $50 indirim 2.500 mili yener; sebep kontrol dışıysa ikisi fark etmez (Hwang/Gao/Mattila, grounding §4). Grev "kontrol dışı" algılanabilir → nakit tazminatın marjinal faydası düşebilir.

---

## 4. Karara çevrildiğinde (ANALİZ — öneri)

Örnek şirketten çıkan net tasarım kuralları:

1. **En az bir karar "hız + kapasite + iletişim"e gitsin**, salt para dağıtmasın. Aday paket: *Extra airport/call-center staff ($0.15M) + Backup ground handling ($0.5M) + Free changes ($0.2M)* = $0.85M. Southwest'i batıran şey kapasite ve iletişim eksikliğiydi, para değil.
2. **İade/yeniden rezervasyonu hızlı ve görünür yap.** DOT cezası iptaller için değil, iadeyi beceremedikleri içindi. Mesaj yolcuya hakkını *açıkça* söylesin (hak bilen %7).
3. **Goodwill'i doğrudan vurulana hedefle.** "Up to 10,000 passengers" — etkilenen tabaka bu; herkese değil. $75 kredi ($0.3M) çoğu boş koltukta kullanılır (düşük gerçek maliyet).
4. **Mesajda suç atfını test et.** İki varyant koş: (A) Kestrel sahipleniyor, (B) sebep taşerona bağlanıyor. Hangisi "would book again"i ve şikâyeti daha iyi tutuyor?
5. **Partner rebooking ($0.25M)** Southwest'in "başka havayolunu bile öderiz" hamlesinin ucuz versiyonu — ağır senaryoda sigorta.

Bütçe $3M; yukarıdaki çekirdek ~$0.85M + hedefli goodwill $0.3M + partner $0.25M ≈ **$1.4M**, geri kalan ağır senaryoya uçak kiralama ($0.7M) için pay bırakır.

**talp bağlantısı (lens + sektör + tez):** Bu rapor Product/Strategy Intelligence'ın tam işi — aviation sektöründe bir kriz kararını, personaların **beyanı değil davranışı** (say-do gap) üzerinden test etmek. Southwest verisi "beyan edilen %34 kaçış"ın gerçekte çok daha düşük çıktığını gösteriyor; bizim probe'larımız bu açığı ölçmeli, varsaymamalı.

---

## 5. Açık işler

- [AÇIK] Taşeron grevinde bağımsız müşteri-memnuniyet verisi bulunamadı (Finnair/Charlotte yalnızca operasyonel). Grevi olasılık değil, **senaryo anahtarı** olarak çalıştır.
- [AÇIK] Nakit-vs-voucher'ın iptalden (gecikmeden değil) sonraki doğrudan karşılaştırması.
- Southwest Q1 2023 earnings call'un birincil kaydıyla "%25 geri dönüş" ve "$325M" rakamlarını doğrula (şimdilik [HABER]).

---

## Sonraki adım

Bu raporun §4'ünü `notes/decisions.md`'ye 3 satırlık karara indir (karar / neden / sonraki adım) ve §3'teki **suç-atfı deneyini** persona prompt'una bir `blames` alanı olarak ekle — iki mesaj varyantını `plan_1` ve bir alternatifte koşup "would book again" farkını ölç.

## Kaynaklar
- [DOT: $140M ceza](https://www.transportation.gov/briefing-room/dot-penalizes-southwest-airlines-140-million-2022-holiday-meltdown) · [CNBC: toparlanma](https://www.cnbc.com/2023/01/25/southwest-airlines-tries-to-improve-its-system-after-holiday-meltdown.html) · [KERA](https://www.keranews.org/news/2023-01-06/southwests-strong-2022-rebound-soured-by-holiday-debacle) · [CBS Texas: itibar onarımı](https://www.cbsnews.com/texas/news/southwest-starts-on-reputation-repair-after-cancellations/)
- [Finnair: Helsinki yer hizmetleri grevi](https://www.finnair.com/se-en/flight-information/archived-travel-information/effects-of-helsinki-airport-ground-handling-staff-s-walkout-on-our-flights-on-06-may-2024-3389540)
- [Leow, servis toparlama (Salford)](https://salford-repository.worktribe.com/output/1410723) · [Tran 2024, Cogent B&M (hız→sadakat)](https://doaj.org/article/dfe0d0a797f44c52b4b7c35e853080bf) · [UMass: servis toparlama değerlendirmesi](https://scholarworks.umass.edu/server/api/core/bitstreams/4de1ee71-5052-4368-b090-472c5142ddc0/content)
