# Public-Sector Fragmentation and Economic Mobility: Landscape, Data Catalog, and Methodology Brief

Prepared for Sergio Marrero. Current as of June 21, 2026. This is background reading for the build. The instructions Claude Code executes against live in `docs/BUILD_SPEC.md`.

## TL;DR
- A state-level composite joining Unemployment Insurance (UI), SNAP, and WIOA on speed, fragmentation, and navigability is a genuine gap: every major existing source covers only one dimension or one program (Code for America scores benefits navigability but not UI/WIOA; EIG scores economic distress but not government performance; OMB/ACSI score federal agencies, not states), and none ties cross-program administrative performance to economic-mobility outcomes at the state level.
- The three anchor "speed" datasets are real, primary, state-level, and free: DOL ETA 9050 UI first-payment timeliness (monthly CSV back to 1997), USDA FNS SNAP Application Processing Timeliness (FY2024 posted March 17, 2026), and DOL WIOA performance (state plus a new 550+ local-board dashboard). The dashboard should lead with these raw metrics; the 0-100 index is a secondary, clearly caveated layer.
- The hardest methodological constraints are non-comparable metrics across programs and the correlation-not-causation problem. Follow EIG/County Health Rankings/OECD practice: percentile-rank normalization, transparent equal weighting for v1, published sensitivity analysis, and explicit language that the index measures administrative performance correlated with mobility, not a causal driver of it.

## Key Findings

1. **The gap is real and specific.** No existing product joins UI + SNAP + WIOA administrative performance at the state level and links it to mobility outcomes. The strongest adjacent works each stop short: Code for America scores benefits-application navigability (not UI timeliness or WIOA outcomes); EIG measures economic distress outcomes (not government performance); OMB/performance.gov and ACSI measure federal-agency customer experience (not states); GAO documents federal program fragmentation (not a state navigability metric for workers).

2. **Speed data is strong and primary.** All three anchor speed datasets exist at state granularity, are free, and have long histories. SNAP FY2024 APT ranges from 95.62% (Wisconsin) to 42.72% (Tennessee), a spread wide enough to anchor a real dashboard.

3. **Fragmentation is the least-standardized dimension** and is where the new analysis can add the most original value. Code for America's integrated-application counts are the best existing proxy, but there is no single dataset counting "how many separate systems must a worker touch." This must be partly hand-constructed.

4. **Navigability data is uneven:** strong third-party scoring (Code for America) and federal-agency satisfaction (ACSI, OMB trust dashboard) exist, but state-level customer-experience/satisfaction data for UI/SNAP/WIOA is largely absent. Take-up rates (SNAP PAI, UI recipiency) are the best available state-level navigability outcome proxies.

5. **Causal claims will not hold.** Administrative performance, take-up, and economic distress are all correlated with state wealth, politics, and capacity. The honest framing is descriptive and correlational.

## PART A: Landscape

**1. Herd & Moynihan, "Administrative Burden: Policymaking by Other Means" (Russell Sage Foundation, 2018), and the 2023 RSF Journal work.**
- Frame: administrative burdens are the frictions people face in encounters with the state, decomposed into learning costs (finding out a program exists and whether you qualify), compliance costs (paperwork, documentation, recertification), and psychological costs (stigma, stress, loss of autonomy). Central thesis: burdens are deliberate policy choices, not accidents, and fall hardest on the disadvantaged.
- Method: theoretical synthesis plus case studies. The book won the 2019 Brownlow, 2020 Academy of Management, and 2022 Herbert Simon book awards.
- Granularity: largely conceptual and program/jurisdiction-level, not a 50-state dataset. Their Medicaid take-up work (Herd, DeLeire, Harvey & Moynihan 2013, Public Administration Review) shows wide cross-state variation in burden and take-up, the empirical hook for a state index.
- Update: book static (2018); extended in the 2023 RSF Journal double issue (Vol. 9, Issues 4 and 5, September 2023, intro DOI 10.7758/RSF.2023.9.4.01, open access). Companion: "Fewer Burdens but Greater Inequality?" (ANNALS of the AAPSS, 2023, DOI 10.1177/00027162231198976).
- Gap it leaves: provides theoretical scaffolding (the three cost types map onto navigability) but no state-level operational scorecard.
- Landing pages: https://www.russellsage.org/publications/book/administrative-burden ; https://www.rsfjournal.org/content/9/4 ; https://www.rsfjournal.org/content/9/5 ; https://www.rsfjournal.org/content/rsfjss/9/4/1.full.pdf

