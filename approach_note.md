# Approach note (under 300 words)

I built a Streamlit prototype that accepts a timestamped WebVTT transcript and produces a class-quality assessment with one of four labels: Poor, Average, Good, or Excellent. The assessment is organised around student interaction and inclusion, rapport and class structure, teaching clarity, learning support, technical quality, and visual setup.

I chose transcript-first analysis because the supplied dataset includes VTT transcripts, which provide timestamped evidence for questions, explanations, homework discussions, and lesson structure. In AI mode, an LLM is instructed to cite transcript evidence, separate observations from uncertainty, and avoid inferring visual or vocal qualities from text. A local keyword baseline is also included as a fallback, clearly marked as low-confidence and not a validated classifier.

The organiser's feedback suggests recurring signals such as individual attention, rapport building, class introductions, homework, teacher visibility, lighting, and technical interruptions. These are useful starting points, but the proposed rubric weights are my own and require validation against the recordings. The `quality issue` examples are treated as evidence for technical problems, not as a fifth output label.

The main limitation is that transcript-only analysis cannot reliably judge vocal energy, visual setup, camera visibility, or all technical issues. Transcription errors and multilingual speech may also distort the evidence. The current prototype therefore reports limitations and does not claim automatic video/audio assessment. Recordings and transcripts must remain confidential and should only be processed by services permitted by the organiser.

Before submission, I will compare outputs against the provided feedback, inspect false positives, document failures and improvements, and test on a recording not used during development.
