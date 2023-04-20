import streamlit as st
import os
from deta import Deta
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

deta_key = os.getenv("DETA_KEY")
deta_db = os.getenv("DETA_DB")
answer_key=os.getenv("ANSWER_KEY")
name=os.getenv("NAME")

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

    last_timestamp_input_question=load_kv("last_timestamp_input_question")

    if last_timestamp_input_question is None:
        last_timestamp_input_question=0

    current_time=datetime.now().timestamp()
    delta_time=current_time-last_timestamp_input_question

    if delta_time<60:
        st.error(f"Please wait {int(60-delta_time)} seconds before asking again")
        return

    save_kv("question" + str(position), st.session_state.question_input)
    save_kv("question_position",position+1)
    save_kv("last_timestamp_input_question",datetime.now().timestamp())
    st.success("Question : "+st.session_state.question_input)
    st.cache_data.clear()

def form_callback_answer_input():
    position = load_kv("question_position")
    for i in range(position):
        if ("answer"+str(i)) not in st.session_state:
            continue
        if answer_key in st.session_state["answer"+str(i)]:
            answer = st.session_state["answer"+str(i)]
            answer=answer.replace(answer_key,"")
            save_kv("answer"+str(i),answer)
            st.success("Answer : "+answer)
            st.cache_data.clear()
            return
        st.error("You are not allowed to answer question")


with st.form(key='my_form'):
    st.title(f"Ask :red[{name}] a question")
    st.text_input('Ask a question',key="question_input",label_visibility="collapsed")
    submit_button = st.form_submit_button(label='Submit', on_click=form_callback_question_input)

position=load_kv("question_position")

if position is None:
    position=0

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