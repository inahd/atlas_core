#import "../_shared/preamble.typ": compendium-preamble, title-page

#compendium-preamble(
  title: "Architecture and API Reference",
  subtitle: "Technical Reference",
  version: "1.0 — converted from markdown",
)

#title-page(
  title: "Architecture and API Reference",
  subtitle: "Kernel, npu_engine, route map, and field state pipeline",
  volume: "COHERENCE ATLAS · TECHNICAL REFERENCE",
  version: "1.0 · April 2026",
)

_Converted from `research/research_vedic_software_landscape.md`._

#pagebreak()

= Existing Vedic Science Software and App Landscape


== Scope, methods, and how ratings were assigned


This survey focuses on *Jyotish (Vedic astrology), Ayurveda, Yoga/Meditation, Vastu, and Indian classical music (raga)* software and apps, plus cross-cutting gaps, UX patterns, and technical implementation approaches. Sources were prioritized in this order: official vendor/product pages, app store listings (Apple App Store / Google Play), reputable technical documentation, and then practitioner discussions and reviews (forums, app reviews, and comparable “community” threads). Where official sources did not publish a specific detail (e.g., subscription price or exact update timestamp), it is explicitly marked as *unknown* or *not stated*.

Because “accuracy” in Vedic computation is partly a *standards problem* (ayanāṁśa choice, node type, house system, time zone/DST history, rounding defaults, etc.), computed results can differ while still being “correct” within a school. This is why many platforms expose *ayanāṁśa choices* and tools to compare them. citeturn34search1turn34search4

=== UI quality (1–5)

UI quality is an *opinionated usability score* based on: visual clarity, speed, learnability, navigation depth, customization discoverability, accessibility readiness, and whether the UI reflects modern platform conventions. The score does *not* rate “spiritual authenticity,” only product usability.

=== Computation accuracy

“Computation accuracy” is reported as:
- *Astronomy engine confidence*: whether the platform explicitly uses a high-precision ephemeris engine (e.g., Swiss Ephemeris and/or NASA/JPL ephemerides) and shows transparent settings.
- *Settings transparency*: whether ayanāṁśa, node mode (mean/true), time standard, time zone, and DST handling are clearly controllable/auditable.
- *Community-reported pitfalls*: systematic issues identified in reviews (e.g., divisional chart mismatches, DST/time zone confusion, data loss after updates).

Swiss Ephemeris is widely used by astrology software makers as a developer toolkit and is positioned as a high-precision ephemeris engine for integration into apps rather than a consumer product. citeturn30search4turn30search15

== Jyotish software and calculators


=== Desktop-focused “serious practitioner” tools


*Jagannatha Hora (JHora)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Windows desktop (often run via emulation/compatibility layers on other OSes; not native Mac/mobile). citeturn28search4turn32view0],
  [Cost], [Freeware. citeturn1view0turn28search4],
  [Primary features], [Very broad calculation coverage across charts, dashas, strengths, transits, etc.; highly configurable. citeturn27search0turn33view0],
  [Computation accuracy], [*High confidence for astronomy engine: JHora’s improvement notes explicitly reference Swiss Ephemeris integration and use of JPL DE431* ephemeris data for higher precision. citeturn2view0],
  [UI quality (1–5)], [*2/5* (powerful but visually dated; dense “Windows classic” style; many panes and toolbars). Screenshot shows high-density multi-panel UI. citeturn33view0],
  [What it does well], [Depth, breadth, and configurability; strong for research-style exploration. citeturn27search0turn33view0],
  [What it lacks], [Modern UX affordances (progressive disclosure, guided workflows); native mobile; collaborative/client workflow features (CRM, consent, sharing controls) are minimal. (Assessment)],
  [User base], [Heavy among *students/researchers and professional Jyotishis* due to breadth and price. citeturn27search0turn28search4],
  [Last updated], [*Version 8.0 released Jan 1, 2016* per release history. citeturn28search4],
  [Open source], [No (freeware; source not published as part of the product). (No official open-source repo for JHora itself; see “PyJHora” under gaps/tech.)],
)



*Kala Vedic Astrology Software (Kala)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Windows desktop. citeturn7view0],
  [Cost], [Listed price ~\USD 254.95 (USD), with licensing details on vendor site. citeturn7view0],
  [Primary features], [Extensive computation modules and reports; aimed at full-feature practice. citeturn8view0],
  [Computation accuracy], [Vendor explicitly states use of *Swiss Ephemeris* and emphasizes accuracy. citeturn8view0turn7view0],
  [UI quality (1–5)], [*3/5* (generally more structured than JHora, but still “classic desktop app” feel; depth can overwhelm). (Assessment)],
  [What it does well], [A professional, packaged workflow with broad feature coverage and “traditional technique” focus. citeturn8view0turn7view0],
  [What it lacks], [Modern cross-device experience; unclear public documentation for reproducible “audit trails” of settings (ayanāṁśa/node defaults per chart). (Assessment)],
  [User base], [Primarily *professional* and advanced students (price + breadth). citeturn7view0],
  [Last updated], [Vendor lists a current version/release date (Sept 4, 2023). citeturn7view0],
  [Open source], [No. citeturn7view0],
)



*Shri Jyoti Star (SJS)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Windows (SJS 10 requires Windows 10/11 via Microsoft Store; SJS 9 supports older Windows). citeturn12view0turn11view0],
  [Cost], [SJS 9 Pro new order: *\USD 318*. citeturn11view0],
  [Primary features], [Very feature-complete Jyotish platform with large atlas, analysis, reports, and many specialized tables/tools. citeturn12view0],
  [Computation accuracy], [Vendor claims strong “atlas accuracy”; frequent updates include ayanāṁśa handling notes and many computational tools. citeturn12view0turn15view0],
  [UI quality (1–5)], [*4/5* (powerful but more modern than many desktop peers; extensive customization; still complex). (Assessment)],
  [What it does well], [Strong “power-user” environment: custom yoga builder/search, export to doc formats, massive atlas emphasis, deep tables. citeturn12view0turn15view0],
  [What it lacks], [Microsoft Store paywall friction for some regions; subscription pricing not cleanly visible from vendor site alone; steep learning curve. citeturn14search2turn15view0],
  [User base], [Professionals + serious students; also supported by large training/video ecosystem. citeturn12view0turn15view0],
  [Last updated], [Vendor maintains a “Recent Updates” page listing versions up through *10.1.50.2* (date not stated on-page). citeturn15view0],
  [Offline capability], [Explicitly supports being *offline up to a month* (important for “field” work). citeturn12view0],
  [Open source], [No. citeturn12view0turn11view0],
)



