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
    logs_df = pd.DataFrame(logs_nested_list, columns=['Name', 'Role', 'Timestamp'])

    # step 3: time based Analysis or Report
    logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
    logs_df['Date'] = logs_df['Timestamp'].dt.date

    # step 3.1: Calculate Intime and OutTime
    # Intime: At which person is first detected in that day (min Timestamp of the date)
    # OutTime: At which person is last detected in that day (max Timestamp of the date)
    report_df = logs_df.groupby(by=['Date', 'Name', 'Role']).agg(
        In_time = pd.NamedAgg('Timestamp', 'min'), # in time
        Out_time = pd.NamedAgg('Timestamp', 'max') # out time
    ).reset_index()

    report_df['In_time'] = pd.to_datetime(report_df['In_time'])
    report_df['Out_time'] = pd.to_datetime(report_df['Out_time'])    
    report_df['Duration'] = report_df['Out_time'] - report_df['In_time']
    
    # step 4: MArking person as present or absent
    all_dates = report_df['Date'].unique()
    name_role = report_df[['Name', 'Role']].drop_duplicates().values.tolist()

    date_name_role_zip = []
    for dt in all_dates:
        for name, role in name_role:
            date_name_role_zip.append([dt, name, role])
    
    date_name_role_zip_df = pd.DataFrame(date_name_role_zip, columns=['Date', 'Name', 'Role'])
    # left join with report_df
    date_name_role_zip_df = pd.merge(date_name_role_zip_df, report_df, how='left', on=['Date', 'Name', 'Role'])    

    # Duration
    # Hours
    date_name_role_zip_df['Duration_seconds'] = date_name_role_zip_df['Duration'].dt.seconds
    date_name_role_zip_df['Duration_hours'] = date_name_role_zip_df['Duration_seconds'] / (60*60)
    
    def status_marker(x):
        if pd.Series(x).isnull().all():
            return 'Absent'
        elif x >= 0 and x < 1:
            return 'Absent (less than 1 hour)'
        elif x >= 1 and x < 4:
            return 'Half Day (less than 4 hours)'
        elif x >= 4 and x < 6:
            return 'Half Day'
        elif x >= 6:
            return 'Present'

    date_name_role_zip_df['Status'] = date_name_role_zip_df['Duration_hours'].apply(status_marker)  
    st.dataframe(date_name_role_zip_df)


            