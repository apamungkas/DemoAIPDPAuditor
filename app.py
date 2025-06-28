import json
import requests
import streamlit as st
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_DEPLOYMENT_NAME, API_VERSION

# Call LLM
def ask_openai(question, user_answer):
    url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }
    messages = [
        {"role": "system", "content": "Anda adalah auditor kepatuhan UU Perlindungan Data Pribadi. Evaluasi jawaban terhadap pertanyaan audit dan beri rekomendasi."},
        {"role": "user", "content": f"Pertanyaan: {question}\nJawaban: {user_answer}"}
    ]
    body = {"messages": messages, "temperature": 0.2}
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def load_questions():
    with open("audit_questions.json", "r") as f:
        return json.load(f)

st.set_page_config(page_title="AuditBot UU PDP", layout="centered")
st.title("🛡️ PatuhPDP - AuditBot UU Perlindungan Data Pribadi")

questions = load_questions()
st.write(f"Loaded {len(questions)} questions.")
if "step" not in st.session_state:
    st.session_state.step = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
st.write(f"Current step: {st.session_state.step}")

def evaluate():
    q = questions[st.session_state.step]
    user_input = st.session_state.user_input
    if user_input.strip() == "":
        st.session_state.warning = "Silakan isi jawaban terlebih dahulu."
        st.session_state.feedback = None
    else:
        st.session_state.warning = None
        with st.spinner("Sedang mengevaluasi..."):
            feedback = ask_openai(q["question"], user_input)
            st.session_state.feedback = feedback

if st.session_state.step < len(questions):
    q = questions[st.session_state.step]
    st.subheader(f"Pertanyaan Pasal [{q['pasal']}]")
    st.markdown(f"**{q['question']}**")
    st.session_state.user_input = st.text_area("Masukkan jawaban Anda di sini:", value=st.session_state.user_input, key=f"input_{st.session_state.step}")

    if st.session_state.feedback is None:
        st.button("Kirim", key=f"kirim_{st.session_state.step}", on_click=evaluate)
        if st.session_state.get("warning"):
            st.warning(st.session_state.warning)
    else:
        st.success("✅ Evaluasi berhasil")
        st.markdown("**Hasil Evaluasi & Rekomendasi:**")
        st.write(st.session_state.feedback)
        if st.button("Lanjut ke Pertanyaan Berikutnya", key=f"lanjut_{st.session_state.step}"):
            st.session_state.step += 1
            st.session_state.feedback = None
            st.session_state.user_input = ""
            st.session_state.warning = None
            st.rerun()
else:
    st.success("🎉 Audit selesai! Terima kasih telah menggunakan AuditBot.")