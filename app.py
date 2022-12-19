# import core packages

import streamlit as st
import streamlit.components.v1 as stc

# import eda packages
import pandas as pd
import neattext.functions as nfx
import pycountry

#Utils packages
import base64
import time
import requests

timestr = time.strftime("%Y%m%d-%H%M%S")
countriesList=list(map (lambda country : country.name, list(pycountry.countries)))
emailExtensionsList=["gmail.com"]
def populateEmailExtensionsList():
    with open("emailExtensions.txt") as file:
        for line in file.readlines():
            emailExtensionsList.append(line.strip())
        

def makeDownloadable(data, task_type):
    csvfile = data.to_csv(index = False)
    b64 = base64.b64encode(csvfile.encode()).decode()
    st.markdown("### **Download Results File** ")
    newfileName = "extracted_{}_result_{}.csv".format(task_type, timestr)
    href = f'<a href="data:file/csv;base64,{b64}" download="{newfileName}">Click Here!</a>'
    st.markdown(href, unsafe_allow_html = True)
    
    
def makeDownloadableDf(data):
    csvfile = data.to_csv(index = False)
    b64 = base64.b64encode(csvfile.encode()).decode() #B64 encoding
    st.markdown("### **Download CSV File** ")
    newFileName = "extracted_data_result_{}.csv".format(timestr)
    href=f'<a href="data:file/csv;base64,{b64}" download="{newFileName}">Click Here!</a>'

# Function to fetch Result
@st.cache
def fetch_query(query):
    header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,
    'referer':'https://www.google.com/'
    }
    base_url = "https://webcache.googleusercontent.com/search?q=cache:{}&num=100".format(query)
    r = requests.get(base_url,headers=header)
    return r.text


    
def main():
    populateEmailExtensionsList()

    menu  = ["Home", "Single Extractor", "Bulk Extractor"]
    choice = st.sidebar.selectbox("Menu",menu)
    
    if choice == "Home":
        st.subheader("Search & Extract")
        countryName = st.sidebar.selectbox("Country", countriesList)
        emailExtension = st.sidebar.selectbox("Email Type",emailExtensionsList)
        tasks_list = ["Emails", "URLs", "PhoneNumbers"]
        task_option = st.sidebar.multiselect("Task",tasks_list, default="Emails")
        search_text = st.text_input("Paste Term Here")
        generatedQuery = f"{search_text}+{countryName}+email@{emailExtension}"
        if not search_text=="":
            st.info("Generated Query: {}".format(generatedQuery))
        if st.button("Search & Extract"):
            if generatedQuery is not None:
                text = fetch_query(generatedQuery)
                
                task_mapper = {"Emails":nfx.extract_emails(text), "URLs":nfx.extract_urls(text)
                       ,"PhoneNumbers":nfx.extract_phone_numbers(text)}
                all_results = []
                for task in task_option:
                    result = task_mapper[task]
                    all_results.append(result)
                st.write(all_results)
                with st.expander("Results as DataFrame"):
                    result_df = pd.DataFrame(all_results).T
                    result_df.columns = task_option
                    st.dataframe(result_df)
                    makeDownloadableDf(result_df)
    elif choice == "Single Extractor":
        st.subheader("Extract A Single Term")
        text = st.text_area("Paste Text Here")
        task_option = st.sidebar.selectbox("Task",["Emails","URLs","PhoneNumbers"])
        if st.button("Extract"):
            if task_option == "URLs" :
                results = nfx.extract_emails(text)
            elif task_option == "PhoneNumbers" :
                results = nfx.extract_phone_numbers(text)
            else:
                results = nfx.extract_emails(text)
            
            st.write(results)
            
            with st.expander("Results As DataFrame"):
                result_df = pd.DataFrame({'Results' : results})
                st.dataframe(result_df)
                makeDownloadable(result_df,task_option)
                
            
                
    elif choice == "Bulk Extractor":
        st.subheader("Bulk Extractor")
        text = st.text_area("Paste Text Here")
        tasks_list = ["Emails", "URLs", "PhoneNumbers"]
        task_option = st.sidebar.multiselect("Task",tasks_list, default="Emails")
        
        task_mapper = {"Emails":nfx.extract_emails(text), "URLs":nfx.extract_urls(text)
                       ,"PhoneNumbers":nfx.extract_phone_numbers(text)}
        all_results = []
        for task in task_option:
            result = task_mapper[task]
            
            all_results.append(result)
        st.write(all_results)
        with st.expander("Results as DataFrame"):
            result_df = pd.DataFrame(all_results).T
            result_df.columns = task_option
            st.dataframe(result_df)
            makeDownloadableDf(result_df)
            
    else:
        st.subheader("About")
        
if __name__ == "__main__":
    main()
    
    
    
    
    