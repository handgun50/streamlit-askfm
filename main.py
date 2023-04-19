import streamlit as st
import os
from deta import Deta
from dotenv import load_dotenv

load_dotenv()

deta_key = os.getenv("DETA_KEY")
deta_db = os.getenv("DETA_DB")
answer_key=os.getenv("ANSWER_KEY")

deta = Deta(deta_key)
db = deta.Base(deta_db)

@st.cache_data
def load_kv(key):
    load = db.get(key)
    if load:
        return load["value"]
    else:
        return None

def save_kv(key, value):
    save = db.put({"key": key, "value": value})
    return "Ok"

def form_callback_question_input():
    position=load_kv("question_position")
    if position is None:
        position=0
    save_kv("question" + str(position), st.session_state.question_input)
    save_kv("question_position",position+1)
    st.success(st.session_state.question_input)

def form_callback_answer_input():
    position = load_kv("question_position")
    for i in range(position):
        if ("answer"+str(i)) not in st.session_state:
            continue
        if answer_key in st.session_state["answer"+str(i)]:
            answer = st.session_state["answer"+str(i)]
            answer=answer.replace(answer_key,"")
            save_kv("answer"+str(i),answer)
            st.success(answer)
            st.cache_data.clear()

with st.form(key='my_form'):
    st.title("Ask a question")
    st.text_input('Ask a question',key="question_input",label_visibility="collapsed")
    submit_button = st.form_submit_button(label='Submit', on_click=form_callback_question_input)

position=load_kv("question_position")
for i in reversed(range(position)):
    result=load_kv("question"+str(i))

    if result is None:
        continue

    with st.form(key='answer_form' + str(i)):
        st.markdown("#### Q-"+str(i)+". "+result)
        key_name="answer"+str(i)
        load=load_kv(key_name)
        if load:
            st.markdown(load)
            is_disabled=True
        else:
            st.text_input('Answer', key=key_name,label_visibility="collapsed",placeholder="")
            is_disabled=False
        submit_button = st.form_submit_button(label='Answer', on_click=form_callback_answer_input,disabled=is_disabled)