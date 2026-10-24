# Kestrel Air: real-world grounding

Collected 2026-10-24 for the TALP Simulation Lab. Kestrel Air is fictional; **the dossier's numbers always win**. Real data below is used only for (a) persona grounding, (b) sanity bounds on simulated outcomes, (c) TEAM_DOC citations.

Tags: `[OFFICIAL]` DOT/BTS/Census/company filing · `[MEDIA]` news or Wikipedia (secondary) · `[ACADEMIC]` peer-reviewed · `[SURVEY]` vendor/advocacy survey · `[GAP]` searched, not found — do not fill with a guess.

## 1. Closest real analog: Frontier Airlines

Why: US ultra-low-cost carrier, single A320-family fleet, bases include Orlando and Philadelphia (Kestrel's two bases), leisure/VFR-heavy customers, Mexico/Caribbean flying. Kestrel is roughly a one-third-scale Frontier.

| Metric | Frontier | Allegiant | Kestrel (dossier) | Source |
|---|---|---|---|---|
| Fleet | 159 A320neo family | mixed A319/A320 | 36, one family | Wikipedia [MEDIA] |
| Passengers / yr | 33.3M (2024) | not verified | 11M | Wikipedia [MEDIA] |
| Complaints per 100k pax, DOT, 2024 | **23.3** (worst of 10) | not found [GAP] | 2,500/mo total, ~150/mo to DOT | PIRG "Plane Truth" from DOT data [SURVEY] |
| Complaints per 100k, 2023 | 32.99 | 5.97–7.47 band | | PIRG [SURVEY] |
| Cancellation rate 2024 | 2.56% (3,252 flights) | 2.37% (1,664) | not stated | Daily Passport analysis [MEDIA] |
| On-time Dec 2024 | 75.0% | 71.8% | 79% (normal) | BTS Dec 2024 ATCR [OFFICIAL] |
| Industry 2024 | on-time 78.10%, cancellations 1.4% | | | BTS [OFFICIAL] |

Context: Spirit (the other Orlando-heavy ULCC; 12.8 complaints/100k in 2024 [SURVEY]) **ceased operations on 2 May 2026** ([NPR](https://npr.org/2026/05/02/nx-s1-5807933/spirit-airlines-ceases-operations-folds) [MEDIA]). In-world this is useful realism: a price-sensitive Orlando passenger in Nov 2026 has fewer ULCC alternatives, and some personas may be ex-Spirit customers who already lived through a stranding.

Sanity reading of the dossier: Kestrel's DOT complaints ≈ 150/mo ÷ (210k × 4.3 weeks) ≈ **17 per 100k** — between Spirit and Frontier. Consistent with a ULCC; do not let the baseline simulation drift far from it.

## 2. Disruption case studies

### Southwest, Dec 21–31, 2022 (worst-case holiday meltdown; airline-caused)
- ~16,700 flights canceled; >2M passengers affected by cancellations and delays. [OFFICIAL, via SEC filing in media]
- Q4 2022 cost $725–825M; Q1 2023 revenue hit ≈ **$325M** from canceled return trips and **slower Jan–Feb bookings**; demand strong again by **March 2023** (record Q1 revenue). [MEDIA, company earnings call]
- On the Q1 call: **only 25% of meltdown-affected customers had future travel booked on Southwest** (some with goodwill points). [MEDIA]
- >$600M refunds/reimbursements; DOT penalty $140M announced 18 Dec 2023 (largest consumer-protection penalty to date; split between cash and credits is reported inconsistently — check the consent order before quoting). [OFFICIAL via media]
- Lesson: even the worst US holiday failure hurt bookings for ~2 months, not permanently. A simulation where most passengers leave forever after a 48-hour strike fails the challenge's own sanity rule.

### Ground-handling / airport-contractor strikes
- **Charlotte, 25 Nov 2024 (Thanksgiving week):** SEIU workers at ABM and Prospect (contractors to American) — cabin cleaners, wheelchair attendants, ramp — 24-hour strike. ~30 American flights (~4%) delayed by mid-afternoon, "not out of the ordinary"; American predicted no significant disruption. [MEDIA: TravelPulse, Scripps]
- **Brussels (date not found):** Swissport baggage-handler walkout → 34 flights canceled by late afternoon; Swissport handles luggage for ~60% of flights there. [MEDIA: VRT]
- **Munich (date not found):** Verdi strike at Swissport Losch (~40% of movements) → 36 flights canceled. [MEDIA]
- **Geneva, Dec 2023 (likely):** dnata crew strike; dnata handled 85 of 417 flights; delays of 2–3 h and a few cancellations on the dnata side. [MEDIA]
- **Spain 2023 (Swissport):** government minimum-service orders protected 55–86% of flights. [MEDIA]
- **How often strikes get extended:** [GAP]. Not found in public data; treat it as a scenario switch, not a probability.
- Lesson: the spread of real outcomes is wide — from "4% delayed" to dozens of cancellations per day. The dossier says "some flights may be late or canceled." Run the strike at more than one severity and report the range.

## 3. Rules the personas live under (not decisions)

- DOT automatic-refund rule in full effect since **28 Oct 2024**: cash refund for cancellation or a "significant change" (domestic >3 h late, international >6 h). Airlines may offer rebooking or credit, but must tell passengers about the cash refund first. Refund due in 7 business days (card) or 20 calendar days (other). Bag fee refunded if a domestic bag is >12 h late. Parts of the rule are under administrative reconsideration. [OFFICIAL via [DOT](https://www.transportation.gov/briefing-room/what-airline-passengers-need-know-about-dots-automatic-refund-rule) and law-firm summaries]
- The 2025 proposal for cash compensation on delays was **withdrawn 17 Nov 2025** — so there is no legal cash payout for delays. [MEDIA]
- Wheelchair: DOT rule (Dec 2024) presumes a violation if a wheelchair comes back damaged; American was fined $50M (Oct 2024) for wheelchair-assistance failures. [OFFICIAL via media] — relevant because striking wheelchair agents are contractor staff.

Persona prompt implication: Mexico/Caribbean flights count as international (6 h threshold). A persona's "knows refund rights" attribute should change what they ask for, not what the law gives them.

## 4. Compensation: cash vs credit (decision menu: $75 credit vs $50 cash)

- Hwang, Gao & Mattila (2020), *Int. J. Hospitality Management*: after a flight delay, a **$50 discount beat 2,500 bonus miles on repatronage only when the delay was seen as the airline's fault**; with an uncontrollable cause, the two did not differ. [ACADEMIC]
- Huang & Qu: compensation and communication effects depend on who passengers blame. [ACADEMIC]
- Direct cash-vs-voucher study after cancellation: [GAP].
- Voucher redemption/breakage rates: [GAP] (the dossier's own note — "most credits are used on seats that would fly empty" — is the only figure; use it as given).

**Modelling idea:** for each persona, simulate **who they blame** (Kestrel vs "the contractor" vs "the union"). The literature says this attribution is what makes compensation work, and the strike is a contractor's — so the message wording (does Kestrel own it?) can change outcomes. This is a candidate for "an idea of your own".

## 5. Persona grounding

| Attribute | Data | Source |
|---|---|---|
| Orange County, FL (Orlando) median household income | $77–81k (ACS 5-yr); by householder age 25–44: $82.3k, 45–64: $89.4k, 65+: $56.6k | Census ACS S1901 [OFFICIAL] |
| Philadelphia County, PA median household income | $60.7k; poverty 22.0% (2023 ACS 5-yr) | Census ACS S1901 [OFFICIAL] |
| Age / household mix | pull directly | Census ACS DP05 [OFFICIAL] |
| Holiday air volume | TSA record 3.1M screened on Sun 1 Dec 2024; Christmas peak 2.85M on 27 Dec 2024; AAA year-end 2025: 8.03M by air | TSA, AAA [OFFICIAL/SURVEY] |
| US → Mexico trips | 17.1M (2024), 18.6M projected 2025 | US Travel / Tourism Economics [SURVEY] |
| ULCC experience | 65% of Americans flew a ULCC in the past 5 years | Ipsos / A4A 2024 [SURVEY] |
| After a bad trip | J.D. Power 2025: <10% of passengers had a problem; only 4% of those rating a trip "poor" say they will "definitely" fly that airline again vs 81% for "perfect" | J.D. Power [SURVEY] |
| Group shares (vacationers / VFR / students / business / agencies) | [GAP] — no public split; choose and justify in TEAM_DOC |
| Refund-rights awareness by segment | [GAP] |
| Booking channel / agency share for ULCCs | [GAP] |

Census values are dossier-compatible anchors; fetch exact figures from data.census.gov before quoting them on a slide.

## 6. Sanity bounds for the simulation (derived; label as analysis)

- Normal week: complaint rate near the dossier's baseline (~17 DOT complaints per 100k); cancellations ≈ 1–3% (industry 1.4%, ULCC 2.4–2.6% in 2024).
- Strike week: plausible range from "few % delayed" (Charlotte 2024) to dozens of daily cancellations (Brussels/Munich). Report the outcome as a range across seeds and severities.
- Post-crisis demand: a dip that recovers over weeks (Southwest: ~2 months), not permanent loss.
- "Would book Kestrel again": after a bad trip this should fall sharply for those directly hit (J.D. Power 4% vs 81%), but most passengers are not directly hit.

## Sources
- [NerdWallet: Southwest $140M penalty](https://www.nerdwallet.com/article/travel/southwest-faces-140-million-penalty-for-2022-holiday-meltdown) · [NPR](https://www.npr.org/2023/12/18/1219906471/southwest-airlines-2022-meltdown-fined-faa) · [TMJ4: SEC filing $725–825M](https://www.tmj4.com/news/national/holiday-travel-disruptions-could-cost-southwest-up-to-825-million) · [Yahoo Finance: Q1 2023 losses](https://hk.finance.yahoo.com/news/southwest-earnings-airline-reports-losses-from-holiday-meltdown-top-11-billion-114411887.html) · [Airways: Q1 2023](https://airwaysmag.com/southwest-q1-2023-losses)
- [TravelPulse: Charlotte strike](https://www.travelpulse.com/news/airlines-airports/airport-workers-in-charlotte-strike-for-better-pay-labor-practices-during-thanksgiving-travel-rush) · [Scripps](https://www.scrippsnews.com/life/travel/workers-at-charlotte-airport-an-american-airlines-hub-go-on-strike-during-thanksgiving-travel-week) · [Business Traveller](https://www.businesstraveller.com/news/charlotte-airport-workers-strike-thanksgiving/)
- [VRT: Brussels](https://vrtnws.be/p.py44aLLbk) · [La Voz de Lanzarote: Swissport minimum services](https://www.lavozdelanzarote.com/en/ekonomus/economy/swissport-strike-72-of-flights-to-the-peninsula-and-57-to-foreign-countries-protected_217326_102.html) · [Guardian NG: Geneva](https://guardian.ng/news/flights-delayed-as-geneva-airport-workers-go-on-strike/) · [reisetopia: Munich](https://reisetopia.de/news/warnstreik-am-flughafen-munchen/amp/)
- [DOT: automatic refund rule](https://www.transportation.gov/briefing-room/what-airline-passengers-need-know-about-dots-automatic-refund-rule) · [Reed Smith summary](https://www.reedsmith.com/our-insights/blogs/legal-flight-deck/102k66z/dot-finalizes-rule-requiring-automatic-refunds-of-airline-tickets-and-ancillary-s/) · [TravelPulse](https://www.travelpulse.com/news/airlines-airports/what-travelers-need-to-know-with-new-dot-refund-rule-for-air-travelers-now-in-effect)
- [PIRG Plane Truth 2024](https://pirg.org/resources/plane-truth-2024/) · [PIRG Plane Truth 2025 PDF](https://publicinterestnetwork.org/wp-content/uploads/2025/07/PLANE-TRUTH-2025-5-23-800.pdf) · [Westword](https://www.westword.com/news/denver-airline-leads-country-in-air-travel-complaints-24548453/)
- [BTS: ATCR Dec 2024 / full-year 2024](https://www.bts.gov/newsroom/air-travel-consumer-report-december-2024-full-year-2024-numbers) · [Daily Passport: cancellation rates](https://dailypassport.com/us-airlines-best-worst-cancellation-rates/)
- [NPR: Spirit ceases operations](https://npr.org/2026/05/02/nx-s1-5807933/spirit-airlines-ceases-operations-folds)
- [Hospitality Net: "Money or Miles" (Hwang, Gao & Mattila)](https://www.hospitalitynet.org/news/4109143.html) · [PolyU record](https://irarecord.lib.polyu.edu.hk/handle/10397/90526) · [Inderscience: Aegean repurchase study](https://www.inderscience.com/offers.php?id=122238)
- Wikipedia pages for Frontier, Allegiant, Sun Country (accessed 2026-10-24) — secondary; verify against 10-K before quoting.
- Census ACS S1901 / DP05 via data.census.gov; TSA and AAA newsroom releases (via subagent; re-check exact figures before slides).