**2. Code for America: Benefits Enrollment Field Guide and Safety Net Innovation Lab.**
- Measures: usability, accessibility, and integration of online safety-net benefits applications across all 50 states, DC, and Puerto Rico. Programs: MAGI Medicaid, SNAP, TANF, Child Care Assistance, WIC. Criteria: online availability, mobile responsiveness, time to completion, Spanish-language support, reading level, account-registration requirements, accessibility.
- Latest figures (2023 Field Guide): 77% of programs examined have online applications (up from 64% in 2019); of those, 2 of 3 can be filled out on a mobile phone. Integration: more than 30 states (the public site also states 35) have a single integrated application for three or more programs; 15 states offer four programs in one application (up from 12 in 2019); 5 states offer all five. Friction: nearly 70% of applications require burdensome account registrations; 52% of program websites are not easily accessed on a mobile phone. Oregon's integrated application now takes as little as 15 minutes (down from ~80 in 2019).
- Method: primary-source assessment of live applications; expanded criteria 2023 vs 2019. Granularity: state (plus DC, PR). Update: ~every four years (2019, 2023), incremental updates (last noted September 2025).
- Gap it fills/leaves: best existing navigability + integrated-application-count source, a primary feed for fragmentation and navigability sub-scores. Does NOT cover UI, WIOA, time-to-employment, or mobility outcomes, and is not a composite index.
- Landing: https://codeforamerica.org/explore/benefits-enrollment-field-guide/ ; https://codeforamerica.org/programs/social-safety-net/integrated-benefits/

**3. OMB / performance.gov Federal Customer Experience program (37 HISPs).**
- Measures: customer experience (satisfaction, trust, ease) for federal High Impact Service Providers. Governed by OMB Circular A-11 Section 280 (annual capacity assessments, post-transaction feedback, a standardized 5-point trust question, public reporting).
- Granularity: FEDERAL AGENCY/service, NOT state. Critical: cannot populate a state dashboard; belongs in the optional federal toggle only.
- Latest: 37 HISPs designated. FY2024 update: 63 of 71 designated services launched at least one post-transaction survey with an approved trust question; 49 of 71 report to the redesigned "Trust in Major Government Service Providers" dashboard.
- GAO critiques: GAO-25-107652 (OMB could not use HISP capacity assessments/action plans to assess actual progress; goals lacked quantifiable targets/timeframes). GAO-24-106632 (performance framework built but baseline data still in progress; two CX CAP goals covered 2022 to January 2025). Government Service Delivery Improvement Act enacted January 2025; next CAP goals due no later than February 2026.
- Landing: https://www.performance.gov/cx/ ; https://www.performance.gov/cx/hisps/ ; https://www.gao.gov/products/gao-25-107652 ; https://www.gao.gov/products/gao-24-106632 ; A-11 280: https://www.performance.gov/cx/assets/files/a11-280.pdf

