# TEAM_DOC

## Personas and why those attributes
- **25 personas** in `code/personas/*.md`, 5 per group: families visiting relatives, vacationers, students, business travelers and travel agencies. Each persona is one Markdown file.
- **Fields follow the case's attribute catalog** (03-audience-attributes.md, sections A-H plus J for Kestrel Air).
- **We kept the attributes that change what a passenger does when a flight goes wrong:**
  - anger speed;
  - patience;
  - tolerance for uncertainty;
  - knowing refund rights;
  - rivals used;
  - date flexibility;
  - news sources, which decide who hears a surprise;
  - trip weeks.
- **25 more personas (06-10 per group) stay switched off** with an `<!-- OFF -->` comment. We switched 12 of them on in memory, never on disk, for the week-5 engine study (see Experiments).
- **One shared prompt** (`code/prompts.json`), with a per-persona `custom` section.
- **Weights:** each group's share of passengers in `world.json` `customer_mix` (a team assumption), split evenly over that group's personas.

## The world
- `code/world.json` holds the calendar, normal rates, the known crisis, the surprises (word for word), the effect of each action and the CFO costs.
- A seeded world RNG draws each persona's flight outcome at its real probability. Gemini (gemini-3.5-flash-lite, temperature 1, seeded) decides only what the persona does, says, and whether they would book again.
- Personas also talk to each other: weekly chats are in `chats.jsonl`.


## Metrics: what the personas decide and what we assumed

The simulation has two layers. Read every board goal with the layer it comes from.

| Goal | Comes from | How to read it |
|---|---|---|
| goal_1 flights operated | **world.json assumptions** | The seeded world draws cancellations from fixed rates (`normal`, `known_crisis`) and multiplies them by `action_effects` (for example backup ground handling: strike-day cancellations x0.35). Strike days are excluded and the normal cancellation rate is 2%. In the final runs the week-4 engine grounding (10% cancellations in weeks 4-5) brings goal_1 to about 90-92.
- **Limit:** this goal_1 is a persona-flight sample. About 33 flights per run, so 3-4 engine cancellations weigh 10%.
- **Board figure:** the board's goal is fleet-level. 3 of 36 aircraft × 2 of 10 weeks ≈ 1.7% of flights, so about 98.3% operated; our fleet model on branch personas-v2 gave 98.31. We report that figure to the board and leave `metrics.json` goal_1 unchanged; its `units` text explains this.
- **The grounding is fixed.** It falls in weeks 4-5, and no later decision changes it.
- **An extended strike would count.** If the strike runs to Dec 24, that day is not excluded, and backup crews keep its flights running (severe runs). Not simulation output; not presented to the board as such. |
| goal_2 rebooked within 24h | **world.json assumptions** | `rebook24` is drawn from a fixed rate plus `rebook24_add` (partner airline +0.2, extra staff +0.1), over about 6 disrupted flights per run. The 77% for partner/staff is that assumption, not persona behaviour. Not presented as simulation output. |
| goal_3 complaints | personas | Share of passengers (weighted) who complain in an average week. The pre-strike baseline (nodecision_1 weeks 1-7) has no complaints, so there is nothing to scale to the dossier's 2,500/month; we report the share and compare runs. Not in the memo as a monthly count. |
| goal_3b NPS proxy | personas | From the end check-in (3a). Personas are not calibrated to the +12 baseline (a run with no disruption still scores about -36), so we report the **difference from nodecision**, not the level. |
| goal_4 revenue weeks 5-10 | personas + world | Fare revenue of personas who stay on Kestrel. Who leaves is persona behaviour; whose flight is canceled is the world draw. Reported as the difference from nodecision. |

Actions with **no** world effect on cancellations or rebooking (hotel rooms, free changes, goodwill, double points) change only what the passenger is told and offered. Any difference they make is pure persona behaviour, which makes them the cleanest test of the simulation.

Persona weights: each group's share of passengers in `world.json` `customer_mix` (team assumption; no public split exists), split evenly over that group's personas. Intervals use the effective sample size (Kish).

## How we read each crisis

**Week-4 update, "three aircraft grounded"** (text word for word in `world.json`): 3 of 36 aircraft out for about 2 weeks means about 8% of flights canceled or merged in weeks 4-5. We model it as cancellations ×5 on the normal 2% (10%), delays ×1.3, weeks 4-5, all airports. The week-3 precaution now affects week 3 only. A leased aircraft multiplies cancellations by 0.8 while it is in force.


