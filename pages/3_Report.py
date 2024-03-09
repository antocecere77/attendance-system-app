import streamlit as st
from Home import face_rec
import pandas as pd

#st.set_page_config(page_title='Reporting', layout='wide')  
st.subheader('Reporting')

# Retrive logs data and show in Report.py
# Extract data from Redis list
name = 'attendance:logs'

def load_logs(name, end=-1):
    logs_list = face_rec.r.lrange(name, start=0, end=end) # extract all data from redis database
    return logs_list

# tabs to show the info
tab1, tab2, tab3 = st.tabs(['Registered Data', 'Logs', 'Attendance Report'])

with tab1:
    if st.button('Refresh Data'):
        # Retrieve data from Redis database
        with st.spinner('Retriving data from Redis db...'):
            redis_face_db = face_rec.retrieve_data(name = 'academy:register')
            st.dataframe(redis_face_db)

with tab2:
    if st.button('Refresh Logs'):
        st.write(load_logs(name=name))

with tab3:
    st.subheader('Attendance Report')
    
    # load logs into attribute logs_list
    logs_list = load_logs(name=name)

    # step 1: convert logs that in list of bytes into list of string
    convert_byte_to_string = lambda x: x.decode('utf 8')
    logs_list_string = list(map(convert_byte_to_string, logs_list))

    # step 2: split string by @ and create nested list 
    split_string = lambda x: x.split('@')
    logs_nested_list = list(map(split_string, logs_list_string))
    
    # convert nested list info into dataframe
    log_df = pd.DataFrame(logs_nested_list, columns=['Name', 'Role', 'Timestamp'])

    st.write(log_df)


