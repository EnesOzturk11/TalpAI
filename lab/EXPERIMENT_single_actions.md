# Single-action experiments (simulation output, not measurements)

Runs: x_base, x_backup_w7, x_backup_w8, x_credit75_w8, x_credit75_w9, x_freechange_w6, x_freechange_w7, x_hotel_w7, x_hotel_w8, x_partner_w7, x_partner_w8, x_staff_w7, x_staff_w8 · seed 1 · 20 personas · model gemini-3.5-flash-lite · weighted by world.json customer_mix (team assumption).
Same seed in every run, so each run faces the same dice; differences come from the action and the model.

| action | week | cost $M | week-8 flights hit / stranded | lost at any week % (Δ) | book again 'no' wk10 % (Δ) | satisfaction wk8 → wk10 (Δ wk10) | blame Kestrel wk8 % (Δ) | rebooked ≤24h % | NPS proxy | revenue wk5-10 % |
|---|---|---|---|---|---|---|---|---|---|---|
| **no decision (base)** | - | 0 | 6/14 · 2 | 18.8 (–) | 26.3 (–) | 54.4 → 70.6 (–) | 38.7 (–) | 58.06 | -58.8 | 82.19 |
| backup ground handling | 7 | 0.5 | 2/14 · 1 | 2.5 (-16.3) | 0.0 (-26.3) | 62.5 → 77.5 (+6.9) | 25.0 (-13.7) | 30.0 | -30.0 | 98.17 |
| backup ground handling | 8 | 0.5 | 2/14 · 1 | 2.5 (-16.3) | 8.7 (-17.6) | 68.1 → 81.9 (+11.3) | 13.8 (-24.9) | 30.0 | -42.5 | 98.17 |
| hotel rooms | 8 | 0.2 | 6/14 · 2 | 2.5 (-16.3) | 10.0 (-16.3) | 67.5 → 71.9 (+1.3) | 41.2 (+2.5) | 58.06 | -35.0 | 98.17 |
| hotel rooms | 7 | 0.2 | 6/14 · 2 | 11.2 (-7.6) | 8.7 (-17.6) | 52.5 → 76.2 (+5.6) | 41.2 (+2.5) | 58.06 | -35.0 | 98.17 |
| partner airline | 7 | 0.25 | 6/14 · 1 | 11.2 (-7.6) | 11.2 (-15.1) | 58.8 → 69.4 (-1.2) | 38.7 (+0.0) | 77.42 | -63.7 | 91.78 |
| extra staff | 7 | 0.15 | 6/14 · 1 | 11.2 (-7.6) | 11.2 (-15.1) | 58.1 → 68.8 (-1.8) | 38.7 (+0.0) | 77.42 | -62.5 | 91.78 |
| extra staff | 8 | 0.15 | 6/14 · 1 | 11.2 (-7.6) | 18.8 (-7.5) | 60.0 → 65.6 (-5.0) | 38.7 (+0.0) | 77.42 | -55.0 | 91.78 |
| partner airline | 8 | 0.25 | 6/14 · 1 | 11.2 (-7.6) | 26.3 (+0.0) | 54.4 → 63.1 (-7.5) | 42.5 (+3.8) | 77.42 | -48.8 | 91.78 |
| goodwill $75 travel credit | 8 | 0.3 | 6/14 · 2 | 18.8 (+0.0) | 11.2 (-15.1) | 63.1 → 68.1 (-2.5) | 30.0 (-8.7) | 58.06 | -43.8 | 82.19 |
| goodwill $75 travel credit | 9 | 0.3 | 6/14 · 2 | 18.8 (+0.0) | 17.5 (-8.8) | 54.4 → 63.1 (-7.5) | 38.7 (+0.0) | 58.06 | -55.0 | 82.19 |
| free changes | 7 | 0.2 | 6/14 · 2 | 18.8 (+0.0) | 22.5 (-3.8) | 56.9 → 60.0 (-10.6) | 30.0 (-8.7) | 58.06 | -56.2 | 82.19 |
| free changes | 6 | 0.2 | 6/14 · 2 | 27.5 (+8.7) | 27.5 (+1.2) | 53.8 → 59.4 (-11.2) | 38.7 (+0.0) | 58.06 | -61.2 | 75.8 |

Sorted by fewest passengers lost. Δ = difference from the no-decision base (percentage points). 'hit' = week-8 flights canceled or 3h+ late; 'stranded' = of those, no new seat within 24h.
With 20 personas and one seed, a few personas move these numbers: 'lost' interval for the base is 6-43%. Treat small Δ as noise.
