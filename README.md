# HUMANITI AI — Class Quality Evaluator

A small Streamlit prototype for assessing online-class quality from a timestamped WebVTT transcript. It returns a four-level rating (Poor, Average, Good, Excellent), rubric scores, evidence, strengths, improvement suggestions, confidence, and limitations.

## Important scope and privacy notes

- The current prototype **analyses transcript text**, not raw video/audio automatically.
- It does not independently verify lighting, teacher visibility, vocal energy, or facial expressions. Add only observations you have actually verified.
- The HUMANITI AI brief says recordings must remain confidential and may only be processed by services permitted by the organiser, especially where children are identifiable.
- The app defaults to local, keyword-based baseline mode. OpenAI mode sends transcript text to the configured API; use it only if the organiser permits that service.
- Do not upload confidential recordings or transcripts to a public repository. `.gitignore` excludes media/transcript files.
- The keyword baseline is deliberately labelled low-confidence and is not a validated classifier.

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Upload a `.vtt` transcript exported for a class, or paste transcript text.

## Enable AI assessment (only if permitted)

Set an API key in your environment; never hard-code it.

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4.1-mini"
streamlit run app.py
```

macOS/Linux:
```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4.1-mini"
streamlit run app.py
```

Then select **AI analysis (OpenAI API)** in the sidebar. In hosted deployments, store secrets in the platform's secret manager, not in source code.

## Suggested validation before submission

1. Run the app with at least one transcript from each labelled category.
2. Compare ratings and evidence against the organiser's feedback notes.
3. Review false positives caused by transcription errors, chess-specific terms, language differences, and missing class segments.
4. Keep a record of what failed and what you changed.
5. If you have permission to analyse audio/video, add and test those modalities before claiming multimodal assessment.
6. Test with a recording not used during development, as the brief says evaluators will do.

## Rubric dimensions

The starting rubric includes student interaction/inclusion, rapport and class structure, teaching clarity, learning support, audio/technical quality, and visual setup. Weights are provisional design choices, not organiser-provided weights. Missing evidence should be marked not observed rather than automatically treated as failure.

## Submission checklist

- [ ] Hosted working app link accessible to evaluators
- [ ] GitHub repository with source and this README
- [ ] No API keys, confidential recordings, or private transcripts in GitHub
- [ ] Relevant AI interaction history saved and redacted
- [ ] Approach note under 300 words
- [ ] Tested on an unseen recording
