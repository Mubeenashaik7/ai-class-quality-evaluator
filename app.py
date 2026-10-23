import os, json, re, tempfile
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="AI Class Quality Evaluator", page_icon="🎓", layout="wide")

RUBRIC = {
    "Student interaction & inclusion": 25,
    "Rapport & class opening/closing": 20,
    "Teaching clarity & structure": 20,
    "Learning support & follow-through": 15,
    "Audio/technical quality": 10,
    "Visual setup & teacher visibility": 10,
}

SYSTEM_PROMPT = """You are an evidence-based reviewer of online classes. Assess only evidence present in the supplied transcript and/or explicitly supplied observations.
Return JSON with keys:
rating (exactly Poor, Average, Good, or Excellent),
summary (2-3 sentences),
scores (object with each rubric dimension mapped to integer 1-5 or null if not assessable),
strengths (array of objects {observation, evidence, timestamp}),
improvements (array of objects {observation, evidence, timestamp}),
limitations (array of strings),
confidence (Low, Medium, or High).
Rules:
- Do not infer tone, energy, lighting, camera visibility, facial expression, or background from a transcript.
- If evidence is missing, use null / "not observed"; do not penalize automatically.
- Distinguish transcription errors from teacher errors.
- Avoid claims about individual children; focus on teaching practices.
- Do not use the dataset folder name or expected label to choose the rating.
- Cite short transcript excerpts and timestamps when available.
- Consider the supplied rubric as guidance, not objective ground truth.
- Technical problems should affect the rating according to their demonstrated impact, not merely because a single interruption occurred.
- Output valid JSON only."""

def parse_vtt(vtt):
    lines = vtt.replace("\r", "").split("\n")
    cues, current_time, text_lines = [], None, []
    def flush():
        nonlocal current_time, text_lines
        if text_lines:
            content = " ".join(x.strip() for x in text_lines if x.strip())
            content = re.sub(r"<[^>]+>", "", content)
            if content and not content.isdigit():
                cues.append((current_time or "", content))
        current_time, text_lines = None, []
    for line in lines:
        s = line.strip()
        if "-->" in s:
            flush()
            current_time = s.split("-->")[0].strip()
        elif s == "WEBVTT" or not s or s.startswith("NOTE"):
            if not s: flush()
        elif re.fullmatch(r"\d+", s):
            continue
        else:
            text_lines.append(s)
    flush()
    return cues

def transcript_stats(cues):
    text = " ".join(t for _, t in cues)
    return {
        "cue_count": len(cues),
        "word_count": len(text.split()),
        "question_mark_count": text.count("?"),
        "text": text,
    }

