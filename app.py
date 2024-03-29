import pandas as pd
import numpy as np
import os
import streamlit as st
import pickle
# import pickle as pkl
import subprocess
import json
import scrapy
import requests
from scrapy.crawler import CrawlerProcess,CrawlerRunner
from urllib.parse import urljoin
import re
import sys
# sys.path.append('/ListingQC')
from loguru import  logger
import excel_checks
from datetime import datetime
from send_email import send_email

st.set_page_config(
    page_title="Listing QC"
)

st.title("Listing QC")
# st.sidebar.success("Select Action")


# data = pd.read_csv('excel_check.csv')
# data.fillna('NULL',inplace = True)

with open('amazon_categories.pickle', 'rb') as handle:
    amazon_categories = pickle.load(handle)

# Initialize Variables
if "r_email" not in st.session_state:
    st.session_state["r_email"] = "NA"
if "Brand_name" not in st.session_state:
    st.session_state["Brand_name"] = ""
if "Region" not in st.session_state:
    st.session_state["Region"] = ""
if "Market_Place" not in st.session_state:
    st.session_state["Market_Place"] = ""
if "ASIN" not in st.session_state:
    st.session_state["ASIN"] = ""
if "category" not in st.session_state:
    st.session_state["category"] = ""
# Enter email to send the results on 
email_place = st.empty()
r_email = email_place.text_input('Enter e-mail address to get results via mail', st.session_state["r_email"])
st.session_state["r_email"]= r_email
logger.info('r_email is {}'.format(r_email))
# Select the region ,'USA','Europe','Asia'
region_place = st.empty()
region = region_place.multiselect(label='Select Region',
                    options=['India'], 
                    default = ['India'])
# st.write('The options selected are:', region)
st.session_state['Region'] = region

# Select Market Places
marketplace_place = st.empty()
region_marketplace = {'India':['Amazon'],
                    'USA':['Amazon','shopify','Walmart'],
                    'Europe':['Amazon','shopify','Walmart'],
                    'Asia':['Amazon','shopify','Walmart']}
available_marketplaces = list(set(np.ravel([region_marketplace[i] for i in ['USA','Europe']])))   
marketplace = marketplace_place.multiselect(label='Select Market Places',
                    options=available_marketplaces,
                    default = ['Amazon'],disabled=False)
# st.write('The options selected are:', marketplace)
st.session_state['Market_Place'] = marketplace

# asin_brand_place = st.empty()

# asin_brand = asin_brand_place.selectbox(label='Select ASIN or Brand',
#                     options=['Brand Name','ASIN'],disabled=False)
# st.session_state['asin_brand'] = asin_brand

category_place = st.empty()
category = category_place.selectbox(label='Select the Category',
                    options=list(amazon_categories.keys()) ,disabled=False)
# st.write('The options selected are:', marketplace)
st.session_state['category'] = category
# logger.info(st.session_state['asin_brand'])
# Select the Brand Name
# if st.session_state['asin_brand']=='ASIN':
asin_place = st.empty()
asins = asin_place.text_input("Search for an ASIN", st.session_state["ASIN"])
# logger.info([x.strip() for x in search_text.split(',')])

st.session_state["ASIN"] = asins if len(asins)>0 else 'NA'#[x.strip() for x in search_text.split(',')]

brandname_place = st.empty()
brand = brandname_place.text_input("Search for a Brand Name (if multiple then separate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"])