**4. EIG Distressed Communities Index (DCI).**
- Measures: composite of economic distress. Seven equally-weighted indicators: no-high-school-diploma share, housing vacancy rate, prime-age (25-54) not working, poverty rate, median income ratio, 5-year employment change, 5-year business-establishment change.
- Method: each geography gets a 0-100 distress score = average percentile rank across the seven indicators (0 = most prosperous, 100 = most distressed); five quintile tiers. Sources: Census ACS 5-Year plus County and ZIP Code Business Patterns. 2025 vintage uses ACS 2019-2023 and newly excludes university-student populations from the poverty rate.
- Granularity: ZIP (~26,032 ZIPs), county (3,136), congressional district; aggregable to state. Update: annual since 2015.
- State findings (recent): Mississippi worst, then West Virginia, Louisiana, Kentucky, Alabama; distress concentrated in South, Southwest, Appalachia. Utah and Colorado lead on prosperity, then Massachusetts, Minnesota, New Hampshire. Verify exact shares against the vintage used.
- Limitations: excludes Puerto Rico and territories; excludes ZIPs under 500 residents and majority-student ZIPs; full ZIP/county dataset requires a free license with a .org/.edu/.gov email. This is the methodological model to emulate and a candidate mobility-outcome input.
- Landing: https://eig.org/dci-hub/ ; methodology PDF: https://eig.org/wp-content/uploads/2025/08/Distressed_Communities_Index_Methodology_2025.pdf

**5. Additional credible sources.**
- **GAO annual fragmentation/overlap/duplication reports.** Annual since 2011. 2025 report (GAO-25-107604, reissued May 13, 2025): 148 new actions across 43 topic areas; cumulative ~$725 billion in benefits. 2026 report (GAO-26-108505, May 12, 2026): 16th edition, cumulative ~$774.3 billion. Authoritative framing for "fragmentation is costly." Landing: https://www.gao.gov/duplication-cost-savings
- **UI recipiency (Minneapolis Fed / BPC / NELP).** Recipiency varies enormously by state, a strong navigability/take-up proxy. NELP (citing DOL ETA UI Chartbook): fewer than 9% of unemployed in Kentucky received UI in 2024 vs nearly 59% in Minnesota; national 27% in 2024 (Minneapolis Fed reports 29% for 2023). Sources: https://www.minneapolisfed.org/article/2025/how-unemployment-insurance-access-and-benefits-vary-by-state ; https://bipartisanpolicy.org/explainer/what-share-of-the-unemployed-receive-unemployment-insurance-context-trends-and-influences/ ; https://www.nelp.org/insights-research/boosting-economic-resilience-seven-ways-states-can-support-more-workers-with-unemployment-insurance/
- **Civilla (Project Re:form, Michigan) and Nava PBC.** Civilla's redesign of Michigan's DHS-1171 cut it from 40+ pages, ~18,000 words, 1,000+ questions to 18 pages, 3,904 words, 213 questions (80% complexity reduction), and reduced processing time ~45% ("nearly half the time"); average completeness rose from 72% to 94%. Canonical proof navigability is fixable without changing eligibility rules. (One secondary outlet cited 42%; primary framing is ~45%.) Landing: https://civilla.org/work/project-reform-case-study
- **Beeck Center (Georgetown) Digital Benefits Network.** Open "Digital Identity in Public Benefits" dataset, 158+ applications across six programs (SNAP, WIC, Medicaid/CHIP, TANF, UI, child care) by state, flags combined applications. Landing: https://beeckcenter.georgetown.edu/projects/digital-benefits-network/ ; https://digitalgovernmenthub.org/
- **ACSI Federal Government Study.** 0-100 federal citizen satisfaction. 2025 study (Nov 18, 2025; 6,914 surveys): 19-year high 70.4, up 1.0%; USDA and State led at 77, Treasury lowest at 63; website satisfaction (72) beats call centers (65). Federal-level only (benchmark and instrument model). Landing: https://theacsi.org/industries/government/
- **211/United Way, Pew, Brookings/Urban, federal "Life Experiences."** 211 needs/referral data could proxy navigation demand but is not a standardized 50-state public dataset (exploratory). Pew tracks trust in government. Urban's UI recipiency work is directly useful. The federal "Life Experiences" projects sit inside the OMB CX program (federal, not state). Context, not core feeds.