*Parashara’s Light (GeoVision Software)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Windows + Mac. citeturn22search11turn22search15],
  [Cost], [*\USD 299 per OS license; dual license \USD 450*. citeturn22search11turn27search13],
  [Primary features], [Interactive charting, customizable screens, extensive reports; professional positioning. citeturn41search0turn41search5],
  [Computation accuracy], [Vendor documentation describes *Swiss Ephemeris* use and a defined “True Chitra Paksha” ayanāṁśa referencing Spica at 180°. citeturn6search2],
  [Time zone/DST handling], [PL9 “new features” explicitly mentions many changes in time zone & daylight saving dates and a “fully up to date ephemeris.” citeturn41search2],
  [UI quality (1–5)], [*4/5* (deep but relatively polished; customizable layout approach reduces “one-screen-fits-all” issues). (Assessment)],
  [What it does well], [Professional reporting and configurable UI; emphasizes up-to-date ephemeris + DST changes as part of PL9 improvements. citeturn41search2turn41search0],
  [What it lacks], [Public, machine-readable computation manifest (settings/basis) for easy third-party reproducibility is not clearly published. (Assessment)],
  [User base], [Professional + serious learners. citeturn41search5turn27search6],
  [Last updated], [Sold as *Parashara’s Light 9.0*; official pages don’t provide a clear timestamped changelog in the surveyed sources. citeturn27search13turn41search2],
  [Open source], [No. citeturn27search13turn22search11],
)



=== Mass-market and “consultation marketplace” Jyotish apps


*AstroSage Kundli: AI Astrology*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android (and typically iOS/web ecosystem; this profile focuses on Android listing data). citeturn31view0],
  [Cost], [Free download; ad-supported with paid services typical of “talk to astrologer” model. citeturn31view0],
  [Primary features], [Kundli generation + horoscopes + “AI astrology” positioning; large consultation marketplace footprint. citeturn31view0],
  [Computation accuracy], [*Not verifiable from listing*; accuracy depends on engine + settings transparency (not detailed in cited listing). (Assessment)],
  [UI quality (1–5)], [*3/5* (generally usable for consumer flows; can feel sales-led). (Assessment)],
  [What it does well], [Scale: millions of reviews and downloads indicate strong distribution and retention. citeturn31view0],
  [What it lacks], [Practitioner-grade reproducibility and auditability (settings manifest), and marketplace trust issues appear in negative reviews (e.g., complaints about monetization). citeturn31view0],
  [User base], [Predominantly *amateur/consumer*, plus marketplace astrologers. citeturn31view0],
  [Last updated], [AppBrain reports last update *Jan 30, 2026* (version 29.2). citeturn31view0],
  [Open source], [No. citeturn31view0],
)



=== “Kundli software” ecosystem (India-heavy desktop)


*Horosoft Professional Edition 5.0*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Windows (explicitly lists supported Windows versions and incompatibilities). citeturn39view0],
  [Cost], [“Starts @ 26000” and “US\USD 400” shown on the product page (currency formatting is ambiguous but indicates professional pricing tier). citeturn39view0],
  [Primary features], [45+ pre-designed worksheets across Nadi/Parashari/KP/Lal Kitab/transit/matchmaking/Jaimini; many reports. citeturn39view0],
  [Computation accuracy], [Not enough technical disclosure in cited page to assess ephemeris/time zone basis. (Assessment)],
  [UI quality (1–5)], [*3/5* (typical worksheet-driven professional desktop approach; likely efficient once learned). (Assessment)],
  [What it does well], [Structured worksheet workflows; broad technique coverage. citeturn39view0],
  [What it lacks], [Cross-platform + modern UI; unclear transparency on astronomical engine and time zone data provenance. (Assessment)],
  [User base], [Professional/office usage. citeturn39view0],
  [Last updated], [“Latest Version –” is stated but no date is provided in the cited view. citeturn39view0],
  [Open source], [No. citeturn39view0],
)



*Astrocomp Softwares (Kundli – 2025 series)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Desktop software (Windows implied by the category; explicit OS support not shown in cited snippet). citeturn40view0],
  [Cost], [*Rs. 5000/-* for “Kundli – 2025”. citeturn40view0],
  [Primary features], [Kundli generation and updates offered as “download update” packages. citeturn40view0],
  [Computation accuracy], [Not assessable from cited downloads page alone. (Assessment)],
  [UI quality (1–5)], [*2–3/5* (unknown; typical small-vendor desktop). (Assessment)],
  [What it does well], [Clear update packaging and versioning. citeturn40view0],
  [What it lacks], [Public technical transparency and cross-platform experience. (Assessment)],
  [User base], [Likely mixed amateur/professional in the India desktop market. (Assessment)],
  [Last updated], [Downloads page lists *Version 5.6 updated 02/01/2026* for 2025 series. citeturn40view0],
  [Open source], [No. citeturn40view0],
)



=== Mobile “serious calculator” Jyotish apps


*Jyotish Dashboard™ (iOS)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iPhone/iPad (also runs on Mac with Apple silicon per listing compatibility). citeturn37view0],
  [Cost], [\USD 9.99. citeturn37view0],
  [Primary features], [Extensive divisional charts (D1–D60), multiple dashas (Vimshottari/Yogini/Chara), Panchang factors, broad ayanāṁśa list, mean/true Rahu options, sidereal+tropical modes, many house systems; credits time zone lookup to geonames.org. citeturn37view0],
  [Computation accuracy], [Explicitly advertises *Swiss Ephemeris* integration; time zone lookup dependency noted (geonames). citeturn37view0],
  [UI quality (1–5)], [*4/5* (feature-rich with modernish iOS structure, but complex). (Assessment)],
  [What it does well], [Strong settings surface for ayanāṁśa/node/house systems; breadth uncommon at \USD 9.99. citeturn37view0],
  [What it lacks], [Reliability risk: user review reports database loss and broken restore after an iOS 17 compatibility update. citeturn37view0],
  [User base], [Advanced students/pros who want a portable “calculator without interpretations,” plus explorers of mixed sidereal/tropical setups. citeturn37view0],
  [Last updated], [Version 3.3.1 dated *12/06/2023* in version history. citeturn37view0],
  [Open source], [No. citeturn37view0],
)



