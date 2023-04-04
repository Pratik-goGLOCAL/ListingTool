# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 15:05:42 2023

@author: pratik
"""

# Import packages

import pandas as pd
# import language_tool_python
import numpy as np
import re
from tqdm import tqdm
from loguru import logger
from fuzzywuzzy import fuzz
import streamlit as st
from stqdm import stqdm
from time import sleep
from gingerit.gingerit import GingerIt
import VIcount
from PIL import Image
import requests
import cv2

# import Caribe as cb

# Load Data

stqdm.pandas()
special_char = pd.read_csv('Special characters list.csv')
# my_tool = language_tool_python.LanguageToolPublicAPI('en-US')
# gf = Gramformer(models=1) # 0 = detector, 1 = highlighter, 2 = corrector, 3 = all

parser = GingerIt()
messages = {'ASIN':['ASIN of the product'],'MRP':['Max Retail Price'], 'aplus_images':['Image links of the Aplus content'],
 'aplus_text':['Text extracted in Aplus content'], 'brand':['Brand Name'], 'bullets':['Bullet Points extracted'], 
 'country_of_origin':['Country of Product Origin'], 'dimensions':['Dimesions details available in Product Information Section'],
 'discount':['Discount Available on the Product Price'], 'description':['Product Description Available'],
 'image_links':['Product Image links'],'price':['Price of the Product'], 'net_quantity':['Quantity of items in the product'],
 'offers':['Offers available on the Product Listing'], 'ratings':['Ratings givent the product'],
 'ratings_breakdown':['Breakdown of Ratings for 1,2,3,4,5 stars'], 'ratings_count':['Number of ratings'], 'title':['Title of the Product'], 
 'url':['Product URL'], 'video_links':['Video links of listed products'],'weight':['Weight of the Product']}
###########################################################################################################
# Helper Functions
###########################################################################################################
## Sentence Case
def sentence_case(brand_name,title,brand_present_title):
    first_word = title.strip().split(' ')[0]
#     print(brand_name,first_word,brand_present_title)
    if brand_present_title==1:
        if brand_name.strip()[0]==first_word[0]:
            res = 1
        else:
            res = 0
    else:
        if first_word[0].isupper():
            res = 1
        else:
            res = 0
#     print(res)
    return res

###########################################################################################################

# def spellcheck(txt,model):
#     res = model.check(txt)
#     logger.info(res)
#     if len(res)>0:
#         flg = 0
#     else:
#         flg = 1
#     return [flg,res]

def runGinger(txt,my_tool):
    if txt=='NA':
        return [0,['No Description'],txt]
    # logger.info(txt)
    try:
        sentences = [x.strip().lstrip(', ') for x in txt.strip().split('\n')]
        logger.info('sentences are : {}'.format(sentences))
        flg = 1
        corrections = []
        result = []
        for sentence in sentences:
            if len(sentence)>600:
                logger.info('sentence char len is greater than 600')
                order = "[+-]?\d+\.\d+"
                p = re.compile(order)
                floats = p.findall(sentence)
                logger.info(floats)
                first_str = sentence
                float_replaces = []
                for f in set(floats):
                    first_str = first_str.replace(f,f.replace('.','point'))
                    float_replaces.append([f.replace('.','point'),f])
                    logger.info(first_str)
                delimiters_regex = "[?.!|]"
                delimiters_re = re.compile(delimiters_regex)
                delimiters = delimiters_re.findall(first_str)
                logger.info('delimiters are {}'.format(delimiters))
                lines = re.split( r'[?.!|]',first_str)
                if len(lines)>len(delimiters):
                    delimiters.append('')
                for i,d in zip(lines,delimiters):
                    [i := i.replace(a, b) for a, b in float_replaces]
                    parse_res = my_tool.parse(i)
                    if len(parse_res['corrections'])>0:
                        flg = 0
                    result.append(parse_res['result']+d)
                    corrections.append(parse_res['corrections'])
            else:
                parse_res = my_tool.parse(sentence)
                if len(parse_res['corrections'])>0:
                    flg = 0
                result.append(parse_res['result'])
                corrections.append(parse_res['corrections'])
    except:
        return [0,['API Error'],[txt]]
    return [flg,corrections,result]

# def spellcheck(txt):
#     samecheck = lambda x,y:1 if x==y else 0
#     sentence = [x.strip().lstrip(', ') for x in txt.strip().split('\n')]
#     corrected_text = ''
#     for first_str in sentence:
#         corrected_text.append(cb.t5_kes_corrector(first_str))
#     '\n'.join(corrected_text)
#     return 

###########################################################################################################
## Special Character Check
def special_char_check(x):
    if len(set(special_char['chars'])) - len(set(special_char['chars'].tolist())-set(x))>0:
        return 0
    else:
        return 1

###########################################################################################################
## Get complete Title Flag
def get_Title_flag(data):
    ## Brand Name Present
    bn_check = lambda x,y:1 if y.strip().lower().find(x.strip().lower())==0 else 0

    t1 = st.empty()
    t1.caption('Brand Check: ')
    data['title_brand_present'] = data[['brand','title']].progress_apply(lambda x:bn_check(x.brand,x.title),axis = 1)
    messages['title_brand_present'] = ['Check to see if Title starts with brand name']
    ## Sentence Case
    t2 = st.empty()
    t2.caption('Sentence Case Check: ')
    data['title_sentence_case'] = data[['brand','title',"title_brand_present"]].progress_apply(lambda x:sentence_case(x.brand,x.title,x.title_brand_present),axis = 1)
    messages['title_sentence_case'] = ['Check to see if Title is written in sentence case']
    ## Spell Check
    t3 = st.empty()
    t3.caption('Spell and Grammar Check: ')
    # data[['title_spellcheck','title_Corrected_text']] = data['title'].progress_apply(lambda x:spellcheck(x,my_tool)).tolist()
    data[['title_spellcheck','title_corrections','title_Corrected_text']] =  pd.DataFrame(data['title'].progress_apply(lambda x: runGinger(x,parser)).tolist())
    # data['title_Corrected_text'] =  data['title'].progress_apply(lambda x: cb.t5_kes_corrector((x)))
    
    # data['title_spellcheck'] = data[['title_Corrected_text','title']].apply(lambda x: samecheck(x.title_Corrected_text,x.title),axis = 1)
    data['final_title_check_flag'] = data[['title_brand_present','title_sentence_case','title_spellcheck']].product(axis = 1)
    # messages['title_spellcheck'] = ['Check to see if Title is grammatically correct']
    messages['title_Corrected_text'] = ['Corrected Title text after spellcheck']
    messages['title_corrections'] = ['Correct Title text after spellcheck']
    messages['final_title_check_flag'] = ['Overall Title Check Flag']
    return data['final_title_check_flag']

###########################################################################################################
## Get complete Description Flag
def get_Description_flag(data):
    ## Special Character Check
    d1 = st.empty()
    d1.caption('Special Character Check: ')
    data['description_special_chr_check'] = data['description'].apply(lambda x:special_char_check(x))
    messages['description_special_chr_check'] = ['Check to see if Description contains any special characters']
    ## Characters Constrained
    d2 = st.empty()
    d2.caption('Number of characters <2000 Check: ')
    data['description_char_constrained_2000'] = data['description'].apply(lambda x:1 if len(x.strip())<=2000 else 0)
    messages['description_char_constrained_2000'] = ['Check to see if number of characters in Description are less that 2000']
    ## Multiline Check
    def multiline_check(first_str):
        order = "[+-]?\d+\.\d+"
        first_str = re.sub(order, '', first_str)
        lines = re.split( r'[?.!]',first_str)
        if len(lines)>1:
            return 1
        else:
            return 0
    
    d3 = st.empty()
    d3.caption('Mutiline Check: ')
    data['description_multiline_check'] = data['description'].apply(lambda x:multiline_check(x))
    messages['description_multiline_check'] = ['Check to see if Description contains multiple lines']

    ## Spell Check 
    # data[['description_spellcheck','description_Corrected_text']] = data['description'].progress_apply(lambda x:spellcheck(x,my_tool)).tolist()
    d4 = st.empty()
    d4.caption('Spell Grammar Check: ')
    data[['description_spellcheck','description_corrections','description_Corrected_text']] =  pd.DataFrame(data['description'].progress_apply(lambda x: runGinger(x,parser)).tolist())
    # data['description_Corrected_text'] =  data['description'].progress_apply(lambda x: cb.t5_kes_corrector((x)))
    
    # data['description_spellcheck'] = data[['description_Corrected_text','description']].apply(lambda x: samecheck(x.description_Corrected_text,x.description),axis = 1)
    messages['description_spellcheck'] = ['Check to see if Description is grammatically correct']
    messages['description_corrections'] = ['Correct Description text after spellcheck']
    messages['description_Corrected_text'] = ['Corrected Description text after spellcheck']

    ## Final Description check Flag
    data['final_description_check_flag'] = data[['description_special_chr_check','description_char_constrained_2000','description_multiline_check','description_spellcheck']].product(axis = 1)
    messages['final_description_check_flag'] = ['Overall Description Check Flag']

    return data['final_description_check_flag']

###########################################################################################################

## Get complete BulletPoints Flag
def get_BulletPoints_flag(data):
    ## Special Character check
    b1 = st.empty()
    b1.caption('Special Character Check: ')
    data['bullets_special_chr_check'] = data['bullets'].apply(lambda x:special_char_check(x))
    messages['bullets_special_chr_check'] = ['Check to see if Bullets contain any special charater']

    ## Number of bullet points check (atleast 3 points)
    b2 = st.empty()
    b2.caption('Atleast 3 bullet Points Check: ')
    data['bullets_number_check'] = data['bullets'].apply(lambda x:1 if x.count('\n')>=2 else 0)
    messages['bullets_number_check'] = ['Check if the number of bullet points is greater than 3']

    ## Bullet Points start with capital letter check
    b3 = st.empty()
    b3.caption('Bullet Points start with capital letter Check: ')
    data['bullets_first_capital_check'] = data['bullets'].apply(lambda x: int(''.join([s.strip().lstrip(', ')[0] for s in x.strip().split('\n')]).isupper()) )
    messages['bullets_first_capital_check'] = ['Check if the bullet points start with a capital letter']

    ## Spell Check
    # data[['bullets_spellcheck','bullets_Corrected_text']] = data['bullets'].progress_apply(lambda x:spellcheck(x,my_tool)).tolist()
    b4 = st.empty()
    b4.caption('Spell Grammar Check Check: ')
    data[['bullets_spellcheck','bullets_corrections','bullets_Corrected_text']] =  pd.DataFrame(data['bullets'].progress_apply(lambda x: runGinger(x,parser)).tolist())
    # data['bullets_Corrected_text'] =  data['bullets'].progress_apply(lambda x: cb.t5_kes_corrector((x)))
    # data['bullets_spellcheck'] = data[['bullets_Corrected_text','bullets']].apply(lambda x: samecheck(x.bullets_Corrected_text,x.bullets),axis = 1)
    messages['bullets_spellcheck'] = ['Check if the Bullet points are grammatically correct']
    messages['bullets_corrections'] = ['Correct Bullet points text after spellcheck']
    messages['bullets_Corrected_text'] = ['Corrected Bullet Points text']

    ## Final Bullet Points check Flag
    data['final_bullet_point_check_flag'] = data[['bullets_special_chr_check','bullets_number_check','bullets_first_capital_check','bullets_spellcheck']].product(axis = 1)
    messages['final_bullet_point_check_flag'] = ['Overall Bullet Points Check Flag']

    return data['final_bullet_point_check_flag']

###########################################################################################################
## Get complete Spell Check Flag
def get_sum(lst):
    return sum(lst)

def get_SpellCheck_flag(data):
    s1 = st.empty()
    s1.caption('Overall Spell-Check: ')
    data['final_entire_spellcheck'] = data[['title_spellcheck','description_spellcheck','bullets_spellcheck']].apply(lambda x:1 if get_sum([x.title_spellcheck,x.description_spellcheck,x.bullets_spellcheck])==3 else 0,axis = 1)
    messages['final_entire_spellcheck'] = ['Overall Spell Check Flag']
    return data['final_entire_spellcheck']

###########################################################################################################
## Get complete Dimension Check Flag
def qc_dim(unit,values):
#     metric = {'meter':['m','meter'],
#     'centimeter':['cm','cms','centimeter'],
#     'millimeter':['mm','millimeter'],
#     'inches':['inch','inches']
#     'litre':['l','lit','litre'],
#     'gram':['g','gm','gram'],
#     'kilogram':['kg','kgms','kilogram']}
#     metric = ['meter','centimeter','millimeter','kilometer','inches','foot']
    metric2 = ['m','cms','mm','km','inches','ft']
    metric_change = [1,0.01,0.001,1000,0.0254,0.0348]
    metric_unit= []
    logger.info('unit for qc {}\nvalue for qc {}'.format(unit,values))
    for u in unit:
        umetric_ratio = []
        for m in metric2:
            umetric_ratio.append(fuzz.ratio(u,m))
        metric_unit.append(metric2[np.array(umetric_ratio).argmax()])
    logger.info('metric_unit {}'.format(metric_unit))
    updated_values = [float(v)*metric_change[metric2.index(i)] for i,v in zip(metric_unit,values)]
    logger.info('updated values {}'.format(updated_values))
    if len(set(metric_unit))>1:
        qc_res = [0,updated_values]
    else:
        qc_res = [1,updated_values]
    
    return qc_res

def format_dim(dim):
    logger.info('initial dim {}'.format(dim))
    dim = dim.replace(' ','').lower()
    dim = dim.replace('x',' ')
    units = []
    for unit in re.finditer("[a-z]+",dim):
        units.append(unit.group())
    values = []
    for val in re.finditer("((\d*[.])?\d+)+",dim):
        values.append(val.group())
    logger.info('unit is {} and values are {}'.format(units,values))
    return [units,values]

def check_values(value_list):
    logger.info('value_list for check values {}'.format(value_list))
    max_len = [len(l) for l in value_list]
    if len(set(max_len))>1:
        logger.info('The dimensions length do not match!!')
        return 0
    value_list = [sorted(l) for l in value_list]
    logger.info('after sort {}'.format(value_list))
    same_val_list = np.array(value_list).T.tolist()
    logger.info('transform for each dim {}'.format(same_val_list))
    res = 1
    for v in same_val_list:
        ratio_list = [v[i]/v[0] for i in range(len(v))]
        logger.info('ratio list for list {} {}'.format(v,ratio_list))
        res*=np.prod([1 if (i<=1.05 and i>=0.95) else 0 for i in ratio_list])
    logger.info('res {}'.format(res))
    return res

def get_dimensions(text):
    iters = re.finditer("(((((\d*[.])?\d+) ?[a-zA-Z]+ ?)[xX] ?(((\d*[.])?\d+) ?[a-zA-Z]+ ?)[xX] ?(((\d*[.])?\d+) ?[a-zA-Z]+ ?))|((((\d*[.])?\d+) ?[a-z]+ ?)[xX] ?(((\d*[.])?\d+) ?[a-zA-Z]+ ?)))|(((((\d*[.])?\d+) ?)[xX] ?(((\d*[.])?\d+) ?)[xX] ?(((\d*[.])?\d+) ?[a-zA-Z]+))|((((\d*[.])?\d+) ?)[xX] ?(((\d*[.])?\d+) ?[a-zA-Z]+)))",text)
    matched_strings = []
    for i in iters:
        matched_strings.append(i.group())
    logger.info('matched_strings {} and length is {}'.format(matched_strings,len(matched_strings)==0))
    if len(matched_strings)==0:
        return 0
    same_unit_in_dim = 1
    multi_units_value = []
    for dim in matched_strings:
        units, values = format_dim(dim)
        if len(units)==1:
            units = units*len(values)
        qc_res = qc_dim(units,values)
        same_unit_in_dim*=qc_res[0]
        multi_units_value.append(qc_res[1])
    # dimres = [1,same_unit_in_dim,check_values(multi_units_value)]
    return check_values(multi_units_value)
            
def get_Dimensions_flag(data):
    dim1 = st.empty()
    dim1.caption('Dimensions Check: ')
    data['complete_data'] = data['title']+'. '+ data['description']+'. '+data['bullets'] + '. ' + data['dimensions']#+
    data['final_dimensionality_check'] = data['complete_data'].progress_apply(lambda x: get_dimensions(x))
    messages['final_dimensionality_check'] = ['Dimensions Check Flag']
    # logger.info(data['dimension_check_res'])
    # data[['final_dimensionality_check','same_unit_in_dim','dimensionality_inter_check']] = data['dimension_check_res'].str.split('__%__')
    # data.drop('dimension_check_res',axis = 1,inplace = True)
    return data['final_dimensionality_check']

###########################################################################################################
## Get complete Spell Check Flag
def get_SentenceCase_flag(data):
    data['final_sentence_case_check'] = data['title_sentence_case']
    messages['final_sentence_case_check'] = ['Title Sentence Case Flag']

    return data['final_sentence_case_check']

##############################################################################################################
## Get Video Image Count
def video_image_count(data):
    data[['Image_Count','Video_count']] = data['url'].progress_apply(lambda x:VIcount.VIcount.get_video_image_count(x)).tolist()
    # return data['Image_Count','Video_count']

##############################################################################################################
## Get A+content Flag
def get_aplus_check_flag(data):
    ap1 = st.empty()
    ap1.caption('A+ Content presence check: ')
    data['aplus_content_check'] = data['aplus_text'].apply(lambda x:1 if x!='NA' else 0)
    messages['aplus_content_check'] = ['Check to see if A+ content is available']

    ap2 = st.empty()
    ap2.caption('Special Character Check: ')
    data['aplus_text_special_chr_check'] = data['aplus_text'].apply(lambda x:special_char_check(x))
    messages['aplus_text_special_chr_check'] = ['Check to see if A+ Text contains any special charater']

    ap3 = st.empty()
    ap3.caption('Spell Grammar Check Check: ')
    data[['aplus_text_spellcheck','aplus_text_corrections','aplus_text_Corrected_text']] =  pd.DataFrame(data['aplus_text'].progress_apply(lambda x: runGinger(x,parser)).tolist())
    messages['aplus_text_spellcheck'] = ['Check if the A+ content is grammatically correct']
    messages['aplus_text_corrections'] = ['Correct A+ content text after spellcheck']
    messages['aplus_text_Corrected_text'] = ['Corrected A+ content text']

    ## Final A+ content check Flag
    data['final_aplus_check_flag'] = data[['aplus_content_check','aplus_text_special_chr_check','aplus_text_spellcheck']].product(axis = 1)
    messages['final_aplus_check_flag'] = ['Overall A+ content Check Flag']


##############################################################################################################
## Ratings count individually
def get_fourplus_fraction(fract_str):
    fract_list = fract_str.split(',')
    logger.info('Ratings Split {}'.format(fract_list))
    total_frac = 0
    for rating in fract_list:
        logger.info('{} contains 5 star or 4 star {}'.format(rating,'5 star' in rating or '4 star' in rating))
        if '5 star' in rating or '4 star' in rating:
            logger.info('ratings {}'.format(rating))
            logger.info('{}'.format(rating.split('%')[0]))
            total_frac+=int(rating.split('%')[0])
            logger.info('Total Fraction {}'.format(total_frac))
    return total_frac/100

def get_ratings_count(data):
    logger.info('Data Size = {}'.format(data.shape))
    data['fraction_4plus_ratings'] = data['ratings_breakdown'].apply(lambda x: get_fourplus_fraction(x))

##############################################################################################################
## Object Detection 
def object_detect_res(links):
    links = links.split(',')
    output_res_file = []
    lifestyle_flag = []
    for image_path in links:
        logger.info('Object Detection API Call for {}'.format(image_path))
        # im = Image.open(requests.get(image_path,stream=True).raw).convert("RGB")
        # im = np.array(im)
        # image_path = '../Detectron_2.0/DataStore/Inputs/test_img.png'
        # cv2.imwrite(image_path,im)
        # response = requests.get(f"{'http://52.204.224.231:8024/Yolo9000-predictions?image_path=DataStore%2FInputs%2Ftest_img.png'}")
        response = requests.get(f"{'http://52.204.224.231:8022/detectron2-predictions?image_path={}'.format(image_path)}")
        logger.info('Got Response!! for {}'.format(image_path))
        res = response.json()
        logger.info('obtained_res {}'.format(res))
        output_res_file.append(res)
        logger.info('Number of classes detected {}'.format(res['output_classes']))
        if len(set(res['output_classes']))>1:
            lifestyle_flag.append(1)
        else:
            lifestyle_flag.append(0)
    return output_res_file,lifestyle_flag
def get_lifestyle_flag(data):
    data[['object_detect','pred_lifestyle_flags']] = pd.DataFrame(data['image_links'].progress_apply(lambda x: object_detect_res(x)).tolist())
        

##############################################################################################################
## Object Text Detection and Infographics Flag

def check_text_position(image, object_boxes,ocr_boxes):
    # object_boxes = object_detection_res[x][1]
    # ocr_boxes = ocr_res[x][0].splitlines()
    # im = Image.open(requests.get(image_path,stream=True).raw).convert("RGB")
    # image = np.array(im)
    h, w, _ = np.array(image).shape
    for obj in object_boxes:
        logger.info('obj is {}'.format(obj))
        ox1,ox2,ox3,ox4 = int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3])
        for txbox in ocr_boxes:
            logger.info('Text Box {}'.format(txbox))
            b = txbox#.split(' ')
            tx1,tx2,tx3,tx4 = int(b[0]), int(b[1]), int(b[4]),int(b[5])
            if tx3<ox3 and tx4<ox4:
                return 1
    return 0

def get_ocr_detection(links,boxes):
    links = links.split(',')
    output_res_file = []
    infographics_flag = []
    image_links = []
    for image_path,box in zip(links,boxes):
        logger.info('OCR API Call for {}'.format(image_path))
        im = Image.open(requests.get(image_path,stream=True).raw).convert("RGB")
        im = np.array(im)
        # image_path = '../MMOCR/DataStore/Inputs/test_img.png'
        # cv2.imwrite(image_path,im)
        response = requests.get(f"{'http://52.204.224.231:8021/mmocr-predictions?image_path={}'.format(image_path)}")
        res = response.json()
        logger.info('Results of API call are {}'.format(res))
        output_res_file.append(res)
        infographics_flag.append(check_text_position(im,box['bbox'],res['bbox']))
    return output_res_file,infographics_flag

def get_infographics_flag(data):
    data[['OCR_detect','pred_infographics_flags']] = pd.DataFrame(data[['image_links','object_detect']].progress_apply(lambda x: get_ocr_detection(x.image_links,x.object_detect), axis= 1).tolist())

##############################################################################################################
## Get all the flags
def QC_check1(data):
    text1 = st.empty()
    logger.info('Title Check Started')
    text1.write('Title Check Started')
    data['final_title_check_flag'] = get_Title_flag(data)
    logger.info('Title Check Completed!!!')
    text1.write('Title Check Completed!!!')

    text2 = st.empty()
    logger.info('Description Check Started')
    text2.write('Description Check Started')
    data['final_description_check_flag'] = get_Description_flag(data)
    logger.info('Description Check Completed!!!')
    text2.write('Description Check Completed!!!')

    text3 = st.empty()
    logger.info('Bullet Points Check Started')
    text3.write('Bullet Points Check Started')
    data['final_bullet_point_check_flag'] = get_BulletPoints_flag(data)
    logger.info('Bullet Points Check Completed!!!')
    text3.write('Bullet Points Check Completed!!!')

    data['Grade1'] = data[['final_title_check_flag','final_description_check_flag','final_bullet_point_check_flag']].sum(axis = 1)
    data['Grade1'] = data['Grade1'].apply(lambda x: 'A' if x==3 else('B' if x>0 else 'C'))
    messages['Grade1'] = ['Grade 1 Score']

    text4 = st.empty()
    logger.info('Entile Spell Check Started')
    text4.write('Entile Spell Check Started')
    data['final_entire_spellcheck'] = get_SpellCheck_flag(data.copy())
    logger.info('Entile Spell Check Completed!!!')
    text4.write('Entile Spell Check Completed!!!')

    text5 = st.empty()
    logger.info('Dimensionality Check Started')
    text5.write('Dimensionality Check Started')
    # data[['final_dimensionality_check','same_unit_in_dim','dimensionality_inter_check']] = get_Dimensions_flag(data.copy())
    data['final_dimensionality_check']= get_Dimensions_flag(data.copy())
    logger.info('Dimensionality Check Completed!!!')
    text5.write('Dimensionality Check Completed!!!')

    text6 = st.empty()
    logger.info('Sentence Case Check Started')
    text6.write('Sentence Case Check Started')
    data['final_sentence_case_check'] = get_SentenceCase_flag(data.copy())
    logger.info('Sentence Case Check Completed!!!')
    text6.write('Sentence Case Check Completed!!!')

    text7 = st.empty()
    logger.info('Video Image Count check started')
    text7.write('Video Image Count check started')
    video_image_count(data)
    messages['Image_Count'] = ['Number of images in the listing']
    messages['Video_Count'] = ['Number of videos in the listing']
    logger.info('Video Image Count check Completed!!!')

    # logger.info('Video Image Count check started')
    # text6.write('Video Image Count check started')
    # video_image_count(data)
    # messages['Image_Count'] = ['Number of images in the listing']
    # messages['Video_Count'] = ['Number of videos in the listing']
    # logger.info('Video Image Count check Completed!!!')

    text8 = st.empty()
    logger.info('A+ content check started')
    text8.write('A+ content check started')
    get_aplus_check_flag(data)
    logger.info('A+ content check Completed!!!')
    
    data['Grade2'] = data[['final_entire_spellcheck','final_dimensionality_check','final_sentence_case_check','final_aplus_check_flag']].sum(axis = 1)
    data['Grade2'] = data['Grade2'].apply(lambda x: 'A' if x==4 else('B' if x==3 else 'C'))
    messages['Grade2'] = ['Grade 2 Score']

    text9 = st.empty()
    text9.write('Fraction of 4+ ratings started')
    logger.info('Get Fraction of 4+ ratings')
    get_ratings_count(data)
    messages['fraction_4plus_ratings'] = ['The faction 4+ ratings out of the total ratings']
    logger.info('Fraction of 4+ ratings check Completed!!!')

    text10 = st.empty()
    text10.write('Lifestyle Image check started')
    logger.info('Object Detection and Lifestyle Image Flag')
    get_lifestyle_flag(data)
    messages['object_detect'] = ['Detected Objects Results']
    messages['pred_lifestyle_flags'] = ['Predicted Lifestyle Flag for the Image']
    logger.info('Lifestyle Image check Completed!!!')

    text11 = st.empty()
    text11.write('Infographics Image check started')
    logger.info('OCR Detection and Infographcics Image Flag')
    get_infographics_flag(data)
    messages['OCR_detect'] = ['OCR Detected Text results']
    messages['pred_infographics_flags'] = ['Predicted Infographics Flag']
    logger.info('Infographics Image check Completed!!!')

    tooltips_df = pd.DataFrame(messages)
    data.style.set_tooltips(tooltips_df)
    # st.write(messages)
    tooltips_df.to_csv('DataStore/DataDict.csv',index=False)
    st.dataframe(tooltips_df)
    return data