**Known: ground handling strike, week 8 (Dec 22-23).** Read as SEVERE (team assumption, research section 2: walkouts with dozens of cancellations a day): 60% of week-8 flights fall on strike days; there cancellations 30%, 3h+ delays 45%, new seat within 24h 40%. A mild reading (Charlotte 2024: a few % late) is kept in `world.json` for comparison.

**Surprise, week 3: "The engine inspection"** (announcement text pasted word for word into `world.json` `surprises`). Two readings, both assumptions:
- SEVERE (as written): 75% of passengers hear it, 95% of those afraid of flying or getting news from TikTok/Instagram (the video is on TikTok); cancellations x1.5 and 3h+ delays x2 for weeks 3-4.
- MILD: 50% hear it; cancellations x1.1, delays x1.3, week 3 only.

Result, 4 runs (2 readings x 2 seeds, 25 personas, no decision) against the same personas without the surprise: behaviour did not change in weeks 3-6 (0-2 of 25 personas lost, as without it); blaming Kestrel rose slightly (weeks 3-6 average 2-6% vs 1-2%). Few personas fly in weeks 3-4 (4 of 25), so the operational hit reaches almost no one. We did not spend a decision on it. The surprise stays on in the hand-in runs and off in `plan_nosurprises`.

## Problems we hit and how we solved them
- **The dashboard accepts one action per decision.** Our earlier multi-action packages (A, B, C) stayed exploration. We re-tested four one-action pairs and chose free changes (week 7) plus backup ground handling (week 8).
- **Importance sampling hid backup and lease from the personas** in our second pipeline (branch personas-v2). It drew a cancellation at least 60% of the time on crisis days and let actions change only the weights. Backup crews and a leased aircraft therefore never changed what a persona lived through, and that pipeline picked hotels over backup (identical strike-stratum loss). This pipeline draws outcomes at their real probability. Here, backup beat hotels in both seeds (strike-day passengers lost 60%/6% vs 73%/22%) and also under an extended strike.
- **The week-7 message first said "Dec 21 and Dec 24 still have seats".** We do not know that, and Dec 24 is a strike day if the strike is extended. It now says the strike may be extended and that days before Dec 22 are the safest.
- **Persona-set difference read as seed noise.** We compared `q_base` (10 personas) with `x_base` (20 personas) and read goal_2 13→58 and goal_4 61→82 as noise between seeds, which made every single-action effect look like noise. The two runs had different personas, not just different seeds. With a fixed 20-persona set and two seeds (`x_base`, `x_base_s2`) the seed noise is small: goal_4 82→84, passengers lost 18.8%→16.3%. Rule since then: compare runs only within the same persona set.
- **Complaint scaling.** goal_3 was scaled so a run's own weeks 1-3 = 2,500 complaints/month; those weeks have no complaints, so one complaining persona became ~11,000/month. Now scaled against a shared pre-strike baseline, and reported as a plain weekly share when that baseline is zero (it is).
- **Persona count for the hand-in.** The 20-persona experiment set fails check.py (at least 24). The five hand-in runs need at least 24 personas.

## Reliability checks

**Test-retest** (`x25_base_s1` run twice, same seed, same personas, no decision): weekly status agrees in 97.6% of 250 persona-weeks; "would book again" in 90.4%; check-in answers identical in 83.2% of 400; the set of lost passengers has Jaccard 0.86 (one persona, stu03, differs). goal_4 69.29 vs 64.57: one persona moves revenue by ~5 points, so every comparison carries a bootstrap interval.

**Sanity: do personas read the world?**
- `x25_sanity_broken` (strike-day cancellations 0.9, new seat within 24h 0.1): weak test. Strike days were already 75% disrupted, so the same 13 flights were hit and only the mix of cancel/delay and the stranded count changed (6 → 9). Passengers lost 6 → 8 of 25; blame did not rise. This shows the patch was too narrow, not that personas ignore the world.
- `x25_sanity_broken2` (also normal days: cancellations 0.6, delays 0.3, new seat 0.1): 32 of 33 flights hit, 27 stranded. Passengers lost 6 → 18 of 25 (weighted 26% → 71%), canceled trips 13% → 38%, "would not book again" 30% → 62%, blaming Kestrel in weeks 8-10 45% → 75%, revenue weeks 5-10 69 → 25. Personas react strongly and in the expected direction when the world gets worse.