## PART B: Data Source Catalog

**B1. DOL ETA 9050: First Payment Time Lapse (UI).** Dimension: SPEED.
- Agency: DOL Employment and Training Administration (Office of Unemployment Insurance).
- Measures: share of UI first payments made within 7/14/21 days and within 35 days of the first compensable week. Federal Secretary's Standard: 87% of intrastate first payments within 14/21 days, 93% within 35 days.
- Download: https://oui.doleta.gov/unemploy/DataDownloads.asp (ETA 9050 raw, comma-delimited CSV). Report builder: https://oui.doleta.gov/unemploy/btq.asp . Definitions: ETA Handbook 401.
- Granularity: state (50 + DC + PR + VI). Frequency: monthly (refreshed every morning). History: 1997 to current. Format: CSV. Limitations: states can edit historical data at any time (not frozen); measures payment promptness, not application-to-decision time; partial/workshare payments separate.

**B2. USDA FNS SNAP Application Processing Timeliness (APT).** Dimension: SPEED (and navigability outcome).
- Agency: USDA Food and Nutrition Service (becoming Food and Nutrition Administration June 1, 2026).
- Measures: percentage of applications processed timely, within 30 days (regular) or 7 days (expedited), from the SNAP Quality Control active-case sample. Corrective-action trigger: if the upper bound of the 95% CI around a state's APT is below 90%, the state must take corrective action.
- Download/per-state tables: https://www.fns.usda.gov/snap/qc/timeliness (landing); FY2024 table: https://www.fns.usda.gov/snap/qc/timeliness/apt-fy24 (posted/updated March 17, 2026). Recertification: /rpt-fy24.
- FY2024 state APT (full ordering, anchor for the dashboard and the scrape verification): Wisconsin 95.62, Illinois 93.56, Rhode Island 93.52, Nevada 93.09, Alabama 93.02, Ohio 91.93, Maryland 91.04, Idaho 91.02, Wyoming 90.43, Washington 90.36, Arizona 90.29, Pennsylvania 90.29, Utah 89.82, New Hampshire 89.32, Connecticut 89.11, Nebraska 88.96, Oklahoma 88.65, Kentucky 87.38, Louisiana 87.08, South Dakota 85.89, Massachusetts 85.45, Vermont 84.47, North Carolina 84.40, Virginia 83.23, Kansas 81.99, New York 81.61, Minnesota 80.37, California 80.21, Indiana 80.04, Mississippi 79.38, Missouri 78.28, U.S. Virgin Islands 77.63, New Jersey 77.61, Michigan 76.05, West Virginia 75.80, Texas 75.48, Delaware 75.08, South Carolina 73.48, Oregon 71.83, Hawaii 68.87, Georgia 67.22, Montana 66.88, Colorado 66.87, Maine 64.93, Iowa 64.66, Florida 63.31, Arkansas 61.94, Alaska 57.93, North Dakota 57.02, DC 56.73, New Mexico 52.36, Guam 50.86, Tennessee 42.72.
- Granularity: state. Frequency: quarterly (rolling 6-month average, ~4-month lag) and annual. Latest: FY2024. Format: HTML tables (no clean CSV/API; scrape or manual capture). Limitations: QC-sample-based; excludes backlog and cases pended for missing verification; applicant-caused delays can be coded untimely; "not a strict measure of regulatory compliance" per FNS. Puerto Rico runs a separate nutrition block grant.