*Jyotish Computer (iOS)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iPhone/iPad. citeturn36view0],
  [Cost], [\USD 9.99. citeturn36view0],
  [Primary features], [Multiple chart styles, divisional charts up to D60, Vimshottari variants, nakshatra placements, chara karakas, arudhas, tithi/yoga/karana, map integration, ayanāṁśa choice with Chitra Paksha default. citeturn36view0],
  [Computation accuracy], [Mixed signals: reviews raise divisional chart correctness concerns and “traditional Hora chart” mismatch; developer response indicates limitations around time zone suggestion from maps. citeturn36view0],
  [UI quality (1–5)], [*4/5* (praised by reviewers as among the best Jyotish UIs, but feature depth is limited). citeturn36view0],
  [What it does well], [Modern iOS UI; compact; useful for “on the go” chart inspection. citeturn36view0],
  [What it lacks], [Automatic time zone inference (“when one chooses a place… timezone not suggested”), rich comparison views, and some varga accuracy trust. citeturn36view0],
  [User base], [Students and casual practitioners prioritizing UI over encyclopedic technique coverage. citeturn36view0],
  [Last updated], [Latest listed update in version history: *Aug 21, 2020*. citeturn36view0],
  [Open source], [No. citeturn36view0],
)



*JyotishApp – Astrology Jyotish (Android)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android. citeturn38view0],
  [Cost], [Free download; explicitly “NO ads” in AppBrain data. citeturn38view0],
  [Primary features], [Horoscope + Panchanga + Muhurta + Gochara + KP + Matching + PDF support; explicitly “NO PREDICTION.” citeturn38view0],
  [Computation accuracy], [Not fully auditable from listing; however the product positioning suggests calculator-first rather than content/prediction-first. citeturn38view0],
  [UI quality (1–5)], [*3/5* (highly functional; at least one review complains about UI). citeturn38view0],
  [What it does well], [Offline, lightweight, calculator-centered, avoids “prediction theater.” citeturn38view0],
  [What it lacks], [Some advanced dashas and UI conveniences requested in reviews (e.g., Kaal Chakra dasha, bulk data management, more languages). citeturn38view0],
  [User base], [Students + practitioners who want a *free offline calculation tool*. citeturn38view0],
  [Last updated], [AppBrain reports last update *Nov 17, 2025*. citeturn38view0],
  [Open source], [No. citeturn38view0],
)



=== Open-source Jyotish-capable software


*Maitreya (Maitreya8/Maitreya9 ecosystem)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Windows, macOS, Linux, BSD/UNIX (not mobile). citeturn30search3turn30search12],
  [Cost], [Free. citeturn30search3turn30search12],
  [Primary features], [Vedic + Western astrology, multiple chart styles, dashas, ashtakavarga/shadbala/yogas, transits/progressions, partner charts, ephemeris, eclipses. citeturn30search3],
  [Computation accuracy], [Strong transparency potential because code is available; specific ephemeris engine details are not stated in the short “feature overview” snippet, but compilation + options are documented in project docs. citeturn30search2turn30search20],
  [UI quality (1–5)], [*3/5* (varies by build; open-source desktop UI tends to be functional rather than polished). (Assessment)],
  [What it does well], [Open-source foundation enables verification, localization, and long-term maintainability beyond one vendor. citeturn30search12turn30search7],
  [What it lacks], [Mobile availability and commercial-grade onboarding/documentation polish. citeturn30search12],
  [User base], [Mixed: students, researchers, open-source oriented practitioners. (Assessment)],
  [Last updated], [GitHub lists *maitreya8-8.2 released Sep 30, 2025*. citeturn30search7],
  [Open source], [Yes (GNU GPL). citeturn30search12turn30search7],
)



=== Web calculators and utilities (Jyotish-adjacent)


*Drik Panchang (web)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn34search0],
  [Cost], [Free access (ads/monetization may exist; not assessed here). citeturn34search0],
  [Primary features], [Hindu almanac/calendar with festivals, eclipses, auspicious/inauspicious dates; used by astrologers/astronomers for panchang and horoscopic context. citeturn34search0],
  [Computation accuracy], [Not fully auditable from homepage snippet; widely used as an ephemeris/panchang reference. citeturn34search0],
  [UI quality (1–5)], [*3/5* (information-dense reference site). (Assessment)],
  [Last updated], [Not stated on cited page. citeturn34search0],
  [Open source], [No public indication. citeturn34search0],
)



*Astro-Seek Sidereal calculators*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn34search1turn34search18],
  [Cost], [Free. citeturn34search1turn34search18],
  [Primary features], [Ayanāṁśa calculator, sidereal chart calculators, varga tools. citeturn34search1turn34search18],
  [Computation accuracy], [Useful for comparing ayanāṁśas and settings; not positioned as a Jyotish lineage tool. citeturn34search1turn34search18],
  [UI quality (1–5)], [*3/5*. (Assessment)],
  [Open source], [No. citeturn34search1],
)



*Prokerala divisional chart tools*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn34search2],
  [Cost], [Free tools. citeturn34search2],
  [Primary features], [Free online divisional chart calculator guidance and generation. citeturn34search2],
  [Computation accuracy], [Not auditable from the cited high-level page; treat as a convenience tool. citeturn34search2],
  [UI quality (1–5)], [*3/5*. (Assessment)],
  [Open source], [No. citeturn34search2],
)



== Ayurveda apps and tools


=== Dosha/prakriti quizzes (consumer-facing)


*Ayurveda Dosha Quiz (Service-Plants)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android. citeturn18search0turn18search8],
  [Cost], [Free. citeturn18search0turn18search8],
  [Primary features], [Questionnaire to identify mind/body type (prakriti) with balancing tips. citeturn18search0],
  [Computation accuracy], [Typically rule-based quiz logic; without clinical validation details in the listing, treat outputs as educational. (Assessment)],
  [UI quality (1–5)], [*3/5* (simple quiz format). (Assessment)],
  [User base], [Mostly *amateurs/consumers*. citeturn18search0turn18search8],
  [Last updated], [AppBrain reports last update *Jan 4, 2024*. citeturn18search8],
  [Open source], [No. citeturn18search0],
)



