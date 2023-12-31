from predictor import setup_qa_chain, chat_with_qa_chain
import streamlit as st
import numpy as np

# set page config
st.set_page_config(
	page_title="Chatbot Ipusnas's Review",
	page_icon="📲"
)

# load model
with st.spinner("Loading our awesome AI 🤩. Please wait ..."):
	model = setup_qa_chain()

def data_generator():
    for chunk in large_data_source:
        yield chunk

# Menggunakan generator dalam aplikasi Streamlit
for data_chunk in data_generator():
    st.write(data_chunk)
@st.cache_data
def handle_text(text):
	# predict
	prediction = chat_with_qa_chain(text)
	my_array = np.array(prediction)
	# Convert to string
	result_str = my_array[0]

	# return
	return result_str

if "data" in st.session_state:
    del st.session_state.data
	
# title and subtitle
st.title("📲 Chatbot Ipusnas's Review")
st.write("It's easy and fast. Put the review down below and we will take care the rest 😉")

# user input
user_review = st.text_area(
	label="Review:",
	help="Input your (or your client's) review here, then click anywhere outside the box."
)

if user_review != "":
	prediction = handle_text(user_review)

	# display prediction
	st.subheader("AI thinks that ...")

	# check prediction
	st.write(prediction)


