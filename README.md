# AI Class Quality Evaluator

An AI-assisted prototype for evaluating online class quality using timestamped transcript evidence and a structured teaching-quality rubric.

## Overview

I built this project to explore how AI can help identify strengths and areas for improvement in online teaching. The evaluator organizes feedback into six dimensions:

- Student Interaction & Inclusion — 25%
- Rapport & Class Opening/Closing — 20%
- Teaching Clarity & Structure — 20%
- Learning Support & Follow-through — 15%
- Audio/Technical Quality — 10%
- Visual Setup & Teacher Visibility — 10%

The application presents a four-level class-quality rating: **Poor, Average, Good, or Excellent**, along with rubric scores and supporting observations.

## How It Works

1. Provide a WebVTT (`.vtt`) transcript or paste transcript text into the Streamlit interface.
2. The application parses timestamped transcript segments.
3. The evaluator analyzes available transcript evidence and generates a provisional quality assessment.
4. The results include rubric scores, strengths, improvement suggestions, and assessment limitations.

The current working baseline uses keyword-based indicators. The project also includes an OpenAI API analysis option. Any external API must be used only when permitted by the recording organiser.

## Technology Stack

- Python
- Streamlit
- WebVTT transcript parsing
- JSON-based assessment output
- Optional OpenAI API integration

## Run Locally

**Requirements:** Python 3.10 or later.

1. Clone the repository:

   ```bash
   git clone https://github.com/Mubeenashaik7/ai-class-quality-evaluator.git
   cd ai-class-quality-evaluator
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python -m streamlit run app.py
   ```

5. Open the local URL displayed in the terminal.

## Limitations

- The current interface accepts transcript text and WebVTT files; direct video upload and recording-link processing are not implemented in this submitted version.
- Transcript evidence alone cannot establish actual audio quality, visual setup, teacher visibility, or non-verbal behaviour.
- Keyword-based results are provisional and have not been validated as a reliable classifier.
- Assessment quality depends on the completeness and accuracy of the transcript.

## Privacy and Responsible Use

Class recordings and transcripts may contain sensitive information. Use only recordings you are authorised to process, and only services approved by the organiser. Do not commit recordings, transcripts, API keys, or other confidential information to this public repository.

This prototype is intended to support formative teaching feedback, not high-stakes decisions.

## Project Status

This is a working prototype developed to explore rubric-based online class assessment. Further work is needed to validate assessment consistency, support direct recording ingestion, and test the system on unseen recordings.