st.session_state["Brand_name"] =brand #[x.strip() for x in search_text.split(',')]
submitplace = st.empty()
submit = submitplace.button("Submit",disabled=False,key='submit1')
stop = st.button('Stop')
db = st.empty()
# pd.DataFrame([brand_name],columns=['keyword_list']).to_csv('DataStore/keyword_list.csv',index=False)
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
# def do_scrapping()
if not stop and submit:
    submitplace.button("Submit",disabled=True,key='submit2')
    email_place.text_input('Enter e-mail address to get results via mail', st.session_state["r_email"],disabled=True,key = 'emailplace')
    region_place.multiselect(label='Select Region',
                    options=['India'], 
                    default = ['India'],disabled = True,key = 'regionplace')
    marketplace_place.multiselect(label='Select Market Places',
                    options=available_marketplaces,
                    default = ['Amazon'],disabled = True,key = 'marketplace')
    
    asin_place.text_input("Search for an ASIN", st.session_state["ASIN"],disabled = True,key = 'asinplace')
    brandname_place.text_input("Search for a Brand Name (if multiple then separate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"],disabled = True,key = 'brandplace')
    category_place.selectbox(label='Select the Category',
                    options=list(amazon_categories.keys()) ,disabled=True,key = 'category')
    st.caption('The Scraping+Listing QC Checks are in process. PLEASE DO NOT CLOSE THE TAB')
    st.caption('To stop the process press the Stop button and refresh the page')
    r_email = 'NA' if len(r_email)>0 else r_email
    query = {'brand':st.session_state['Brand_name'],
             'asin_list': st.session_state['ASIN'],
             'category':st.session_state['category'],
             'r_email': st.session_state["r_email"]}
    logger.info('json query is {}'.format(query) )
    qc_response = requests.post(f"http://52.204.224.231:8031/ListingQC",json=query)
    if r_email!="NA":
        st.caption('The results are successfully sent on you email address !!')
    res_df = pd.read_json(qc_response.json(), orient='records')
    # textplace = st.empty()
    # textplace.subheader("Scraping Started for {} ".format(search_text))
    # ##################################################################################################################################
    # # import subprocess
    # # variable = 'Run_Spider.py'
    # # subprocess.call(f"{sys.executable} " + variable, shell=True)
    # # try:
    # #     df = pd.read_csv('DataStore/Scrapy_Res.csv')
    # #     df.fillna('NA',inplace = True)  
    # #     # df['product_brand'] = df['product_brand'].apply(lambda x:st.session_state['Brand_name'].title() if x=='NA' else x).copy()
    # # except:
    # #     df = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
    # #     df.fillna('NA',inplace = True)
    # # # listing_cols = ['ASIN', 'MRP', 'aplus_images', 'aplus_text', 'brand', 'bullets', 'description', 'image_links',
    # # #                 'price', 'ratings', 'ratings_count', 'title', 'url', 'video_links']
    # # df = df#[listing_cols]
    # ##################################################################################################################################
    # logger.info('asin_brand:{}, search_text:{}, category:{}'.format(st.session_state['asin_brand'],search_text,st.session_state['category']))
    # response = requests.get(f"{'http://52.204.224.231:8027/Scrapping?brand_asin={}&search_text={}&category={}'.format(st.session_state['asin_brand'],search_text,st.session_state['category'])}")
    # logger.info('We got the Response form API')
    # dict = json.loads(response.json())
    # logger.info('Reponse JSON dict {}'.format(dict))
    # df = pd.DataFrame.from_dict(dict)
    # logger.info('DataFrame Head is {}'.format(df.head()))
    # ##################################################################################################################################
    # textplace.subheader('Scraping Complete!!!')
    # # st.write(df)
    # minpdata = 2
    # timetorun = str(round(len(df)*minpdata/60,1))+' hours' if (len(df)*minpdata)/60 >1 else str(len(df)*minpdata)+' minutes'
    # st.caption('Estimated time for completion is about {} '.format(timetorun))
    # # st.write(os.listdir('DataStore/'))
    # st.subheader('QC_Checks Started')
    # df.fillna('NA',inplace = True)
    # res_df = excel_checks.QC_check1(df)
    # # res_df = df.copy()
    # # res_df = res_df.drop(['product_weight','product_material','product_category','item_height','item_length','item_width'], axis = 1)
    # st.subheader('QC Checks Completed!!!')
    submitplace.button("Submit",disabled=False,key='submit3')
    email_place.text_input('Enter e-mail address to get results via mail', st.session_state["r_email"],disabled=False,key = 'emailplace3')
    region_place.multiselect(label='Select Region',
                    options=['India'], 
                    default = ['India'],disabled = False,key = 'regionplace3')
    marketplace_place.multiselect(label='Select Market Places',
                    options=available_marketplaces,
                    default = ['Amazon'],disabled = False,key = 'marketplace3')
    asin_place.text_input("Search for an ASIN", st.session_state["ASIN"],disabled = False,key = 'asinplace3')
    brandname_place.text_input("Search for a Brand Name (if multiple then separate using ' , ') e.g. Yellow Chimes", st.session_state["Brand_name"],disabled = False,key = 'brandplace3')
    category_place.selectbox(label='Select the Category',
                    options=list(amazon_categories.keys()) ,disabled=True,key = 'category3')
    # st.dataframe(res_df[[col for col in res_df.columns if 'Corrected_text' not in col]])
    # st.dataframe(res_df)

    # now = datetime.now()
    # dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    # filename = 'Listing_QC_results_'+dt_string+'.csv'
    # res_df.to_csv('DataStore/'+filename ,index = False)
    

    # if 'ScrapedData_pg_v1.csv' in os.listdir('DataStore/'):
    #     # st.write('TRUE')
    #     overall_data = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
    # else:
    #     # st.write('FALSE')
    #     overall_data = pd.DataFrame(columns=listing_cols)
    # overall_data_new = pd.concat([df,overall_data])

    # st.write('Total {} unique product Asin found, Data Size: {}'.format(df['product_asin'].nunique(),df.shape))
    # st.write('Overall Data Size is {}'.format(overall_data_new.shape))
    # overall_data_new.to_csv('DataStore/ScrapedData_pg_v1.csv',index=False)
    csv = convert_df(res_df)
    db.download_button(
        label="Download",
        data=csv,
        file_name='ListingQC_res.csv',
        mime='text/csv',
    )
    # if len(r_email)>0:
    #     send_email(r_email,filename)