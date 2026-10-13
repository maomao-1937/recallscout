# RecallScout

An offline, read-only second pass for qualitative researchers who already selected passages about a topic and want a short list of possibly missed source passages.

## The job

Long interviews contain implicit mentions. A first-pass AI extractor may find “trip” yet omit “packed a bag and left before sunrise.” RecallScout compares **every unselected passage** to the research topic and the selected examples using a real local sentence-embedding model, then writes a ranked review queue with stable source IDs and verbatim text. It does **not** assert that an item is relevant, calculate recall without a human-labeled gold set, or replace research judgment.

This is intended for a researcher reviewing an existing extract, not as a transcription, full coding, or automated publication system. Input remains on the local machine. First run downloads the public `sentence-transformers/all-MiniLM-L6-v2` model; later runs work offline from cache. No API key is needed.

## Install and run

Python 3.11+ and [uv](https://docs.astral.sh/uv/) are required. From the repository root:

```sh
uv sync --python 3.11 --extra test
uv run recallscout examples/passages.json examples/selection.json --out report.md --json-out report.json
uv run pytest -q
```

`passages.json` is a non-empty array of `{ "id": "stable-id", "text": "verbatim passage", "source": "optional timestamp/file" }`. `selection.json` has a required `topic`, optional `selected_ids`, and optional `positive_examples`. An ID in `selected_ids` must exist in the passages. `--limit` defaults to 10 and `--min-score` to 0.25. The score is a ranking heuristic, not a probability.

The example files are deliberately **synthetic**, not user interviews. It selects `I01-01` (“booked a train ticket”). In an actual local-model run on 2026-10-13, the report returned `I02-01` (“missed our connection”, score 0.4026) and `I01-02` (“packed a small bag”, score 0.2577); unrelated billing/invoice passages did not pass the default threshold. Scores are model- and wording-dependent, not calibrated confidence. Inspect `report.md` for source text and `report.json` for the scores.

## Design choices and limitations

- It reviews omissions after any upstream extractor, so it does not require moving the entire research project into another coding platform.
- Embeddings can miss indirect meanings and over-rank merely similar words. Review both candidates and a random sample of non-candidates; use a manually coded gold set if a defensible recall estimate matters.
- The current model is best for English. Different languages and domain-specific codebooks require separate validation.
- Segmentation and stable IDs are supplied by the user. The tool does not ingest audio, infer participant emotion, validate transcript accuracy, or decide whether a quote supports a final research claim.
- Do not commit actual participant interviews or confidential transcripts to a public repository. The bundled data is synthetic.

The product and evidence boundary are documented in [RESEARCH.md](RESEARCH.md). MIT licensed.
