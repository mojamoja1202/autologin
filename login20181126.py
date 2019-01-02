#20181123加入上傳圖片至雲端硬碟分析的碼
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import time
import random
from selenium import webdriver
from PIL import Image



'''
add from ocr using google driver url:https://tanaikech.github.io/2017/05/02/ocr-using-google-drive-api/
'''
import os
import io
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None



allTeacher=['533604','_2453','_2451','_149810','_14552','_111762','_195629','_15032','_111743','_111735','_111738','_111737','_14194','_111739','_111740','_111742','_15025','_15027','_15031','_15044','_15029','_15048','_15047','_14190','_15013','_15041','_15038','_15052','_15017','_15018','_15019','_15020','_15022','_15049','_15046','_182031','_111756','_182035','_15030','_200844','_200845','_111770','_15045','_15034','_15035','_15036','_137254','_182039','_15040','_111750','_111736','_15053','_15054','_15042','_14206','_15050','_179943']
rndTeacher=random.choice(allTeacher)
driver=webdriver.Chrome('chromedriver.exe')
driver.get('https://exam.tcte.edu.tw/tbt_html')
time.sleep(5)
driver.find_element_by_xpath("//select[@name='identity']/option[@value='siso']").click()
time.sleep(1)
driver.find_element_by_name("sch_code").send_keys("533604")
driver.find_element_by_name("button").click()
time.sleep(5)

#抓取驗證碼的圖
driver.save_screenshot('test.png')
element=driver.find_element_by_id('sch_imgcode')
left=element.location['x']
right=element.location['x']+element.size['width']
top=element.location['y']
bottom=element.location['y']+element.size['height']
img=Image.open('test.png')
img=img.crop((left,top,right,bottom))
img.save('captcha.png','png')

#20181123將圖片上傳到google driver
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))


# Call the Drive v3 API
results = service.files().list(
    pageSize=10, fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])

if not items:
    print('No files found.')
else:
    print('Files:')
    for item in items:
        print(u'{0} ({1})'.format(item['name'], item['id']))


#上傳圖片
imgfile = 'captcha.png'
txtfile = 'output.txt'

mime = 'application/vnd.google-apps.document'
res = service.files().create(
    body={
        'name': imgfile,
        'mimeType': mime
    },
    media_body=MediaFileUpload(imgfile, mimetype=mime, resumable=True)
).execute()

downloader = MediaIoBaseDownload(
    io.FileIO(txtfile, 'wb'),
    service.files().export_media(fileId=res['id'], mimeType="text/plain")
)
done = False
while done is False:
    status, done = downloader.next_chunk()

service.files().delete(fileId=res['id']).execute()
print("Done.")


#讀取output.txt，提取驗證碼
fp=open('output.txt','r')
lines=fp.readlines()
fp.close
linesNum=len(lines)-1

captcha=lines[linesNum]

captcha=captcha.replace(' ','')

print(captcha)




#輸入密碼及驗證碼
driver.find_element_by_xpath("//select[@name='_NAME']/option[@value=%r]"%rndTeacher).click()
driver.find_element_by_id("_PASS").send_keys("s3411888")
driver.find_element_by_id("vercode").send_keys(captcha)
time.sleep(2)
driver.find_element_by_name("jqi_state0_button").click()
time.sleep(5)
driver.quit()