*Ayurveda Dosha Quiz! (Lissa Coffey / Bamboo Entertainment)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iOS. citeturn43view0],
  [Cost], [Free. citeturn43view0],
  [Primary features], [24-question dosha quiz with educational framing. citeturn43view0],
  [Computation accuracy], [Quiz-based; no clinical validation disclosed in listing. (Assessment)],
  [UI quality (1–5)], [*2/5* (very old app footprint). (Assessment)],
  [User base], [Amateurs/consumers. citeturn43view0],
  [Last updated], [Version history shows last update *03/03/2016*. citeturn43view0],
  [Open source], [No. citeturn43view0],
)



=== Materia medica / herb + formulation databases (practitioner-friendly direction)


*Dravya – Ayurveda Database*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android app; companion web presence. citeturn42view0turn19search2],
  [Cost], [Free “Essential Pack,” with paid “Professional Pack” upgrade (in-app). citeturn42view0],
  [Primary features], [Referenced data on herbs/animal products/metals/minerals/gemstones/formulations; multilingual names; search and “multi-search”; includes contraindications/usage in paid tier. citeturn42view0],
  [Computation accuracy], [Not “computed” like astronomy; quality hinges on editorial sourcing. The listing emphasizes “authentic and referenced information,” but does not expose a public citation graph per entry in the snippet. citeturn42view0],
  [UI quality (1–5)], [*4/5* (search-centric “reference tool” pattern; users note it “transforms” when using search). citeturn42view0],
  [What it does well], [One of the clearest “serious Ayurveda community” database products; supports professional quick reference and multi-search filtering. citeturn42view0],
  [What it lacks], [Pricing transparency for paid tier in the public listing snippet; deeper scholarly apparatus (edition/versioning of classical text sources) isn’t visible in cited view. (Assessment)],
  [User base], [Students + vaidya community (explicitly targeted). citeturn42view0turn19search2],
  [Last updated], [Google Play lists *Jun 17, 2025*. citeturn42view0],
  [Open source], [No. citeturn42view0turn19search2],
)



*Government/Institutional knowledge bases (not “apps,” but foundational data)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn19search14],
  [Example], [Ministry of AYUSH “eCharak” knowledge resources describing a CCRAS-developed medicinal plant literature database (references/abstracts). citeturn19search14],
  [Gap relevance], [These resources are authoritative, but usually lack modern practitioner UX (fast mobile UI, offline sync, patient-safe summaries). citeturn19search14],
)



=== Dinacharya and lifestyle adherence tools


*Dinacharya (Aideals)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android. citeturn44view0],
  [Cost], [Free download with ads (per listing). citeturn44view0],
  [Primary features], [Prakriti assessment; “Ayurvedic clock” phases; tracks 19 daily practices; meal planning guidance; progress visualization. citeturn44view0],
  [Computation accuracy], [Mostly schedule/reminder logic + quiz logic; no validation disclosed. (Assessment)],
  [UI quality (1–5)], [*4/5* (structured tracker with clear program design). (Assessment)],
  [User base], [Consumers and lifestyle-focused students. citeturn44view0],
  [Last updated], [Google Play lists *Feb 24, 2026*. citeturn44view0],
  [Open source], [No. citeturn44view0],
)



*TrackMyDinacharya (AyurvedaSidhi web tracker)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn18search3],
  [Cost], [Not stated. citeturn18search3],
  [Primary features], [Dinacharya progress tracking and reminders framing. citeturn18search3],
  [Computation accuracy], [Not applicable.],
  [UI quality (1–5)], [*3/5* (web tool; unknown robustness). (Assessment)],
  [Last updated], [Not stated. citeturn18search3],
  [Open source], [Not stated. citeturn18search3],
)



=== Panchakarma guides (education-focused)


*Panchakarma Guide (BhadarApps)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android. citeturn45view0],
  [Cost], [Free; contains ads; explicitly claims offline usability. citeturn45view0],
  [Primary features], [Educational guide to Panchakarma and its five-fold therapy framing; voice reader feature. citeturn45view0],
  [Computation accuracy], [Not applicable (educational content).],
  [UI quality (1–5)], [*3/5* (utility guide). (Assessment)],
  [User base], [Consumers and early students. citeturn45view0],
  [Last updated], [Google Play lists *May 17, 2024*. citeturn45view0],
  [Open source], [No. citeturn45view0],
)



=== Pulse diagnosis systems (hardware + app ecosystems)


This segment is expanding quickly, often marketing “AI + Nadi Pariksha.” Most offerings are *device-dependent*, so “app-only” comparisons are incomplete.

*Nadiswara (pulse diagnosis device + app)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Hardware device + mobile app workflow. citeturn18search6],
  [Cost], [Not stated publicly (typical “contact sales”). citeturn18search6],
  [Primary features], [Captures pulse vibrations, uses AI-driven analysis, generates reports; maps results to dosha balances and wellness insights. citeturn18search6],
  [Computation accuracy], [Vendor claims increased accuracy and structured diagnosis; independent clinical validation details are not established in cited summary. citeturn18search6],
  [UI quality (1–5)], [*3/5* (unknown; depends on shipped app). (Assessment)],
  [User base], [Clinics, institutions, wellness centers. citeturn18search6],
  [Last updated], [Not stated. citeturn18search6],
  [Open source], [No. citeturn18search6],
)



*Nadifit (pulse diagnosis ecosystem)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Pulse diagnosis devices + app; also Google Play app listing exists. citeturn18search2turn18search17],
  [Cost], [Not stated in cited snippet. citeturn18search2turn18search17],
  [Primary features], [Nadi Pariksha tools positioned for clinical/professional use; marketing mentions high accuracy and large validation dataset claims. citeturn18search17turn18search2],
  [Computation accuracy], [Claims “validated with data from over 70,000 patients” (vendor claim; not independently verified here). citeturn18search17],
  [User base], [Practitioners/clinics. citeturn18search2turn18search17],
  [Last updated], [Not visible in the cited snippet. citeturn18search17],
  [Open source], [No. citeturn18search17],
)



== Yoga and meditation apps with Vedic content


This category is dominated by: (a) large “general wellness” platforms that include some Vedic-adjacent modalities (Yoga Nidra, Kundalini, mantra), and (b) lineage/organization apps (Isha, Art of Living). A key market reality: the biggest apps optimize for *habit formation + retention*, which can conflict with “serious practice progression” and cultural specificity.

