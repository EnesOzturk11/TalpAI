# Decision brief (generated; numbers are simulation output, not measurements)

## Board goals by decision (mean, min-max over seeds)

| decision | runs | goal_1* | goal_2* | goal_3 % complaining/wk [boot] | goal_3b [boot] | Δ goal_3b | goal_4 [boot] | Δ goal_4 | lost any week % [boot] | blame Kestrel wk8-10 % |
|---|---|---|---|---|---|---|---|---|---|---|
| nodecision | 2 | 94.66 (91.95-97.37) | 43.65 (38.24-49.06) | 3.05 [1.05-4.95] | -61.5 [-77.0--44.5] | – | 68.7 [46.34-91.28] | – | 23.5 [9.0-40.5] | 36.34 |
| decisions.json | 2 | 94.66 (91.95-97.37) | 58.48 (48.0-68.97) | 1.9 [0.85-2.95] | -48.5 [-63.5--33.0] | +13.00 | 90.94 [77.51-100.0] | +22.24 | 5.0 [0.0-11.0] | 11.0 |

Mean over seeds; [boot] = 95% bootstrap interval of that mean (500 draws, personas resampled within groups). *goal_1 and goal_2 are driven by world.json assumptions (action_effects), not persona behaviour: do not present them as simulation output. goal_3b is not calibrated to the +12 baseline: read the Δ.

## x25_base_s1 (nodecision, seed 1)

| group | n | lost at any week | week 10: flies / rebooked / moved / canceled | book again: yes / no | said stay, then left |
|---|---|---|---|---|---|
| business travelers | 5 | 40% [12-77] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 40% [12-77] / 20% [4-62] | 40% [12-77] of 5 |
| families visiting relatives | 5 | 40% [12-77] | 60% [23-88] / 0% [0-43] / 20% [4-62] / 20% [4-62] | 40% [12-77] / 40% [12-77] | 40% [12-77] of 5 |
| students | 5 | 0% [0-43] | 80% [38-96] / 20% [4-62] / 0% [0-43] / 0% [0-43] | 20% [4-62] / 40% [12-77] | 0% [0-43] of 5 |
| travel agencies | 5 | 20% [4-62] | 80% [38-96] / 0% [0-43] / 20% [4-62] / 0% [0-43] | 40% [12-77] / 20% [4-62] | 20% [4-62] of 5 |
| vacationers | 5 | 20% [4-62] | 80% [38-96] / 0% [0-43] / 0% [0-43] / 20% [4-62] | 60% [23-88] / 20% [4-62] | 20% [4-62] of 5 |
| ALL | 25 | 26% [12-48] | 75% [53-89] / 3% [0-21] / 9% [2-29] / 13% [4-34] | 43% [24-64] / 30% [14-52] | 26% [12-48] of 25 |

## x25_base_s2 (nodecision, seed 2)

| group | n | lost at any week | week 10: flies / rebooked / moved / canceled | book again: yes / no | said stay, then left |
|---|---|---|---|---|---|
| business travelers | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 80% [38-96] / 0% [0-43] | 0% [0-43] of 5 |
| families visiting relatives | 5 | 20% [4-62] | 80% [38-96] / 0% [0-43] / 0% [0-43] / 20% [4-62] | 60% [23-88] / 20% [4-62] | 20% [4-62] of 5 |
| students | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 100% [57-100] / 0% [0-43] | 0% [0-43] of 5 |
| travel agencies | 5 | 20% [4-62] | 80% [38-96] / 0% [0-43] / 20% [4-62] / 0% [0-43] | 60% [23-88] / 20% [4-62] | 20% [4-62] of 5 |
| vacationers | 5 | 40% [12-77] | 80% [38-96] / 0% [0-43] / 20% [4-62] / 0% [0-43] | 60% [23-88] / 20% [4-62] | 40% [12-77] of 5 |
| ALL | 25 | 21% [9-43] | 85% [64-95] / 0% [0-16] / 8% [2-28] / 7% [2-26] | 68% [46-84] / 15% [5-36] | 21% [9-43] of 25 |

## x25_A_s1 (plan, seed 1)

| group | n | lost at any week | week 10: flies / rebooked / moved / canceled | book again: yes / no | said stay, then left |
|---|---|---|---|---|---|
| business travelers | 5 | 20% [4-62] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 60% [23-88] / 0% [0-43] | 20% [4-62] of 5 |
| families visiting relatives | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 80% [38-96] / 0% [0-43] | 0% [0-43] of 5 |
| students | 5 | 0% [0-43] | 80% [38-96] / 20% [4-62] / 0% [0-43] / 0% [0-43] | 20% [4-62] / 0% [0-43] | 0% [0-43] of 5 |
| travel agencies | 5 | 20% [4-62] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 60% [23-88] / 20% [4-62] | 20% [4-62] of 5 |
| vacationers | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 80% [38-96] / 0% [0-43] | 0% [0-43] of 5 |
| ALL | 25 | 4% [1-22] | 97% [79-100] / 3% [0-21] / 0% [0-16] / 0% [0-16] | 67% [45-83] / 2% [0-20] | 4% [1-22] of 25 |

## x25_A_s2 (plan, seed 2)

| group | n | lost at any week | week 10: flies / rebooked / moved / canceled | book again: yes / no | said stay, then left |
|---|---|---|---|---|---|
| business travelers | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 80% [38-96] / 0% [0-43] | 0% [0-43] of 5 |
| families visiting relatives | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 80% [38-96] / 0% [0-43] | 0% [0-43] of 5 |
| students | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 60% [23-88] / 0% [0-43] | 0% [0-43] of 5 |
| travel agencies | 5 | 0% [0-43] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 60% [23-88] / 0% [0-43] | 0% [0-43] of 5 |
| vacationers | 5 | 20% [4-62] | 100% [57-100] / 0% [0-43] / 0% [0-43] / 0% [0-43] | 60% [23-88] / 20% [4-62] | 20% [4-62] of 5 |
| ALL | 25 | 6% [1-25] | 100% [84-100] / 0% [0-16] / 0% [0-16] / 0% [0-16] | 69% [47-85] / 6% [1-25] | 6% [1-25] of 25 |

Shares are weighted by world.json customer_mix (team assumption). Brackets: 95% Wilson interval on the effective sample size. With few personas per group, intervals are wide: treat group differences as hypotheses unless they hold across seeds.
