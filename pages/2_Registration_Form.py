import streamlit as st
from Home import face_rec
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer
import av

#st.set_page_config(page_title='Registration Form')  
st.subheader('Registration Form')

## init registration form
register_form = face_rec.RegistrationForm()

# Step-1: collect person name and role
# form 
person_name = st.text_input(label='Name', placeholder='First & Last Name')
role = st.selectbox(label='Select your role', options=('Student', 'Teacher'))

# Step-2: Collect facial embedding of that person
def video_callback_func(frame):
    img = frame.to_ndarray(format='bgr24') # 3d array bgr
    reg_image, embedding = register_form.get_embedding(img)
    # two step process
    # 1st step save data into local computer txt
    if embedding is not None:
        with open('face_embedding.txt', mode='ab') as f:
            np.savetxt(f, embedding)

    return av.VideoFrame.from_ndarray(reg_image, format='bgr24')

webrtc_streamer(key='registration', video_frame_callback=video_callback_func,
rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
	}
)

# Step-3: Save the data in Redis database

if st.button('Submit'):
    ret_value = register_form.save_data_in_redis_db(person_name, role)
    if ret_value == True:
        st.success(f"{person_name} registered successfully")
    elif ret_value == 'name_false':
        st.error('Please enter the name: Name cannot be empty or spaces')
    elif ret_value == 'file_false':
        st.error('face_embedding.txt not found. Please refresh the page anc execute again')