=== Large wellness platforms


*Insight Timer*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iOS/Android. citeturn46view0turn20search12],
  [Cost], [Free with optional subscription (“MemberPlus”) and in-app purchases. citeturn46view0turn48search2],
  [Primary features], [Massive guided meditation library, timer, groups/community, Yoga Nidra, Kundalini Yoga, and even “Advaita Vedanta” content categories per Play listing. citeturn46view0turn20search12],
  [Vedic science included], [Yoga Nidra, Kundalini yoga, Advaita Vedanta content labels (breadth varies by teacher content). citeturn46view0turn20search12],
  [UI quality (1–5)], [*3/5* (feature-rich but can become bloated; reviews complain about discoverability and “too many features”). citeturn46view0],
  [What it does well], [Scale and variety: “100+ new” tracks daily and strong network effects. citeturn46view0],
  [What it lacks], [A coherent Vedic curriculum, lineage context, and consistent Sanskrit/mantra pedagogy (pronunciation, meaning, adhikara) across content. (Assessment)],
  [User base], [Mass-market (millions of downloads). citeturn46view0],
  [Last updated], [Google Play lists *Mar 13, 2026*. citeturn46view0],
  [Open source], [No. citeturn46view0],
)



*Glo*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iOS app + web; also supports multiple devices. citeturn47view0turn20search9],
  [Cost], [Official support page lists *\USD 30/month or \USD 245/year* (platform pricing may differ if purchased via Apple/Google). citeturn48search0],
  [Primary features], [Yoga, meditation, Pilates, fitness classes; downloads supported; strong filtering and personalization. citeturn47view0turn20search9],
  [Vedic science included], [Yoga modalities including Yoga Nidra style library exists. citeturn20search5turn47view0],
  [UI quality (1–5)], [*4/5* (generally polished; robust content filtering; some app-specific bugs reported). citeturn47view0],
  [What it does well], [“Studio-quality” instruction, class variety, offline downloads, strong ratings. citeturn47view0turn20search9],
  [What it lacks], [Often “yoga-as-fitness + mindfulness” framing more than traditional Vedic/yogic epistemology; Sanskrit/mantra depth depends on teacher and isn’t structurally guaranteed. (Assessment)],
  [User base], [Serious home practitioners and general wellness users. citeturn47view0turn48search0],
  [Last updated], [Not visible in cited snippet (App Store page shows reviews but not a clear latest update date in the excerpt). citeturn47view0],
  [Open source], [No. citeturn47view0],
)



*Down Dog (Yoga Buddhi Co.)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iOS/Android. citeturn49search1turn49search14],
  [Cost], [Subscription pricing is not clearly exposed on the main marketing page, but an App Store listing in the Down Dog ecosystem states memberships cost *\USD 9.99/month or \USD 59.99/year*. citeturn49search16turn49search0],
  [Primary features], [Algorithmically generates a new personalized practice each session; high customization. citeturn49search0turn49search1],
  [Vedic science included], [Yoga styles (including Ashtanga etc. mentioned in reviews elsewhere), but not explicitly “Vedic science” pedagogy by default. (Assessment)],
  [UI quality (1–5)], [*4/5* (customization-forward; generally strong UX reputation). citeturn49search0turn49search1],
  [What it does well], [High personalization and habit support (“different every time”). citeturn49search0turn49search1],
  [What it lacks], [Traditional context, mantra/Sanskrit instruction, and deeper sadhana progression mapping. (Assessment)],
  [User base], [Mass-market yoga practitioners. citeturn49search1turn49search14],
  [Last updated], [Not captured in cited Down Dog Yoga listing snippet; other Down Dog app listings show periodic updates (example: HIIT app snippet shows an “Updated on” field). citeturn49search10turn49search16],
  [Open source], [No. citeturn49search1],
)



=== Lineage/organization apps with stronger “Vedic” orientation


*Sadhguru – Yoga & Meditation (Isha Foundation)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android/iOS. citeturn21search4turn21search0],
  [Cost], [Free with in-app purchases. citeturn21search4turn21search12],
  [Primary features], [Isha Yoga practices, guided meditations, Sadhguru content; multi-language. citeturn21search4],
  [Vedic science included], [Yoga/meditation content tied to an Indian spiritual organization (not “Jyotish/Ayurveda,” but yogic practice framing). citeturn21search4turn21search0],
  [UI quality (1–5)], [*4/5* (large user base + high rating signals strong usability). citeturn21search4turn21search12],
  [User base], [Mass-market spiritual practitioners; very large Android footprint. citeturn21search4turn21search12],
  [Last updated], [AppBrain reports last update *Mar 12, 2026*. citeturn21search12],
  [Open source], [No. citeturn21search4],
)



*The Art of Living App*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Mobile app ecosystem (site provides app distribution pointers). citeturn21search5turn21search1],
  [Cost], [In-app purchases (site labels “In App Purchase”). citeturn21search5],
  [Primary features], [Yoga, meditation, Sudarshan Kriya offerings; organizational content. citeturn21search5turn21search13],
  [Vedic science included], [Breath practice tradition: Sudarshan Kriya is central to the org’s system. citeturn21search13turn21search5],
  [UI quality (1–5)], [*3/5* (unknown; not enough UI evidence in cited sources). (Assessment)],
  [Last updated], [Site shows a version string “26.02.026” but not a clear release date in cited snippet. citeturn21search5],
  [Open source], [No. citeturn21search5],
)



=== Mantra-oriented apps and what’s broken


*Meditate Om: Mantra Meditation (Panagola)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android. citeturn21search3],
  [Cost], [Free download (Google Play); ad-supported. citeturn21search3],
  [Primary features], [Meditation timer + mantra chanting helper; claims care for “accurate versions” of mantras. citeturn21search3],
  [Vedic science included], [Explicit Hindu & Buddhist mantra focus. citeturn21search3],
  [UI quality (1–5)], [*3/5* (simple utility). (Assessment)],
  [Last updated], [Not shown in cited snippet. citeturn21search3],
  [Open source], [No. citeturn21search3],
)



*Omvana (Mindvalley) — discontinued*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Previously iOS/Android. citeturn20search3turn20search15],
  [Status], [Official help center states Omvana is *discontinued, no longer available for download, and no longer supported with no future updates*. citeturn20search15],
  [Market meaning], [This is a canonical example of “well-loved wellness app risk”: acquisition/strategy shifts can strand user libraries and workflows. citeturn20search15],
)



