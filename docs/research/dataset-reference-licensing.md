# Can we reuse official dataset descriptions?

Pre-flight for F73 (the 8th-grade explanatory document), 2026-09-14. The team
lead asked in the Sprint 14 retrospective: *"Are there any references that we can
use from the internet to better explain the datasets (can we copy and use
official references or do we need to reference)"*

Settling it first because it constrains the document's shape, and it is cheap.

## Short answer

| Dataset | License | Can we copy its description? | What we do |
|---|---|---|---|
| **ULB creditcard** | Database Contents License (DbCL) v1.0 | **Yes**, including commercially | Quote or paraphrase freely, attribute anyway |
| **IEEE-CIS** | Kaggle competition rules, Vesta Corporation data | **No, assume not** | Paraphrase in our own words; cite, never copy |
| **SPECTRA** | See `docs/references.md` | Unverified | Treat as IEEE-CIS until checked |

**Practical consequence for F73: write every dataset explanation in our own
words regardless.** The licensing permits copying in one case out of three, and
a document with one copied passage and two paraphrased ones is harder to
maintain than three paraphrases. The reuse right is worth having as a fallback,
not as a plan.

## ULB creditcard: DbCL v1.0, permissive

Published by the ULB Machine Learning Group on Kaggle under the **Database
Contents License (DbCL) v1.0**.

From the license text at opendatacommons.org:

- Grants "a worldwide, royalty-free, non-exclusive, perpetual, irrevocable
  copyright license" **including the right to sublicense**.
- Rights "explicitly include commercial use, and do not exclude any field of
  endeavour."
- The DbCL covers the CONTENTS' copyright only. Section 2.3: "This license does
  not cover any Database Rights, Database copyright, or contract over the
  Contents as part of the Database." Database-level rights sit under ODbL
  separately.
- **The DbCL itself specifies no attribution requirement.**

**So we may copy the description.** We will attribute anyway, for two reasons:
the dataset page asks for acknowledgement by convention, and an explanatory
document that does not say where its facts came from would contradict the entire
posture of the project it explains.

**The acknowledgement to use**, as the dataset states it: the data was collected
and analysed during a research collaboration of **Worldline** and the **Machine
Learning Group of Université Libre de Bruxelles (MLG-ULB)** on big data mining
and fraud detection.

## IEEE-CIS: assume restrictive

Provided by **Vesta Corporation** through a Kaggle competition run by the IEEE
Computational Intelligence Society, July to October 2019.

**I could not retrieve the competition's data-use rules.** Kaggle competition
pages are JavaScript-rendered and the rules sit behind acceptance. What I can
establish from secondary sources is that the data is Vesta's **real-world
e-commerce transactions**, which is commercial data contributed for a
competition rather than published under an open licence.

**Treat as: cite, do not copy.** Competition data typically carries
non-commercial and no-redistribution terms, and the burden of proof runs the
wrong way here -- we would be asserting a right we have not verified, in a
public repository, about another company's commercial data.

**If the right ever matters**, the team lead can read the accepted competition
rules from a logged-in Kaggle session. Until then this is the safe reading and
it costs us nothing, because we are paraphrasing anyway.

## What this means for F73

1. **Write dataset explanations in our own words.** Uniform, maintainable, and
   correct under every licence above.
2. **Attribute every dataset** with its source and collaboration, whether or not
   the licence compels it.
3. **Quote sparingly and only from ULB**, if a phrase is genuinely better than a
   paraphrase.
4. **Do not reproduce IEEE-CIS field descriptions verbatim**, including the
   column dictionaries circulating in competition write-ups. Those are
   derivative of the competition data.
5. **Record the licence beside each dataset** in the document, because a reader
   learning about datasets should learn that datasets have licences.

## What I could not establish

- **IEEE-CIS competition rules verbatim.** Behind acceptance; not retrievable
  anonymously.
- **SPECTRA licensing.** Not checked in this pre-flight. `docs/references.md`
  names the source; the terms were not verified.
- Whether Kaggle's own Terms of Service add constraints on top of a dataset's
  stated licence. Probably yes for scraping and redistribution of the files
  themselves, which we do not do -- `experiments/data/` is gitignored and only
  `MANIFEST.json` is committed.
