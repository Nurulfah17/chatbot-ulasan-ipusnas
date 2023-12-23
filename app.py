from predictor import endpoint, load_model
import streamlit as st
import numpy as np

# set page config
st.set_page_config(
	page_title="Chatbot Ipusnas's Review",
	page_icon="📲"
)

# load model
with st.spinner("Loading our awesome AI 🤩. Please wait ..."):
	model = load_model()

@st.cache_data
def handle_text(text):
	# predict
	prediction = endpoint(text)
	my_array = np.array(prediction)
	# Convert to string
	result_str = my_array[0]

	# return
	return result_str
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
	st.write(result)