**Bootstrap intervals**: 500 draws, personas resampled with replacement within each group (group sizes, and so the customer-mix weights, stay fixed); one draw is shared by the seeds of a decision, and the interval is for the seed mean.

## Experiments
- `x_*`: 20 personas, seed 1, one action in one week each, against `x_base` (no decision). Report: `EXPERIMENT_single_actions.md`.
- `xA_s1/s2`, `xC_s1/s2` against `x_base`, `x_base_s2`: packages A and C over two seeds, to see whether differences survive a second seed.
- `x25_*` (25 personas = the hand-in set): `x25_base_s1/s2` vs `x25_A_s1/s2` (package A, surprises off) is the main comparison in the memo. The 20-persona `x_*` runs are the exploration round.
- `x_base_eng_sev/mild_s1/s2`: the engine-inspection surprise, two readings, no decision.
- `x25_eng_info_s1/s2`, `x25_eng_merge_s1/s2`: a week-4 text about the engine inspection, packaged with double loyalty points or with merging low-load flights (a message needs at least one action). Against `x_base_eng_sev_s1/s2`: no passenger lost in weeks 4-6 in any of the four runs (base: 0 and 1 of 25), blame weeks 4-6 3-11% vs 2-8%. Within the base intervals: no effect, so no decision spent on it. Seed-1 runs of both variants are identical, because no flight was disrupted in weeks 4-5, so both actions left the prompts unchanged: a free determinism check.
- Earlier runs not used for comparison: `q_*` (10 personas), `runs/_old/exp_1` (50 personas, gemini-3.7-flash, draft messages).
- **Final one-action pairs** (`k_nd`, `k_S2`, `k_S1`, seeds 1-2, 25 personas, engine update on). The hand-in plan_1/plan_2 are copies of `k_S1_s1/s2`, and nodecision_1/2 are copies of `k_nd_s1/s2` (`copied_from` in run.json). plan_nosurprises is S1 with seed 3. Seeds 1 / 2:

| run | goal_4 | lost (holding a booking) % | strike-day passengers ever lost % | moved to a rival % |
|---|---|---|---|---|
| no decision | 70.1 / 74.0 | 31 / 18 | 73 / 50 | 8 / 3 |
| free w7 + hotel w8 | 68.5 / 88.6 | 33 / 10 | 73 / 22 | 8 / 2 |
| **free w7 + backup w8 (final)** | 72.4 / 98.4 | 28 / 2 | 60 / 6 | 0 / 0 |

- **Severe strike** (`k_sev_*`: strike-day cancellations 0.5, delays 0.6, 80% of week-8 flights on strike days, i.e. extended to Dec 24):
  - Backup and hotels tie on revenue (72.4 / 80.3) and loss (28 / 10).
  - Backup loses fewer strike-day passengers: 50 / 18 vs 54 / 29, and 77 / 36 with no decision.
  - So backup is at least as good as hotels in both scenarios.
- **Week-5 engine study** (`k5_*`, "w5panel" of 37 personas: the 25 plus 12 switched-off personas who fly in weeks 5-6, so 7 fly in week 5 and 12 in week 6; hotels in week 8 fixed):
  - **Cost of the week-4 update, no decision:** goal_1 98.7 to 92.0 / 94.3. Lost while holding a booking 11.9 to 17.1 and 4.4 to 18.4. Week 5-6 travelers themselves stayed 100% in every run; the loss comes from passengers who fly later.
  - **Week-5 answers vs the week-7 free-changes slot** (goal_4 / strike-day lost):
    - lease: 95.9 / 87.4 and 13 / 48;
    - free changes: 99.0 / 85.8 and 5 / 58;
    - double points: 95.9 / 93.2 and 13 / 48;
    - week-7 slot: 97.9 / 84.3 and 5 / 54.
  - None of them wins in both seeds, so the decision slot stays on the strike.

## What we would do with more time
- More seeds (5+) and a larger week-5 panel. The 300-persona pool in `personas/personas.jsonl` has 43 travelers in weeks 5-6.
- Targeting by booking date instead of "everyone".
- Calibrating the backup crews' effect and the strike cancel rates with Kestrel operations data.
