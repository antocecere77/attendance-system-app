import streamlit as st
from Home import face_rec
from streamlit_webrtc import webrtc_streamer
import av
import time

#st.set_page_config(page_title='Prediction')  
st.subheader('Real-Time Attendance System')

# Retrieve data from Redis database
with st.spinner('Retriving data from Redis db...'):
    redis_face_db = face_rec.retrieve_data(name = 'academy:register')
    st.dataframe(redis_face_db)

st.success('Data successfully retrieved from Redis')

# time
waitTime = 30 # time in seconds
setTime = time.time()
realtimepred = face_rec.RealTimePred() # real time prediction class

# Real time Prediction
# streamlit webrtc

# callback function
def video_frame_callback(frame):
    global setTime

    img = frame.to_ndarray(format="bgr24") # 3 dimension array  

    # operation that you can perform
    pred_img = realtimepred.face_prediction(img, 
                                        redis_face_db, 
                                        'facial_features',
                                        ['Name', 'Role'], thresh=0.5)

    timenow = time.time()
    difftime = timenow - setTime
    if difftime >= waitTime:
        realtimepred.saveLogs_redis()
        setTime = time.time() # reset time
        print('Save data to redis database')

    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback,
rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
	}
)