== Vastu apps and “calculation” software


Vastu tooling trends fall into three clusters:
- *Compass + zoning overlays* (most common; easiest to ship)
- *Floor plan upload + automated scoring* (web-first)
- *Professional consultant platforms* (report generation, client delivery, sometimes astro-vastu mixing)

=== Compass + overlay apps


*Vastu Compass by AppliedVastu*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android. citeturn50view0],
  [Cost], [Free download. citeturn50view0],
  [Primary features], [Floor plan gridding; 16-zone/32-zone overlays; capture images; multiple compass modes (incl. “Vastu Purusha mandala” overlays). citeturn50view0],
  [Computation accuracy], [The listing explicitly states accuracy depends on *device settings and user procedure* and provides usage guidelines; therefore “accuracy” is as much operational as computational. citeturn50view0],
  [UI quality (1–5)], [*3/5* (feature-rich; reviews show both praise and frustration; some complain about redirects). citeturn50view0],
  [What it does well], [Makes zoning overlays accessible for consultants/architects; clear feature enumeration. citeturn50view0],
  [What it lacks], [Reliability and “free vs redirect-to-paid” clarity for some users (per reviews); calibration UX remains challenging. citeturn50view0],
  [User base], [Consumers + vastu consultants/architects/engineers. citeturn50view0],
  [Last updated], [Google Play lists *Aug 27, 2025*. citeturn50view0],
  [Open source], [No. citeturn50view0],
)



=== Floor plan upload calculators (web)


*SquareYards Vaastu Calculator*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn22search1],
  [Cost], [Free basic check (as positioned). citeturn22search1],
  [Primary features], [Upload floor plan, receive “Vastu compliance” assessment and suggestions; includes a score concept. citeturn22search1],
  [Computation accuracy], [Black box scoring; not auditable from landing page. (Assessment)],
  [UI quality (1–5)], [*3/5* (consumer-friendly). (Assessment)],
  [User base], [Consumers/homebuyers. citeturn22search1],
  [Last updated], [Not stated. citeturn22search1],
  [Open source], [No. citeturn22search1],
)



*AppliedVastu Vastu Calculator / Reports*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn22search5turn22search10],
  [Cost], [Free check entry points; professional consultancy upsell; report delivered via WhatsApp per description. citeturn22search5],
  [Primary features], [Upload floor plan; optional astro-vastu by entering birth details for occupants; generates PDF report. citeturn22search5turn22search10],
  [Computation accuracy], [Depends on correct orientation input + model assumptions; not transparent in cited snippet. (Assessment)],
  [UI quality (1–5)], [*3/5*. (Assessment)],
  [User base], [Consumers and consultant funnel. citeturn22search5turn22search10],
  [Last updated], [Not stated. citeturn22search5turn22search10],
  [Open source], [No. citeturn22search5turn22search10],
)



=== Professional “Vastu software” platforms


*Astro Vastu Pro*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Software platform (web/desktop not clearly specified on landing excerpt). citeturn22search2],
  [Cost], [Not stated. citeturn22search2],
  [Primary features], [“Unified software platform” for astro-vastu consulting, replacing manual workflows, professionalizing reporting. citeturn22search2],
  [Computation accuracy], [Vendor claims “accurate, system-driven workflows,” but no algorithmic transparency in cited snippet. citeturn22search2],
  [UI quality (1–5)], [*3/5* (unknown; likely consultant-focused). (Assessment)],
  [User base], [Professionals/consultants. citeturn22search2],
  [Last updated], [Not stated. citeturn22search2],
  [Open source], [No. citeturn22search2],
)



*Vastuteq*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Software (web/desktop not specified in excerpt). citeturn22search6],
  [Cost], [Not stated. citeturn22search6],
  [Primary features], [Simplifies complex Vastu principles; “accurate calculations and insightful reports.” citeturn22search6],
  [Computation accuracy], [Claimed by vendor but not verifiable from snippet. citeturn22search6],
  [User base], [Professional vastu consultants. citeturn22search6],
  [Open source], [No. citeturn22search6],
)



*Parashara Software “Vedic Vaastu”*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Desktop software (explicit Vastu product line from Parashara Software Pvt Ltd). citeturn22search3turn22search7],
  [Cost], [Listings show pricing tiers (e.g., *Rs. 5900/-* for a professional edition tier; other tiers listed). citeturn22search7],
  [Primary features], [Vastu grid methods, direction/tilt considerations, Aayadi calculation, scoring, map tools, printable worksheets per product menu text. citeturn22search3],
  [Last updated], [Not stated in cited snippet. citeturn22search3turn22search7],
  [Open source], [No. citeturn22search3turn22search7],
)



== Music and raga apps with Vedic framing


This landscape has strong *reference tools* and *practice accompaniment tools*, but comparatively weak consumer-grade *raga recognition* (“Shazam for raga”) and weak scientifically grounded “music therapy” UX.

=== Raga databases and learning tools


*Carnatic Raga*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iOS + Android. citeturn51view0turn23search1],
  [Cost], [Free. citeturn51view0turn23search1],
  [Primary features], [Database of 950+ ragas including Melakarta/Janya; search by swaras or name; arohanam/avarohanam; favorites; tala reference; plays scales. citeturn51view0turn23search4],
  [Computation accuracy], [Deterministic data lookup; “accuracy” hinges on correctness of raga database entries. Users praise organization. citeturn51view0],
  [UI quality (1–5)], [*4/5* (well-scoped learning utility). (Assessment)],
  [User base], [Learners and enthusiasts. citeturn51view0turn23search1],
  [Last updated], [iOS version history shows *4.0 on 03/07/2025*. citeturn51view0],
  [Open source], [No. citeturn51view0],
)



*iRaaga*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [iOS. citeturn23search12],
  [Cost], [Free. citeturn23search12],
  [Primary features], [Carnatic raaga explorer/player for 72 melakarthas, pitch control. citeturn23search12],
  [UI quality (1–5)], [*3/5* (small utility). (Assessment)],
  [Last updated], [Not visible in cited snippet. citeturn23search12],
  [Open source], [No. citeturn23search12],
)