**B3. DOL WIOA State Performance + Local Board Dashboard.** Dimension: SPEED-of-employment + navigability outcome.
- Agency: DOL ETA.
- Measures (six WIOA core indicators): employment rate Q2 after exit, employment rate Q4 after exit, median earnings Q2 after exit, credential attainment rate, measurable skill gains, effectiveness in serving employers. Reported via ETA-9169.
- PY2023 national headline (PY July 1, 2023 to June 30, 2024): Title I Adult: Q2 employment 74.1%, Q4 73.4%, median earnings $8,677, credential 72.2%, MSG 71.2%. Title I Dislocated Worker: Q2 70.7%, Q4 71.4%, median $9,397, credential 73.5%, MSG 70.4%.
- VINTAGE CAVEAT: the live "Results At-A-Glance" page now serves PY2024, not PY2023. PY2023 must be pulled from the PY2023 PDF/Excel or Data Book. (PY2024 live-page figures, for reference, Adult: Q2 72.2%, Q4 72.3%, median $8,754, credential 73.6%, MSG 74.0%; Dislocated Worker: Q2 69.0%, Q4 70.5%, median $9,897, credential 75.1%, MSG 72.4%.)
- Download: At-A-Glance: https://www.dol.gov/agencies/eta/performance/wioa-performance ; PY2023 National Performance Summary (PDF): https://www.dol.gov/sites/dolgov/files/ETA/Performance/pdfs/PY2023/PY%202023%20WIOA%20National%20Performance%20Summary.pdf ; PY2023 Annual Report Accessible File (Excel): https://www.dol.gov/sites/dolgov/files/ETA/Performance/pdfs/PY2023/PY2023%20Annual%20Report%20Accessible%20File.xlsx ; Performance Data Archive: https://www.dol.gov/agencies/eta/performance/results-archive
- Local board dashboard: https://www.dol.gov/sites/dolgov/files/ETA/Performance/PY2023_WIOA_Local_Board_Annual_Report.html (launched August 13, 2025, release ETA 25-1271-NAT; 550+ local boards; PY2023; filterable by state or board; downloadable accessible version at the bottom).
- Granularity: state AND local board (~550+) AND public-use microdata (PIRL). Frequency: annual (program year). Format: PDF + Excel + HTML dashboard + microdata. Limitations: exit-based lagged cohorts; self-reported with data-validation variation; At-A-Glance vintage shifts each year.

**B4. OMB performance.gov CX / HISP Trust dashboard.** Dimension: NAVIGABILITY (federal toggle only). Federal agency/service granularity, not state. Web dashboard. Place in optional federal toggle, never the state dashboard. Landing: https://www.performance.gov/cx/

**B5. EIG DCI.** Dimension: mobility OUTCOME (dependent variable, not a performance input). Download: https://eig.org/dci-hub/ (interactive) plus licensed Excel (free, .org/.edu/.gov email). Granularity: ZIP/county/CD, aggregable to state. Keep DCI OUT of the composite to avoid circularity; use as benchmark/correlate.

**B6. SNAP Program Access Index (PAI) and participation rates by state.** Dimension: NAVIGABILITY/take-up OUTCOME. PAI = ratio of average monthly participants to people below 125% of poverty, by state. Landing: https://www.fns.usda.gov/snap/qc/pai ; https://www.fns.usda.gov/research/snap/state-participation-rates . State; annual (no 2020). PDF tables. PAI denominator is a poverty proxy, not true eligibility, so values can exceed 1.0.

**B7. UI recipiency rate by state.** Dimension: NAVIGABILITY/take-up OUTCOME. DOL ETA UI Chartbook: https://oui.doleta.gov/unemploy/chartbook.asp (recipiency at /Chartbook/a13.asp). State; monthly/annual moving averages. Denominator is total unemployed, so it conflates eligibility policy with administrative access.

**B8. Census ACS context variables.** Dimension: context/control. data.census.gov / API. Internet/broadband, language isolation, disability, vehicle access, educational attainment, prime-age employment. State to tract; annual. API + CSV. Controls, not performance scores.

**B9. Beeck Center Digital Identity dataset.** Dimension: FRAGMENTATION + NAVIGABILITY. 158+ applications across six programs by state; flags combined applications and identity-proofing. Landing: https://beeckcenter.georgetown.edu/projects/digital-benefits-network/

