import streamlit as st

st.write("Ask FM")


st.button('Submit')

def form_callback():
    st.success(st.session_state.question_input)

with st.form(key='my_form'):
    st.text_input('Question',key="question_input")
    submit_button = st.form_submit_button(label='Submit', on_click=form_callback)