# Spain: PISA 2025 versus 2022

The comparison is between assessment cycles, not publication years. OECD
released PISA 2025 on 8 September 2026. Access the student PUF through the
[official database](https://www.oecd.org/en/data/datasets/pisa-2025-database.html)
and complete its access form/terms before downloading. Raw and individual-level
processed data remain local and ignored by git; this update does not redistribute
them through GitHub or Hugging Face.

## Reproduce from the repository root

```bash
uv sync
uv run python Global/pisa/pipelines/download_from_oecd.py --years 2025 --file-types student_questionnaire
uv run python Global/pisa/pipelines/extract_spain_microdata.py data/Global/pisa/raw/2022/student_questionnaire/CY08MSP_STU_QQQ.SAV --year 2022
uv run python Global/pisa/pipelines/extract_spain_microdata.py data/Global/pisa/raw/2025/student_questionnaire/CY09_MS_STU_PUF.sav --year 2025
OPENBLAS_NUM_THREADS=1 uv run python Global/pisa/analysis/spain_cycle_change.py
uv run python Global/pisa/analysis/build_spain_report.py data/Global/pisa/analysis/2025
uv run python Global/pisa/pipelines/merge_trend_cycles.py
uv run python -m unittest discover -s tests -v
```

The 2022 original SAV is required, not just the legacy harmonized file. Paths
are resolved against the repository root. Check the downloaded archive for the
actual SAV filename/case. The harmonizer's `process_year_data(2025)` produces
the individual legacy 2025 cycle file before `merge_trend_cycles.py` runs.
The report builder creates the canonical aggregate `artifact.json` and its
supporting Markdown. Package that artifact with the Data Analytics portable
report renderer for a self-contained HTML, or use its validated native reader.
The reviewed findings are also recorded in [RESULTS_2025.md](RESULTS_2025.md).

## Two separate data products

* `processed/analysis_ready/spain_2022_2025_full.parquet`: repeated cross-section
  with all original columns, 10 plausible values per subject, final weights,
  and 80 replicate weights; cycle-specific metadata preserve labels and SHA256.
  Different individuals are sampled in each year: this is not a student panel.
* `processed/trend_analysis/pisa_combined_2006_2025.parquet`: compact legacy
  international archive. Its score fields use PV1 and lack survey weights;
  **do not use its means for inference or as official PISA results**. The merge
  removes exact duplicated rows, checks country/school/student/year identity,
  and rejects conflicting duplicate identities. Historical coverage is only
  the cycles actually present, not every configured year.

The previous 2009/2012 files multiplied respondents. The old join used
student IDs without country/school context. The new harmonizer reads the
student questionnaire without an unnecessary cognitive-file join. Original
upstream files are not overwritten; the new merged archive deduplicates local
copies and records counts in its merge metadata.

## Statistical contract

* Weighted means independently for each of ten plausible values; Fay BRR
  sampling variance from all 80 replicates (`sum((rep-full)^2)/20`). Add Rubin
  imputation variance `(1+1/10) * variance(PV estimates)`.
* Cross-cycle sampling errors combined assuming independent samples. CSV
  change intervals **exclude scale-linking uncertainty** and are labelled as
  provisional, not complete official trend confidence intervals. Do not
  declare a subgroup's absolute decline significant from these intervals.
* Subgroup-versus-rest change contrasts account for within-cycle covariance
  by differencing each replicate/PV estimate. Common additive scale-linking
  error cancels in these contrasts. BH-adjusted p-values describe exploratory
  heterogeneity, not a confirmatory causal test.
* Publish subgroup estimates only with >=100 students and >=10 schools in
  both cycles. Suppress Catalonia separately following OECD's exclusion-rate
  warning, while retaining its students in national figures.
* HISCED codes differ between cycles. Harmonize to ISCED <=2, ISCED 3–4,
  ISCED >=5. Missing education/origin responses remain explicit categories.
* REGION codes also changed: harmonize the SPSS value labels, not numeric
  codes. For example, 72405 is Canary Islands in 2022 but Basque Country in
  2025. Preserve original REGION alongside the label-derived comparison field.
* Spain has no observed ST004D01T values in the 2025 PUF. Use MALE (1 male,
  0 female/other) and label the comparison male/non-male; the 2022 non-male
  category contains females only. Do not present this as an exact girls-only
  comparison across cycles.
* Five non-Spanish country PUFs suppress school IDs in 2025. The legacy merger
  permits missing school ID only when country/year/student ID is unambiguous;
  Spain's full extracts require all three respondent identity fields.
* ESCS quartiles are weighted within each cycle. They represent relative
  position, not fixed real income or a common absolute socioeconomic scale.
* Family support items compare identical questions/response categories:
  weekly or daily versus less frequent, with nonresponse reported separately.
  These are students' reports, not independently observed parenting practices.
  About 57% lack observed answers to these items in 2022 versus 11% in 2025;
  these include differences in questionnaire administration, not just refusal.
  Respondent-only comparisons are descriptive and can be selection-sensitive.
  Family response/nonresponse categories are not used in the full-population
  composition decomposition because their coverage is not comparable.
* Symmetric Kitagawa: composition = change in group share × average group
  score; within = average group share × change in group score. Exhaustive,
  mutually exclusive cells include missing values and pool cells <100.
  Their sum must equal the national change exactly. Point estimates only.
  Alternative partitions are **not additive**.
* Neither group membership nor decomposition identifies a cause. Within-group
  changes can still contain unmeasured composition, school/test changes,
  selection, or other confounding. Do not interpret origins as innate traits.

## Sources

* [PUF download index](https://webfs.oecd.org/pisa2022/index.html)
* [Spain country note](https://www.oecd.org/en/publications/pisa-2025-results-volume-i-country-notes_2d4ff9ea-en/spain_748275c0-en.html)
* [Reader's guide](https://www.oecd.org/en/publications/pisa-2025-results-volume-i_73451bc5-en/full-report/reader-s-guide_0364240f.html)
* [PISA analysis instructions](https://www.oecd.org/en/about/programmes/pisa/how-to-prepare-and-analyse-the-pisa-database.html)
