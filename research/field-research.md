# Saha araştırması: Kestrel Air müşterileri

> Amaç: Persona'ları ve krizi kamuya açık verilere dayandırmak, dağılımları "neden böyle" diye savunabilmek.
> Araştırma tarihi: 2026-10-24. Kaynak kalitesi her satırda belirtiliyor: **[RESMİ]** devlet verisi · **[ANKET]** bağımsız veya sektör anketi · **[TİCARİ]** ürün satan şirketin anketi (taraflı olabilir) · **[HABER]** · **[VARSAYIM]** bizim kararımız.
> Kestrel, şirketleri ve rakamları kurgusal [BRIEF]. Gerçek veriyi yalnızca **davranış oranlarını ve dağılımları** kalibre etmek için kullanıyoruz.

---

## 1. Krizle doğrudan ilgili bulgular

| Bulgu | Kaynak | Persona / dünya tasarımına etkisi |
|---|---|---|
| **Southwest, Aralık 2022:** 21–31 Aralık arasında ~16.700 iptal. Fırtınayla başladı, ekip planlama sistemi çökünce büyüdü. Etkilenen ~2 milyon müşteriye 25.000'er puan verildi | [HABER] [NBC/CNBC](https://www.nbcbayarea.com/news/business/money-report/southwest-ceo-maps-out-a-recovery-after-holiday-meltdown-we-have-work-to-do/3139016/?amp=1), [AP](https://www.nbclosangeles.com/news/national-international/southwest-moves-to-rebuild-reputation-after-cancellation-chaos-during-holidays/3067940/?amp=1) | Tatil krizinin en yakın analogu. Telafi puanının (bizdeki "double loyalty points") gerçekte de denenmiş bir araç olduğunu gösteriyor |
| Southwest marka skoru 12 Aralık 2022'de net 25'ten 30 Ocak 2023'te 0'a düştü. Eski müşterilerde değerlendirme %53 → %46'ya indi. **Mevcut müşterilerin memnuniyeti görece sabit kaldı** | [ANKET] [YouGov](https://yougov.com/articles/45161-us-southwest-airlines-continues-be-caught-storm-ho), [YouGov](https://yougov.com/en-us/articles/46547-us-southwest-airlines-flights-delayed-again-how-has-the-airline-fared-in-recent-months) | **Sanity check:** Simülasyonda müşterilerin yarısı tek haftada kaçıyorsa model yanlış. Brief de aynı uyarıyı yapıyor. Kayıp, gerçek analogda **kademeli ve sınırlı** |
| Büyük, hava koşullarından kaynaklanmayan bir aksaklıktan sonra yolcuların **%34'ü** o havayolunu bir daha seçmeyeceğini söylüyor. Kısa sürede tekrarlanan sorunlarda bu oran **%65** | [TİCARİ] Qualtrics/[Sungard AS](https://www.sungardas.com/resources/infographics/airline-traveler-survey-outage/?hsLang=fr) | Etkilenen personalarda "would book again: no" oranı için **üst sınır kalibrasyonu**. Bu oran beyan; gerçek davranış daha düşük olabilir (say-do gap!) |
| **Charlotte, Kasım 2024:** SEIU'lu ~700 taşeron işçi (kabin temizliği, tekerlekli sandalye, ramp) Şükran Günü haftasında 24 saat greve çıktı. FlightAware'e göre **iptal yok**, gecikme az; grev büyük ölçüde sembolik kaldı | [HABER] [Business Traveller](https://www.businesstraveller.com/news/charlotte-airport-workers-strike-thanksgiving/), [WCAX/AP](https://www.wcax.com/2024/11/25/charlotte-airport-workers-strike-outset-busy-thanksgiving-travel-week) | **Grevi okurken:** "Replacement staff where it can" ifadesi gerçekte etkiyi ciddi biçimde sınırlayabiliyor. Hafif senaryo gerçekçi bir uç |
| **Philadelphia 2015–2017:** PHL'de taşeron işçiler (PrimeFlight, Prospect…) 2015'te kısa bir iş bırakma yaptı. 2016 (DNC sırasında) ve 2017'de grevler **son anda iptal edildi** | [HABER] [32BJ SEIU](https://www.seiu32bj.org/press-release/over-500-phl-airport-workers-go-on-strike/), [Inquirer](https://www.inquirer.com/philly/business/labor_and_unions/philly-airport-workers-plan-strike-20170711.html), [Prospect](https://prospect.org/2016/07/27/dnc-avoided-philly-airport-worker-strike/) | **Grevi okurken:** "Talks continue" → grevin iptal edilmesi de gerçek bir olasılık. Karar her iki duruma da dayanıklı olmalı (§5) |
| Grevi yapan meslekler: bagaj, kabin temizliği, **tekerlekli sandalye**, yakıt [BRIEF] | dossier | En çok etkilenecekler bagaj teslim edenler, yardım ihtiyacı olanlar ve refakatsiz çocuklar. Bu attribute'lar personalarda bilinçli olarak temsil ediliyor |
| **DOT otomatik iade kuralı** (28 Ekim 2024'ten beri): İptal veya ciddi gecikmede (yurt içi >3 saat, yurt dışı >6 saat) yolcu rebook'u seçmezse **nakit iade**. Kartla ödemede 7 gün içinde | [HABER] [NBC Miami](https://www.nbcmiami.com/responds/new-refund-rule-for-air-travelers-department-of-transportation/3458034/?amp=1), [Checkbook](https://www.checkbook.org/national/consumers-notebook/articles/Flight-Delayed-or-Canceled-Luggage-Lost-Know-Your-Rights-7739) | İade bizim kararımız değil [BRIEF]; dünya modeli otomatik uygular. G2 için "refunded" sayılır, G4'ten düşer |
| ABD'li yolcuların yalnızca **~%7'si** haklarını tam biliyor. Yalnızca üçte biri bir aksaklık sırasında haklarından haberdar edilmiş | [TİCARİ] [AirHelp 2025](https://airhelp.com/en/blog/air-passengers-rights-survey-2025-what-we-found-out) | `knows_refund_rights`: çoğunluk "bilmiyor" veya "belli belirsiz". Acenteler ve sık uçanlar istisna. **Mesajda hakları açıkça söylemek** güven kazandıran bir hamle olabilir |
| DOT şikâyetlerinde (Ocak–Haziran 2026) en büyük kategori **iadeler, %29**; ikincisi tarife ve iptal sorunları, %22 | [ANKET/RESMİ-türev] [AirAdvisor (DOT verisi)](https://airadvisor.com/en/statistics/us-airline-complaints) | Şikâyet modelinde iadenin gecikmesi en hızlı DOT şikâyeti üreten tetikleyici olmalı |
| **AAA 2025 yılsonu tahmini:** 8,03M kişi yurt içinde uçacak (rekor, +%2,3). **Noel'den hemen önceki günler en yoğun ve en pahalı** | [ANKET] [AAA/NBC](https://www.nbcmiami.com/news/national-international/christmas-new-years-travel-record-projections-2025/3732331/) | 22–23 Aralık'ta rakiplerde de koltuk yok ve pahalı. "Moved to another airline" seçeneği **pahalı ve zor**; fiyat hassas personalar için gerçekçi değil |

## 2. Müşteri profili bulguları

| Bulgu | Kaynak | Etkisi |
|---|---|---|
| ABD'li yetişkinlerin yaklaşık yarısı 2025'te uçtu. 18–24 yaş grubunun uçma eğilimi en yüksek. Yolcuların %87'si fiyatı en önemli kriterler arasında sayıyor | [ANKET] [A4A/Ipsos 2026](https://www.airlines.org/news-update/nearly-half-of-americans-chose-to-travel-by-air-in-2025/) | Fiyat hassasiyeti çoğu personada "yüksek". Öğrenci grubu gerçek bir segment |
| 2018–2022 arasında katılımcıların %19'u kişisel bir seyahatte ULCC'lerden (Spirit, Frontier, Allegiant, Avelo…) biriyle uçtu | [ANKET] [A4A 2023](https://www.airlines.org/wp-content/uploads/2023/03/A4A-Air-Travel-Survey-2023-Key-Findings.pdf) | Kestrel müşterileri aynı anda diğer düşük maliyetli havayollarını da kullanıyor ("başka zamanlarda başkasıyla" [BRIEF]) |
| Düşük maliyetli havayolu yolcularında akraba ziyareti ve tek başına seyahat artıyor | [ANKET] [Charleroi 2021](https://difusion.ulb.ac.be/vufind/Record/ULB-DIPOT:oai:dipot.ulb.ac.be:2013/332090/TOC) (Avrupa) | "Families visiting relatives" en büyük grup olmalı |
| Gece konaklamalı yurt içi seyahatlerin %41'i akraba ziyareti; bunların %23'ünde uçak kullanılıyor (2021 2. çeyrek, tüm ulaşım türleri) | [ANKET] [Longwoods](https://longwoods-intl.com/news-press-release/longwoods-international-travel-usar-highlights-january-june-2021) | Grup ağırlıklarını desteklemek için kullanıldı (§4) |
| Kendi düşük maliyetli havayoluna sadakat **çok zayıf** (2011 akademik çalışma). Gen Z'nin %65'i, Boomer'ların %89'u sadakat programına kayıtlı. Engel: tek bir havayoluyla düzenli uçmamak | [ANKET] [Chacon & Mason](https://ideas.repec.org/a/wly/transj/v50y2011i3p271-290.html), [OAG 2024](https://www.businesswire.com/news/home/20240604932830/en/Gen-Z-Travel-Habits-Usher-in-New-Future-for-Airline-Rewards-Programs-OAG-Survey-Reveals) | `loyalty_tier`: çoğunluk "none/basic". Yalnızca birkaç sık uçan Silver/Gold. "Double points" kararı herkese aynı etkiyi yapmaz |
| ~%33 uçmaktan korktuğunu söylüyor; hiç uçmamışlarda %74 | [TİCARİ] [Upgraded Points](https://upgradedpoints.com/travel/which-us-states-are-most-afraid-of-flying/) · Gallup 1999: düzenli uçanların %21'i "çoğu zaman korkuyor" [ANKET] | `fear_of_flying`: ~1/3 "biraz/orta", birkaç kişi "güçlü". Belirsizlik ve gecikme bu kişilerde kaygıyı büyütür |
| PreCheck'in 20M+ üyesi var (Ağustos 2024); Global Entry dahil 40M+ kişinin PreCheck erişimi var | [HABER] [TravelPulse/TSA](https://www.travelpulse.com/news/airlines-airports/tsa-precheck-reaches-record-20-million-members) | `tsa_precheck`: fiyat hassas bu kitlede ~%25 (VARSAYIM). İş yolcuları ve sık uçanlarda daha yüksek |
| **Bagaj:** 2025'te yolcuların %71'i bagaj vermekten kaçındığını söylüyor ([TİCARİ] LugLess); 2016'da %48'i sadece kabin bagajıyla uçuyordu ([ANKET] Expedia) | [BusinessWire](https://www.businesswire.com/news/home/20250617837060/en), [Malay Mail/Expedia](https://www.malaymail.com/news/travel/2016/01/21/why-overhead-bins-are-so-crowded-and-other-flyer-behavioural-quirks/1045413) | Tatilde hediye, çocuk ve uzun kalış bagajı artırır → `checks_bag` ~%40–50 (VARSAYIM). Bagaj işçileri grevde, yani bunlar daha kırılgan |
| **MCO'ya ulaşım:** Yolcuların %78'i araçla geliyor. Bunların %30'u kiralık araç, %28'i Uber/Lyft, %20'si aile veya arkadaş bırakıyor, kalanı otopark veya shuttle. Toplu taşıma %0,4 | [HABER/RESMİ-türev] [Bay News 9 (GOAA)](https://baynews9.com/fl/tampa/news/2026/05/13/how-passengers-arrive-to-mco) | `airport_access` dağılımı. Kiralık araçla dönüşü olan veya bırakılmayı bekleyen birinin iptali ek maliyet yaratır |
| **Rezervasyon kanalı:** Havayolu sitesi %36, OTA %33 (PhoCusWright, eski veri). Yalnızca ~%13 klasik acenteyi tercih ediyor (2005) | [ANKET] [PhocusWire](https://www.phocuswire.com/A-new-problem-for-OTAs-Airline-websites-are-outselling-them-in-the-US), [Synovate](https://www.hotelexecutive.com/newswire/10307/asta-responds-to-synovate-survey) | `booking_channel`: direkt (app/site) yaklaşık yarı, OTA (Expedia vb.) yaklaşık 1/3, acente az. **OTA'dan alanlar yeniden rezervasyonda daha çok sorun yaşar** (aracı var) |
| **Engelli yolcular:** ~17M engelli kişi her yıl uçuyor (DOT 2005). American Airlines 2023'te 8M+ tekerlekli sandalye talebi aldı. 2021'de engelli şikâyetlerinin %51'i tekerlekli sandalye yardımıyla ilgiliydi | [RESMİ] [DOT](https://www.transportation.gov/sites/dot.gov/files/2023-10/Summary%20Report%202021.pdf), [KUOW](https://www.kuow.org/stories/american-airlines-fined-50-million-for-its-treatment-of-passengers-with-disabilities) | Az sayıda ama çok yüksek etkili segment. Grev tekerlekli sandalye görevlilerini de kapsıyor → en az 1–2 persona |
| **Koltuk:** Pencere %58–67, koridor %12–40. Sık uçanlar koridoru tercih ediyor | [ANKET] [Upgraded Points](https://upgradedpoints.com/news/ultimate-airplane-seat-survey/), [Quartz](https://qz.com/267961/the-more-people-fly-the-more-they-prefer-the-aisle-seat) | `seat`: ~%60 pencere; iş yolcuları ve sık uçanlar koridor. Krizle ilgisi düşük (§3) |
| **Öğrenciler:** Tatilde eve dönüş büyük bir masraf. Erken alan ucuza alıyor; uzaktan gelen ve uluslararası öğrenciler en çok zorlananlar | [HABER] [F Newsmagazine 2026](https://fnewsmagazine.com/2026/01/what-it-costs-to-go-home/), [Stanford Daily](https://stanforddaily.com/2021/12/02/students-express-frustration-with-high-travel-costs-due-to-winter-quarter-start-date/) | Final sınavları Aralık ortasında bitiyor; 18–22 Aralık eve dönüşün zirvesi. Kimisi kendi ödüyor, kimisinin ailesi |
| **Bölge geliri:** Orlando metrosunda medyan hane geliri ~$52K (eski ACS) | [HABER] [Orlando Weekly (ACS)](https://www.orlandoweekly.com/news/orlando-ranks-among-nations-worst-for-income-says-recent-census-survey-7113085/) | Gelir bantları geniş, alt ve orta bant ağırlıklı. Güncel ACS B19013 tablosu doğrulanmadı (açık iş) |

## 3. Hangi attribute'ları kullandık, hangilerini bilerek bıraktık

**Kriz için kritik olanlar (davranışı değiştirir):**
- **Seyahat tarihi ve üs:** grev yalnızca 22–23 Aralık'ta MCO ve PHL'de.
- **Tarih sabit mi esnek mi:** ücretsiz değişiklik kararının etkisini belirliyor.
- **Bagaj:** bagaj işçileri grevde.
- **Havalimanında yardım ihtiyacı ve refakatsiz çocuk:** tekerlekli sandalye görevlileri de grevde.
- **Çocuk veya yaşlı ebeveynle seyahat:** sabır ve alternatif bulma kapasitesi düşüyor.
- **İade hakkını biliyor mu:** iade isteyip istemeyeceğini ve şikâyet kanalını belirliyor.
- **Rezervasyon kanalı:** OTA veya acente aracılığıyla alanlarda rebook zorlaşıyor.
- **Fiyat hassasiyeti ve elindeki rakip seçenekleri:** "moved to another airline" seçeneğinin gerçekçi olup olmadığını belirliyor.
- **Sadakat seviyesi:** puan teklifinin cazibesini belirliyor.
- **Şikâyet eğilimi ve sosyal medya kullanımı:** G3'ü ve haberin kime ulaşacağını belirliyor.
- **Bilgiyi nereden alıyor:** grev haberini kim, nereden duyuyor.
- **Seyahatin önemi:** kaçırılırsa ne kaybediyor (kruvaziyer, düğün, iş başı…).

**Bağlam için kullanılanlar:** uçuş sıklığı, seyahat sebebi, havalimanına ulaşım (dönüş planı bozulursa ek maliyet), uçuş korkusu (belirsizlikte kaygı), aktarma toleransı (partner veya aktarmalı rebook'u kabul eder mi), işveren ödüyor mu, PreCheck (hızlanmış güvenlik, krizde küçük etki).

**Dossier'de olup etkisi düşük olanlar:** pencere/koridor tercihi, uçakta atıştırma, favori destinasyon. Dossier tam olsun diye dolduruyoruz ama davranış prompt'unda ağırlıkları düşük.

**Bilerek bırakılanlar:** Katalog bölüm I'nın tamamı (burç, favori renk, ayakkabı numarası, solak/sağlak, boy, kahve siparişi…). Grev veya karar karşısındaki davranışla savunulabilir bir ilişkisi yok. Board sorarsa cevabımız: "*O attribute'lar davranışı değiştirmez ama LLM'i stereotipe iter.*"

**Hassas özellikler:** Etnik köken, din, siyasi görüş, göçmenlik statüsü kullanılmadı. Sağlıkla ilgili tek bilgi, dossier'nin kendi alanı olan havalimanı yardım ihtiyacı. Bir personanın sendikalı olması, greve **bakışını** etkileyen meslekle ilgili bir bilgi ve doğrudan bu krize ait (TEAM_DOC'ta gerekçelendirilecek).

## 4. Örneklem ve ağırlıklar [VARSAYIM, gerekçeli]

| Grup | Persona sayısı | Müşteri payı (varsayım) | Persona başına temsil (haftalık yolcu) | Gerekçe |
|---|---|---|---|---|
| families visiting relatives | 9 | %38 | ~8.870 | Düşük maliyetli havayolları ve tatil dönemi için en büyük segment (Longwoods %41 akraba ziyareti; Charleroi) |
| vacationers | 9 | %37 | ~8.630 | Orlando'nun tema parkları ve kruvaziyer kapısı olması; Karayipler/Meksika rotaları |
| students | 6 | %9 | ~3.150 | 18–24 yaşın uçma eğilimi en yüksek (A4A); Philadelphia ve Orlando büyük üniversite şehirleri |
| business travelers | 6 | %9 | ~3.150 | Dossier'ye göre "some small business travelers": küçük ama gelir için önemli |
| travel agencies | 6 | %7 | ~2.450 | Grup rezervasyonları; bir acente personası onlarca yolcuyu temsil ediyor |

**Tabakalı örneklem uyarısı (metrik sahibi için):**
- 36 personanın 16'sı grev günlerinde MCO veya PHL'den uçuyor. Bu bilerek yapılmış bir **aşırı örnekleme**; gerçekte bu oran çok daha düşük.
- Bu yüzden metrikleri iki adımda hesaplayın: personalardan **tabaka içi davranış oranları** (etkilenen / komşu gün / etkilenmeyen) çıkar, gerçek yolcu sayıları ise **operasyon modelinden** gelir.
- Ham persona ağırlıklarıyla doğrudan toplam almayın.

**Elde edilen dağılım (30 bireysel yolcu, acenteler hariç; `code/personas.py` çıktısı):**

| Attribute | Bizdeki oran | Referans | Not |
|---|---|---|---|
| Bagaj veriyor | 18/30 (%60) | %29–52 kabin bagajı dışında bagaj veren (anketler) | Tatil etkisi: hediye, çocuk eşyası, uzun kalış. Bilinçli olarak yüksek tutuldu |
| PreCheck | 10/30 (%33) | 40M+ kişinin erişimi var | İş yolcuları yukarı çekiyor |
| Uçuş korkusu (en az hafif) | 8/30 (%27) | ~%33 | |
| İade hakkını iyi biliyor | 3/30 (%10) | ~%7 (AirHelp) | 13 kişi "kısmen", 14 kişi "bilmiyor veya belli belirsiz" |
| Pencere tercihi | 13/30 (%43) | %58–67 | İş yolcusu ağırlığı koridoru artırıyor (Quartz: sık uçanlar koridor seçiyor) |
| OTA üzerinden almış | 4/30 (%13) + acenteler | ~%33 (eski veri) | Düşük maliyetli havayolu müşterisi daha çok direkt alıyor (VARSAYIM) |
| Havalimanında yardım gerekiyor (tekerlekli sandalye veya refakatsiz çocuk) | 8 persona (grup içindekiler dahil) | Az ama yüksek etkili | Grev bu hizmetleri doğrudan vuruyor |
| Yaş | 18–81 | | 19 kadın, 16 erkek, 1 non-binary |

**Başlangıç NPS kalibrasyonu:**
- Dossier NPS'i +12 [BRIEF]. 36 personaya promoter / passive / detractor dağılımı 13 / 15 / 8 verildi: (13 − 8) / 36 ≈ **+14**.
- Bu yalnızca başlangıç hâli. Probe'lar başlangıçta bunu doğrulamalı; doğrulamıyorsa persona kartları gözden geçirilmeli.

## 5. Grev nasıl okunmalı (araştırmaya göre)

Belirsizlik çok gerçek; üç senaryo da tarihsel olarak yaşanmış:
- **Hafif** (Charlotte 2024): yedek personel var, iptal yok, gecikmeler var, bagaj ve yardım hizmetleri yavaş.
- **Orta:** iki üste turnaround'lar yavaş, kısmi iptaller, bagaj gecikmeleri, tekerlekli sandalye beklemeleri.
- **Ağır** (sendika "may be extended" dedi): 24 Aralık'a uzama ve zincirleme iptaller. Rakipler de dolu ve pahalı (AAA).
- **İptal** (PHL 2016/2017): grev son anda iptal edilir.

→ İyi karar dört senaryonun hepsinde savunulabilir olmalı. Yedek yer hizmetleri sözleşmesi ağır senaryoda sigorta işlevi görür, hafif senaryoda ise "boşa para" olarak görülebilir. Bu ödünleşimi board'a açıkça söyleyelim.

## 6. Açık işler

- Güncel ACS metro gelir tablosu (B19013): Orlando-Kissimmee-Sanford ve Philadelphia-Camden-Wilmington.
- DOT'un 2025 tam yıl şikâyet kategori dağılımı.
- BTS T-100: MCO ve PHL'deki gerçek düşük maliyetli havayolu payları. Kestrel kurgusal, ama rota gerçekçiliği için yararlı.
