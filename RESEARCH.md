# RecallScout — selection record (2026-10-13)

**Value proposition:** identify candidate omissions in an existing qualitative extract, with exact source IDs, locally. **User task:** a researcher reviews long interview passages selected under one topic. **Non-goals:** produce a definitive thematic analysis, guarantee recall, infer emotion, or replace human review. **Acceptance:** local embedding model ranks a relevant omitted synthetic passage above an unrelated one, writes a source-linked report, and rejects malformed IDs; tests and package build pass.

## Demand evidence and limits

1. [r/UXResearch first-hand question](https://www.reddit.com/r/UXResearch/comments/1sdvntu/qualitative_analysis_extraction_with_ai_spotting/) (2026-04, Reddit): the researcher explicitly cannot see relevant passages an AI extractor omitted, especially implicit mentions. Supports the omission-review job, not market size or model performance.
2. [An independent UXR practitioner](https://www.reddit.com/r/UXResearch/comments/1id46wh/feeling_existential_as_pms_at_my_org_have_started/) (2025-01, Reddit): one commenter reports that AI-generated interview notes missed or misrepresented much of what mattered, requiring a return to the transcript. Supports the need for human review across years, not a measured error rate.
3. [Meetily bug report](https://github.com/Zackriya-Solutions/meetily/issues/602) (2026-07, GitHub, independent project): a concrete long-transcript chunking bug silently omitted source ranges before summarization. Supports the broader need to make omitted source passages visible, not the claim that RecallScout would repair this specific preprocessing bug.
4. [UX Stack Exchange interview workflow](https://ux.stackexchange.com/questions/147693/interview-users-best-practices) (2023-06, Q&A): an independent practitioner says rereading transcripts/rewatching sessions is costly, preferring live notes. Supports the cost of exhaustive manual re-review, not AI false-negative rate.

[A current r/UXResearch practitioner thread](https://www.reddit.com/r/UXResearch/comments/1x43uaa/do_you_still_read_every_openended_answer_yourself/) (2026-10-13, Reddit) contains independent experiences of AI summaries missing important nuance and manual code review. Together with 2023–2026 evidence, it indicates sustained discussion, not guaranteed adoption or virality. Assumption: a lightweight second-pass queue saves review time for researchers with an existing extract; this needs user testing.

## Alternatives and distinction

Checked via search, original product pages, and GitHub before implementation:

- [Skimle](https://skimle.com/) provides AI-native qualitative coding and two-way traceability; it advertises a free trial and prices from €20/user/month (viewed 2026-10-13). It is a more complete hosted workspace. Its visible materials do not show a tool-agnostic offline post-hoc omissions audit over another extractor's IDs; that is a narrow positioning inference, not proof of no such feature.
- [Bewley](https://github.com/expectedparrot/bewley) is an MIT local-first qualitative coding CLI with codebooks, source spans, and human review. It is more capable for full studies; its documented workflow prioritizes recall but is not framed as an independent check of another extractor's omissions.

Neither alternative's code, assets, or prompts were copied. The model is a third-party downloadable dependency with its own model license; check suitability for redistribution in downstream products. RecallScout only suggests candidates, leaving coding decisions to a person.
