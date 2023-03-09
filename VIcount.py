import pandas as pd
from bs4 import BeautifulSoup
import requests
from loguru import logger

# Below function returns the count of videos and images as a tuple when fed with a url
# Functionality is dependant on page structure of the Amazon listing since they vary around
# hence the result might show deviation from actual number for some listings

class VIcount:

    def get_video_image_count(url):
        logger.info(url)
        try:
            HEADERS = {
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64)'
                            'AppleWebKit/537.36 (KHTML, like Gecko)'
                            'Chrome/44.0.2403.157 Safari/537.36'),
            'Accept-Language': 'en-US, en;q=0.5'
            }
            image_count=0
            video_count=0
            req = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(req.content,'html.parser')
            #print(soup.prettify())  
            soup= soup.find('div', {'id': 'imageBlock'})
            #print(soup.prettify())
            soup= soup.find('div', attrs = {'id': 'altImages'})
            thumbnails = soup.find('ul')
            thumbnails=thumbnails.find_all('li')
            for obj in thumbnails:
                if('item' in obj['class']):
                    info=obj.find('span',{'class': 'a-declarative'})
                    data=info['data-thumb-action']
                    #print(data)
                    if('"type":"image"' in data):
                        image_count+=1
                    else:
                        video_count=1+video_count
                        count_text=info.find('span',{'class': 'a-size-mini a-color-secondary video-count a-text-bold a-nowrap'})
                        if(count_text is not None and count_text.text!=" VIDEO"):
                            num_videos=count_text.text.split()[0]
                            if(num_videos.isdigit()):
                                video_count=video_count+int(num_videos)-1                
            return(image_count, video_count)
        except:
            logger.info('Error')
            return(0,0)

# def get_video_check(video_num):
#     if(video_num==0):
#         return False
#     else:
#         return True