# Spain PISA 2025: reviewed findings, 8 September 2026

Assessment comparison: **2025 versus 2022**, using original OECD student PUFs,
final and 80 replicate weights, and all ten plausible values per subject.

| Subject | 2022 | 2025 | Difference |
|---|---:|---:|---:|
| Mathematics | 473.14 | 457.45 | -15.69 |
| Reading | 474.31 | 451.36 | -22.95 |
| Science | 484.53 | 477.13 | -7.41 |

## Findings

* Composition by male/non-male and immigrant background accounts for -0.71
  reading points; -22.24 points occur within these groups. Adding reported
  parental education changes the decomposition to -4.36 composition and
  -18.59 within. These are alternative descriptions, not causal effects.
* Highest within-cycle national ESCS quartile: reading -33.02 versus -15.07
  in the lowest quartile. The high-quartile within contribution is -7.91 points
  (34.45% of the total decline). Quartiles exclude missing ESCS when setting
  boundaries and are relative positions, not fixed income bands.
* High ESCS quartile × Comunitat Valenciana: reading -54.61 (456 sampled
  students in 2025); high quartile × Basque Country: -52.67 (533 students).
  Both contrasts versus the rest survive the exploratory BH adjustment over
  747 subgroup/domain comparisons.
* Native-background × high ESCS quartile: reading -32.30, with 6,825 students
  in 2025; within contribution -7.17 points. This overlaps with the other
  partitions: **never sum demographic and geographic contributions**.
* Overall regional reading changes: Comunitat Valenciana -58.24; Basque
  Country -47.18. Their combined within contribution is -8.54 points, or
  37.20% of the national decline. Catalonia is not separately reported in
  accordance with OECD's exclusion warning, but remains in national means.
* Weekly discussion of school problems among family-item respondents falls
  from 60.35% to 50.49%. Questionnaire coverage differs substantially; in the
  2022 original, 14,624 of Spain's 30,800 records have code 97 (not applicable)
  for ST300Q05JA. This is not evidence of parental disengagement among those
  without an observed answer, nor an identified cause of score changes.

## What not to conclude

There is no causal attribution to immigration, parenting, language policy, or
any other policy. The principal pattern is deterioration inside comparable
observed groups, especially high relative SES in reading. Reported parental
education and questionnaire nonresponse show sizeable distribution changes,
so the education-based composition estimate is measurement-sensitive.

Science is especially uncertain: including the guide's 2.9-point linking
error gives an approximate trend interval [-14.90, +0.08]. The saved raw change
intervals explicitly exclude linking uncertainty; they are not complete
official significance tests. Group-versus-rest trend tests cancel a common
additive link error and use BH multiplicity adjustment.

## Data and validation receipt

* Spain 2022: 30,800 respondents; Spain 2025 PUF: 29,966 respondents, 956
  schools. OECD's note lists 29,967; the reason for the one-record discrepancy
  is unresolved. Rounded PUF means match the official 2025 publication.
* Historical merge: 3,895,685 respondents over 2006, 2009, 2012, 2015, 2018,
  2022 and 2025. Removed 46,312,312 exact repeated legacy rows; conflicting
  identities fail rather than being arbitrarily deduplicated.
* The historical archive is PV1-only and unweighted. It is not used for these
  inferences. Full Spain repeated-cross-section data preserve every original
  variable and cycle metadata for further questions.
* Reconciled each exhaustive composition + within decomposition to the
  national difference; regression tests cover weights, BRR/imputation,
  identity conflicts, missing school IDs, education/region recoding, and the
  2025 male/other indicator. Threshold: 100 students and 10 schools per cycle.
* Raw and individual-level processed data remain local and git-ignored. No
  new microdata were published to GitHub or Hugging Face.

See [methodology and commands](README_2025.md),
[analysis](spain_cycle_change.py), and [reviewed report builder](build_spain_report.py).
The report builder is snapshot-specific and rejects a changed headline or
comparison count pending narrative review.

Official references:
[database](https://www.oecd.org/en/data/datasets/pisa-2025-database.html),
[Spain note](https://www.oecd.org/en/publications/pisa-2025-results-volume-i-country-notes_2d4ff9ea-en/spain_748275c0-en.html),
[reader's guide](https://www.oecd.org/en/publications/pisa-2025-results-volume-i_73451bc5-en/full-report/reader-s-guide_0364240f.html).