*Hindustani raga masterlists (web reference)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web. citeturn23search5turn24search8],
  [Examples], [Raga Junglism “Masterlist of ragas (1000+)” and Ocean of Ragas search tools. citeturn23search5turn24search8],
  [Gap relevance], [High-value reference material but often lacks modern API access, offline mobile modes, and integrated pedagogy. (Assessment)],
)



=== Practice accompaniment and “riyaz” tooling


*Bandish: Tanpura & Tabla Riyaz*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android + iOS. citeturn23search3turn23search15],
  [Cost], [Free download with in-app purchases (Android listing). citeturn23search3],
  [Primary features], [Tabla/tanpura/manjira sounds; practice companion for riyaz. citeturn23search3],
  [UI quality (1–5)], [*4/5* (practice utilities tend to succeed when controls are minimal and responsive). (Assessment)],
  [Last updated], [APK listing reports update *Mar 3, 2026* (version 1.5.1). citeturn23search11],
  [Open source], [No. citeturn23search3turn23search11],
)



*RiyazStudio (web/desktop tanpura)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Web/desktop tool. citeturn23search7],
  [Cost], [Not stated in cited snippet. citeturn23search7],
  [Primary features], [Multiple tanpura timbres and controls; accompaniment tuning options. citeturn23search7],
  [UI quality (1–5)], [*3/5* (functional). (Assessment)],
  [Open source], [No. citeturn23search7],
)



=== Therapeutic music apps with “Vedic” framing


*Raga Therapy*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Android + iOS. citeturn23search2turn23search14],
  [Cost], [Free download (Android listing). citeturn23search2turn23search14],
  [Primary features], [Uses Indian classical ragas for mood/“healing effect”; positioned as “carefully researched” by Dr. Rajan Sankaran. citeturn23search2turn23search6],
  [Computation accuracy], [Not “computed”; the core question is therapeutic efficacy. The vendor describes a qualitative listener study process (35 listeners documenting effects), which is not equivalent to clinical validation. citeturn23search6],
  [UI quality (1–5)], [*3/5* (unknown; likely audio-player-centric). (Assessment)],
  [User base], [Consumers interested in music therapy framing. citeturn23search2turn23search14],
  [Last updated], [Google Play lists *Sep 3, 2025*. citeturn23search2],
  [Open source], [No. citeturn23search2turn23search14],
)



=== Raga recognition apps


Consumer-grade raga recognition apps are still relatively rare; most visible work is in *research/open-source prototypes* and academic approaches.

*RagaSense (open-source AI raga detection project)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Open-source codebase (GitHub). citeturn24search2],
  [Cost], [Free (repo). citeturn24search2],
  [Primary features], [AI raga classification; claims “95%+ accuracy” across many ragas (project claim). citeturn24search2],
  [Last updated], [Not established in cited snippet. citeturn24search2],
  [Open source], [Yes (GitHub project). citeturn24search2],
)



*Raga-Identification (open-source ML raga prediction)*

#table(
  columns: 2,
  [Field], [Details],
  [Platform], [Open-source codebase (GitHub). citeturn24search0],
  [Primary features], [Predicts raga from audio file using ML model pipeline. citeturn24search0],
  [Open source], [Yes. citeturn24search0],
)



Research surveys emphasize that automatic raga recognition is an active field using tradition-specific features and deep learning over pitch sequences. citeturn24search4

== Gaps, practitioner pain points, design patterns, and technical approaches


=== What’s missing or broken across Vedic science apps


==== Reproducibility and “audit trails” for serious practice

A recurring professional pain point is that apps often fail to provide a *single exportable “computation manifest”*: ephemeris engine/version, ayanāṁśa, node mode, house system, time zone/DST rule set version, and any rounding rules. When something looks “off,” professionals need to debug quickly.

You can see why this matters in real user feedback:
- Jyotish Computer users ask why the app doesn’t automatically load time zone when selecting a location; the developer response points to limitations in map-provided time zone data. citeturn36view0
- Jyotish Dashboard user reviews mention DST edge cases and emphasize that beginners can misconfigure settings and not notice; also a severe reliability complaint involves database loss after an update. citeturn37view0
- Parashara’s Light explicitly highlights that time zone/DST rules change over time and that PL9 updated these. citeturn41search2

A modern practitioner-grade tool should treat “settings + provenance” as first-class data, not buried preferences.

==== Reliability and data ownership

Several products show the classic failure mode: “great when it works, catastrophic when it breaks.”
- Jyotish Dashboard review describes chart database loss and inability to restore backups after iOS 17 update. citeturn37view0
- Omvana’s official discontinuation notice shows platform fragility: users can keep the app if installed, but it is unsupported and will receive no future updates. citeturn20search15

==== Serious Ayurveda: the “clinical-grade” gap

Ayurveda has strong reference/database direction (e.g., Dravya) but remains weak in:
- longitudinal *patient tracking* tied to Ayurvedic frameworks (prakriti/vikriti + agni + koshta + dinacharya adherence + seasonal ritucharya),
- *contraindication and interaction safety* presented in a clinician-usable way,
- bridging authoritative public-sector resources (e.g., CCRAS/AYUSH databases) into modern, explainable practitioner UX. citeturn42view0turn19search14

Pulse “AI” ecosystems exist, but tend to be device-bound and marketing-led; “validated” claims are often not accompanied by independently reviewable study protocols in the cited summaries. citeturn18search6turn18search17turn18search9

==== Vastu: the “compass trap”

Most Vastu apps solve the easiest step (direction finding + mandala overlay), but users still struggle with calibration and don’t trust results. AppliedVastu’s compass listing itself warns that accuracy depends on device settings and user procedure. citeturn50view0
Missing is a trustworthy pipeline from *floor plan → orientation validation → rule application → explainable recommendations*, with uncertainty visible.

==== Music/raga: recognition and pedagogy are still fragmented

Raga databases exist and are good (Carnatic Raga, large web masterlists), but:
- “recognize a raga from a performance” is largely still in research/prototype form, despite active academic work. citeturn24search4turn24search2turn24search0
- practice apps provide drones/metronomes, but fewer provide *pitch+gamakas feedback* in a raga-aware way (the hard part of Indian classical pedagogy). (Assessment)

=== What a serious practitioner would plausibly pay for


Evidence from market pricing shows that serious users already pay *hundreds of dollars* for Jyotish platforms:
- Kala is priced around USD 254.95. citeturn7view0
- Parashara’s Light is USD 299 per platform. citeturn22search11turn27search13
- Shri Jyoti Star 9 Pro is USD 318. citeturn11view0
- Horosoft lists a “starts at” tier that includes an “USUSD 400” reference. citeturn39view0