def fallback_assessment(cues):
    """Transparent baseline; not a substitute for multimodal/LLM evaluation."""
    text = " ".join(t for _, t in cues)
    low = text.lower()
    indicators = {
        "Student interaction & inclusion": sum(low.count(x) for x in ["?", " can you", "what do you", "tell me", "your answer", "any questions", "everyone"]),
        "Rapport & class opening/closing": sum(low.count(x) for x in ["hello", "hi ", "welcome", "good morning", "thank you", "bye", "goodbye"]),
        "Teaching clarity & structure": sum(low.count(x) for x in ["because", "for example", "so that", "first", "next", "let me explain", "remember"]),
        "Learning support & follow-through": sum(low.count(x) for x in ["homework", "assignment", "practice", "previous class", "last class", "revision"]),
        "Audio/technical quality": sum(low.count(x) for x in ["can't hear", "cannot hear", "audio", "voice", "sound", "screen is", "not visible"]),
        "Visual setup & teacher visibility": None,
    }
    scores = {}
    for dim, count in indicators.items():
        if count is None:
            scores[dim] = None
        else:
            scores[dim] = min(5, max(1, 1 + count // 3))
    observed = [v for v in scores.values() if v is not None]
    avg = sum(observed) / len(observed) if observed else 2.5
    rating = "Poor" if avg < 1.8 else "Average" if avg < 2.7 else "Good" if avg < 3.7 else "Excellent"
    return {
        "rating": rating,
        "summary": "This is a lightweight transcript-only baseline based on keyword indicators. It is not a validated assessment and should be treated as a provisional result.",
        "scores": scores,
        "strengths": [{"observation": "Potential interaction or teaching cues detected in transcript", "evidence": "Keyword-based signal only; review the transcript to confirm.", "timestamp": None}],
        "improvements": [{"observation": "Review the recording and transcript manually for context, accuracy, and omitted signals.", "evidence": "The baseline cannot understand context or reliably assess delivery.", "timestamp": None}],
        "limitations": ["Heuristic baseline, not a true language-model assessment.", "Cannot assess vocal tone, lighting, camera visibility, or visual setup from transcript.", "Transcript keyword counts can be misleading and do not prove class quality."],
        "confidence": "Low"
    }

def call_llm(cues, model):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # Keep evidence manageable while retaining cue timestamps.
    transcript = "\n".join(f"[{ts}] {txt}" for ts, txt in cues)
    transcript = transcript[:45000]
    prompt = f"""Assess this class transcript using the rubric below.
Rubric dimensions and suggested weights:
{json.dumps(RUBRIC, ensure_ascii=False)}
Transcript:
{transcript}

Return the JSON schema requested in your system instructions. If transcript content appears garbled or mistranscribed, say so and lower confidence rather than treating it as teacher error."""
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
    )
    return json.loads(response.choices[0].message.content)

def render_assessment(result):
    rating = result.get("rating", "Average")
    st.subheader("Assessment result")
    st.metric("Class quality", rating)
    st.write(result.get("summary", ""))
    scores = result.get("scores", {})
    if scores:
        st.markdown("#### Rubric scores")
        for dim, score in scores.items():
            if score is None:
                st.write(f"**{dim}:** Not observed / not assessable")
            else:
                st.write(f"**{dim}:** {score}/5")
                st.progress(min(100, max(0, int(score) * 20)))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Strengths")
        for item in result.get("strengths", []):
            st.write("• " + item.get("observation", ""))
            if item.get("evidence"):
                st.caption(f'Evidence: {item["evidence"]}')
            if item.get("timestamp"):
                st.caption(f'Timestamp: {item["timestamp"]}')
    with col2:
        st.markdown("#### Improvements")
        for item in result.get("improvements", []):
            st.write("• " + item.get("observation", ""))
            if item.get("evidence"):
                st.caption(f'Evidence: {item["evidence"]}')
            if item.get("timestamp"):
                st.caption(f'Timestamp: {item["timestamp"]}')
    if result.get("limitations"):
        with st.expander("Limitations and uncertainty"):
            for item in result["limitations"]:
                st.write("• " + item)
    st.caption("Confidence: " + str(result.get("confidence", "Low")))
    st.download_button("Download assessment JSON", json.dumps(result, indent=2, ensure_ascii=False), file_name="class_assessment.json", mime="application/json")

st.title("🎓 AI Class Quality Evaluator")
st.write("Assess an online class recording using timestamped transcript evidence. This prototype does not claim to assess video-only signals unless separately reviewed.")
st.warning("Privacy: the organiser requires class recordings to remain confidential and only be processed by permitted services. This app analyses a transcript locally by default. If you enable the OpenAI API option, transcript text is sent to the configured API; do not use it unless the organiser permits it. Do not upload identifiable recordings to a public host.")

with st.sidebar:
    st.header("Assessment settings")
    mode = st.radio("Analysis mode", ["AI analysis (OpenAI API)", "Local transcript baseline"])
    model = st.text_input("OpenAI model", value=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"))
    st.caption("AI mode requires OPENAI_API_KEY in the environment.")
    st.markdown("**Rubric dimensions**")
    for k, v in RUBRIC.items():
        st.write(f"{k}: {v}%")

st.markdown("### 1. Provide transcript evidence")
uploaded_vtt = st.file_uploader("Upload WebVTT transcript (.vtt)", type=["vtt"])
pasted = st.text_area("Or paste transcript text (optional)", height=180, placeholder="Paste transcript text here if you do not have a .vtt file.")
st.markdown("### 2. Optional recording metadata")
duration = st.text_input("Recording duration (optional)", placeholder="e.g. 45 minutes")
notes = st.text_area("Your permitted observations from audio/video (optional)", placeholder="Only add observations you have actually verified, such as camera off at 12:10 or repeated audio interruption at 06:20.")
if uploaded_vtt:
    raw = uploaded_vtt.getvalue().decode("utf-8", errors="replace")
    cues = parse_vtt(raw)
    st.success(f"Loaded {len(cues)} transcript cues.")
elif pasted.strip():
    cues = [("", line.strip()) for line in pasted.splitlines() if line.strip()]
else:
    cues = []

if cues:
    stats = transcript_stats(cues)
    st.caption(f'{stats["cue_count"]} transcript segments · {stats["word_count"]} words · {stats["question_mark_count"]} question marks')
    with st.expander("Preview parsed transcript"):
        st.text("\n".join(f"[{ts}] {txt}" for ts, txt in cues[:100]))
else:
    st.info("Upload a .vtt file or paste transcript text to begin.")

if st.button("Assess class", type="primary", disabled=not bool(cues)):
    with st.spinner("Assessing transcript evidence..."):
        try:
            if notes.strip():
                cues_for_ai = cues + [("", "Reviewer-provided verified audio/video observations: " + notes.strip())]
            else:
                cues_for_ai = cues
            if mode == "AI analysis (OpenAI API)":
                if not os.environ.get("OPENAI_API_KEY"):
                    st.error("OPENAI_API_KEY is not set. Choose Local transcript baseline or configure the key in your deployment secrets.")
                    st.stop()
                result = call_llm(cues_for_ai, model)
                result.setdefault("limitations", [])
                result["limitations"].append("This run analysed transcript text and reviewer-provided observations only; it did not automatically inspect video frames or raw audio.")
            else:
                result = fallback_assessment(cues)
                if notes.strip():
                    result["limitations"].append("Reviewer notes were not incorporated by the keyword baseline.")
            render_assessment(result)
        except Exception as e:
            st.error(f"Assessment failed: {type(e).__name__}: {e}")
            st.info("Check the API key/model or use Local transcript baseline.")