**B10. 211/United Way and state digital-service benchmarks.** Dimension: NAVIGABILITY (exploratory). Not standardized 50-state public data. Manual/exploratory.

## PART C: Methodology Guidance

**Architecture.** Lead with the dashboard (raw, sortable state metrics with units and source/vintage labels). Offer the 0-100 composite as a secondary toggle. Matches EIG and County Health Rankings (both expose underlying measures, not just the headline).

**Normalization** (OECD/JRC Handbook on Constructing Composite Indicators, 2008): min-max (intuitive, bounded, outlier-sensitive); z-score (handles spread, unbounded, assumes normality); percentile rank (robust to outliers/skew, directly interpretable, EIG's choice). Recommendation: percentile rank for the composite, raw values in the dashboard.

**Weighting.** Equal weighting (EIG) is the most defensible v1 default: transparent, communicable. Expert/theory weighting (County Health Rankings: 30/20/10/40) encodes domain knowledge but invites scrutiny. PCA is opaque and unstable with 50 units. Recommendation: equal weighting within and across the three sub-scores for v1, plus a published sensitivity analysis showing rank movement under alternatives (OECD treats uncertainty/sensitivity analysis as required; ±20% weight perturbation is standard).

**Sub-scores.**
- SPEED: percentile-rank and average UI first-payment timeliness (% within 14/21 days), SNAP APT (% timely), and WIOA Q2-after-exit employment. All are "percent good," direction consistent.
- FRAGMENTATION (most original, least off-the-shelf): combine Code for America integrated-application count, Beeck DBN combined-application flags, and a hand-coded count of distinct intake systems a worker touches across UI + SNAP + WIOA. Document hand-coding rules explicitly; reviewers probe hardest here.
- NAVIGABILITY: combine Code for America usability/accessibility metrics with take-up outcomes (SNAP PAI, UI recipiency) as revealed-preference proxies. Take-up also reflects eligibility policy; label carefully.

**Missing data / non-comparable metrics.** Puerto Rico/territories: EIG excludes them and SNAP runs a PR block grant, so v1 = 50 states + DC, territories shown in the dashboard where data exists but excluded from the composite. Percentile-rank solves unit comparability; never average raw percentages across programs. Show gaps rather than impute silently; if imputing, document the method and flag imputed cells. Surface confidence intervals (SNAP APT ships a 95% CI) so single-year ranks are not over-read.

**Sub-state for v2.** WIOA supports it now (550+ local-board dashboard, PY2023). SNAP is harder: APT is state-level; sub-state exists only in county-administered states; no uniform national county file. UI is state-level with essentially no sub-state breakdown. Keep v1 state-level; build v2 sub-state only for WIOA boards and county-administered SNAP, and state explicitly that UI cannot be disaggregated.

**Correlation, not causation.** Administrative performance, take-up, and distress all co-vary with state income, politics, and capacity. The index measures performance correlated with mobility; it cannot show administration causes mobility. Adopt the EIG/County Health Rankings framing: the index directs attention and highlights variation, a starting point for inquiry, not a causal verdict. Publish the composite's correlation with EIG DCI and median earnings as external-validity checks, but keep DCI out of the index to avoid circularity.

## Verification discipline (carry into the build)
- Pull every statistic from the primary source and label its exact vintage.
- Two live traps: the WIOA At-A-Glance page silently rolled from PY2023 to PY2024; FNS became the Food and Nutrition Administration (FNA) on June 1, 2026, so SNAP URLs may migrate from fns.usda.gov to fna.usda.gov.
- Figure discrepancies to resolve at build: Civilla processing-time gain ~45% (primary) vs 42% (secondary); UI national recipiency 27% (2024, NELP) vs 29% (2023, Minneapolis Fed); Code for America integration count "more than 30" vs "35" states. Re-verify against the exact published vintage used.