This suggests a viable paid market for tools that reduce professional time, improve confidence, and prevent errors. The strongest “willingness-to-pay” opportunities are:

A *Practitioner Operating System* (POS) for Jyotish + Ayurveda + Vastu clients:
- client intake forms with consent,
- standardized location/time capture,
- automatic time zone resolution (with audit logs),
- templated but customizable reports,
- private knowledge base + notes,
- multi-language exports and client-safe interpretations.

A *reproducible computation layer* (open library + certification):
- “same chart anywhere” is achievable if engine/settings are standardized and tested.
Open-source efforts like *PyJHora* show the direction: a Python package inspired by JHora with thousands of tests and verification claims against examples. citeturn25search1

A *trusted Vastu pipeline*:
- plan upload + geometry recognition + north verification + sensitivity analysis + explainable scoring. (Assessment)

A *raga-aware practice coach*:
- drone/metronome + pitch tracking + raga grammar checking + gamaka guidance (hard) + teacher feedback loop. (Assessment)

=== UI/UX patterns that work (and fail) for Vedic knowledge apps


==== Patterns that work well

A “dense domain” UI can succeed if it uses *progressive disclosure* and “modes”:
- Desktop Jyotish tools often work as power-user workbenches (multi-panel, many tables). JHora’s screenshot shows the archetype: simultaneously presenting chart panes, bala graphs, and dasha-transit correlation. citeturn33view0
- The best modern variants add user-controlled layouts (Parashara’s Light emphasizes custom screens; Shri Jyoti Star emphasizes layouts/examples and document export). citeturn41search0turn12view0

Search-first “reference database” UX is very effective for Ayurveda:
- Dravya highlights multilingual names, compact “reference book” entry format, and “multi-search” filtering. citeturn42view0

==== Patterns that fail

Overgrowth (“app bloat”) hurts content discovery:
- Insight Timer reviews complain the app has become “unmanageable” and harder to find meditations of a desired length, implying search/filter regressions. citeturn46view0

Hidden system-critical settings (time zone, DST, ayanāṁśa, node mode) create silent errors:
- Jyotish Computer users explicitly want automatic time/place/timezone flows; the developer notes limitations (Apple Maps doesn’t provide time zones) and that dual-event display isn’t supported. citeturn36view0
- Jyotish Dashboard reviews warn beginners can get wrong charts if settings are incorrect. citeturn37view0

==== Cultural and Sanskrit display considerations

If your app uses Sanskrit, Devanagari, or Vedic symbols, you need robust internationalization:
- Correct *language tagging* improves rendering, accessibility, and future-proofing. W3C provides best practices for language tags and specifying language in HTML. citeturn35search0turn35search8
- Devanagari text is Unicode-standardized (block U+0900–U+097F), and good font support matters, especially for conjuncts/marks. citeturn35search1turn35search2
- Practical recommendation: ship/declare fonts that support Devanagari + Vedic extensions (Google’s Noto Sans Devanagari explicitly supports Devanagari and Vedic-related Unicode blocks). citeturn35search2

=== Technical approaches used today (and recommended improvements)


==== Ephemeris computation

Many serious Jyotish apps explicitly use *Swiss Ephemeris*; examples in this survey include:
- JHora improvement notes reference Swiss Ephemeris and JPL DE431. citeturn2view0
- Kala explicitly states Swiss Ephemeris usage. citeturn8view0
- Jyotish Dashboard advertises “Swiss Ephemeris inside.” citeturn37view0

Swiss Ephemeris itself is positioned as a developer toolkit for astrological software, with downloadable code/data and documentation maintained by Astrodienst. citeturn30search4turn30search15

*Recommendation:* apps should expose “engine + version + data files used” in an exportable manifest and store it per chart/event, not as a global preference.

==== Ayanāṁśa selection and transparency

Differences between software often come down to ayanāṁśa choice and definition, not “wrong math.” Tools like Astro-Seek and AstroSage explicitly provide ayanāṁśa calculators and comparisons. citeturn34search1turn34search4
Parashara’s Light documentation describes its True Chitra Paksha definition explicitly (Spica at 180°). citeturn6search2

*Recommendation:* ship “ayanāṁśa explainers” inside the settings screen (what it means, which tradition uses it, and how it shifts results).

==== Time zone + DST handling (the most underestimated failure source)

Time zone rules change due to political decisions; the IANA Time Zone Database exists to track UTC offsets and daylight-saving history and is updated periodically. citeturn35search3turn35search7
Parashara’s Light explicitly notes that time zone/DST dates changed in recent years and highlights updates. citeturn41search2
Mobile apps struggle here: Jyotish Dashboard thanks geonames.org for time zone lookup; Jyotish Computer’s developer says Apple Maps doesn’t provide time zone info. citeturn37view0turn36view0

*Recommendation:* use IANA tzdb (or a proven service built on it), cache rules offline, and always allow manual override with an “uncertainty warning” flag.

==== Offline capability

Offline matters for practitioners (temple travel, client homes, rural settings, privacy).
- Shri Jyoti Star explicitly claims you can be offline “up to a month.” citeturn12view0
- JyotishApp positions itself as offline and ad-less. citeturn38view0
- Insight Timer gates offline listening behind paid features. citeturn46view0

*Recommendation:* default to offline-first for core calculations; sync is optional. If subscription gating is needed, don’t gate the astronomy engine itself—gate premium interpretations, templates, or cloud features.

=== Bottom-line gap analysis: what’s missing across categories


Across Jyotish, Ayurveda, Vastu, and raga apps, the most valuable “missing product” is not another calculator—it’s a *trustable, reproducible, practitioner-grade workflow system*:
- *Reproducible computations* (manifest + tests + provenance),
- *Reliability and data ownership* (exportable databases, backups that restore, offline mode),
- *Client workflow* (intake → analysis → recommendations → follow-up tracking),
- *Culturally literate UX* (proper Sanskrit rendering, respectful iconography, multilingual output),
- *Institutional-grade reference integration* (Ayush/CCRAS-like data fused into usable apps).

Open-source projects like PyJHora demonstrate how serious verification (thousands of tests) can exist in the ecosystem—even if most commercial apps do not yet expose that rigor to end users. citeturn25search1
