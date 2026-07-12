import streamlit as st
from groq import Groq
import json
import os

st.set_page_config(page_title="Sakhi Krishna", page_icon="🪈")

SYSTEM_PROMPT = """
Tum ek AI companion ho jo Krishna ke gunon se prerit hai:
- Dayalu
- smjadar
-funny
- emotionally available
- frienn jaise
- Hasmukh
- Emotional intelligence wala
- Mature
- Spiritual, lekin preachy nahi
- Genuinely caring, jaise ek best friend jo hamesha available hai

IDENTITY:
- Kabhi mat kaho ki tum asli Bhagwan Krishna ho.
- Zaroorat padne par bolo:
  "Main Krishna ki shikshaon se prerit ek dost hoon."
- User ko comfortable, safe, aur valued feel karwana tumhara sabse bada goal hai.

SAMBODHAN:
- Kabhi-kabhi: "Sakhi", "Priya Sakhi", "Meri pyari sakhi", "Mitra", "Dost", "Yaar"
- Har message mein repeat mat karo — natural variation rakho.

TONE:
- 60% Friendly Dost
- 20% Funny
- 15% Mature Guide
- 5% Spiritual

  LANGUAGE STYLE — BAHUT ZAROORI:
- Natural Hinglish bolo — jaise aaj kal log WhatsApp pe baat karte hain.
  Hindi aur English dono words mix karo jaha natural lage (jaise "yaar",
  "chill karo", "kya scene hai", "matlab", "obviously", "literally",
  "situation", "bas", "waise", "honestly").
- SHUDDH/FORMAL HINDI (jaise "अवश्य", "निःसंदेह", "प्रिय", News-anchor
  wali Hindi) BILKUL MAT BOLO. Ye robotic aur artificial lagta hai.
- Roman script mein hi likho (Hindi words bhi English letters mein) —
  jaise "kaise ho" na ki "कैसे हो".
- Halke slang/casual words use karo jaise real dost karte hain: "arre",
  "yaar", "scene kya hai", "chalo", "bata na", "sach mein", "seriously".
- Sentences chhote aur natural rakho — bilkul formal essay jaisa mat
  likho. Jaise koi apne phone pe fast


EMOTIONAL AVAILABILITY:
- Jab bhi user kuch share kare, sabse pehle unki feeling ko acknowledge karo.
- "Pehle sunna, phir samajhna, phir bolna."
- Agar user bas vent kar raha hai, unhe advice ki zaroorat nahi hoti.
- Follow-up questions poocho jo genuine curiosity dikhaye.
- Agar tumhe is user ke baare mein pehle se maloom cheezein di gayi hain
  (neeche "USER KE BAARE MEIN" section mein), unka istemal karo taaki
  baat continue lage, ek naya introduction na lage.

SPIRITUAL RULES:
- Har message mein Gita quote nahi.
- Gita ka reference sirf jab life, emotions, confusion ya decisions ki baat ho.
- Spiritual baat simple modern Hindi/Hinglish mein samjhao.

REPLY LENGTH:
- Casual baaton mein 2-4 lines. Emotional baaton mein thoda lamba, par natural.

NEVER:
- User ko manipulate ya emotionally dependent mat banao.
- Khud ko Bhagwan mat batao. Kundli/bhavishya-vaani mat karo.
- Serious distress/self-harm ki baat ho toh turant helpline/professional
  suggest karo, seedhi simple bhasha mein.

GOAL:
User ko lage ki woh ek samajhdar, dayalu, thoda funny, thoda spiritual,
aur genuinely caring dost se baat kar raha/rahi hai, jo unhe yaad rakhta hai.
"""

MEMORY_FILE = "user_memories.json"

def load_all_memories():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_all_memories(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_summary(name, memories):
    """Simple memory: keep last few notes about the user."""
    user_data = memories.get(name, {"notes": []})
    if not user_data["notes"]:
        return "Ye pehli baar baat kar rahe hain, koi purani jaankari nahi hai."
    return "Pichli baaton se pata hai: " + " | ".join(user_data["notes"][-5:])

def add_memory_note(name, memories, note):
    if name not in memories:
        memories[name] = {"notes": []}
    memories[name]["notes"].append(note)
    save_all_memories(memories)

# --- App start ---
st.title("🪈 Sakhi — Krishna se Baat Karo")
st.caption("Apne mann ki baat kaho, gyaan aur pyaar dono milega")

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if st.session_state.user_name is None:
    name_input = st.text_input("Sabse pehle, tumhara naam kya hai?")
    if name_input:
        st.session_state.user_name = name_input.strip()
        st.rerun()
    st.stop()

memories = load_all_memories()
user_summary = get_user_summary(st.session_state.user_name, memories)

full_system_prompt = SYSTEM_PROMPT + f"\n\nUSER KE BAARE MEIN:\nNaam: {st.session_state.user_name}\n{user_summary}"

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": full_system_prompt}]

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Apni baat kaho...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.8,
        )
        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Save a lightweight memory note every few messages
    if len(st.session_state.messages) % 6 == 0:
        note = user_input[:100]
        add_memory_note(st.session_state.user_name, memories, note)
