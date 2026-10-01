# -*- coding: UTF-8 -*-
import requests as req
import json, sys, time, random
import argparse
import os
import pytz
from datetime import datetime
import random
# import parser
#先注册azure应用,确保应用有以下权限:
#files:	Files.Read.All、Files.ReadWrite.All、Sites.Read.All、Sites.ReadWrite.All
#user:	User.Read.All、User.ReadWrite.All、Directory.Read.All、Directory.ReadWrite.All
#mail:  Mail.Read、Mail.ReadWrite、MailboxSettings.Read、MailboxSettings.ReadWrite
# 注册后一定要再点代表xxx授予管理员同意,否则outlook api无法调用




# parser = argparse.ArgumentParser()
# parser.add_argument('--config_id', required=True)
# parser.add_argument('--config_key', required=True)
# args=parser.parse_args()
# id=args.config_id
# secret=args.config_key


path=sys.path[0]+r'/1.txt'
num1 = 0
MIN_CALLS_PER_RUN = 2
MAX_CALLS_PER_RUN = 6
API_ENDPOINTS = [
    ("drive root", "https://graph.microsoft.com/v1.0/me/drive/root", 5),
    ("drive", "https://graph.microsoft.com/v1.0/me/drive", 4),
    ("drive root", "https://graph.microsoft.com/v1.0/drive/root", 1),
    ("users", "https://graph.microsoft.com/v1.0/users", 1),
    ("messages", "https://graph.microsoft.com/v1.0/me/messages", 3),
    ("inbox rules", "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules", 2),
    ("drive children", "https://graph.microsoft.com/v1.0/me/drive/root/children", 4),
    ("Power BI apps", "https://api.powerbi.com/v1.0/myorg/apps", 1),
    ("mail folders", "https://graph.microsoft.com/v1.0/me/mailFolders", 2),
    ("master categories", "https://graph.microsoft.com/v1.0/me/outlook/masterCategories", 2),
]
# get the timezone for China Standard Time (CST)
cst = pytz.timezone('Asia/Shanghai')

# get the current time in the CST timezone
now = datetime.now(cst)

# format the time as a string
localtime = now.strftime("%Y-%m-%d %H:%M:%S")

def choose_endpoints():
    max_calls = min(MAX_CALLS_PER_RUN, len(API_ENDPOINTS))
    call_count = random.randint(MIN_CALLS_PER_RUN, max_calls)
    available = API_ENDPOINTS.copy()
    selected = []
    for _ in range(call_count):
        endpoint = random.choices(
            available,
            weights=[item[2] for item in available],
            k=1
        )[0]
        selected.append(endpoint)
        available.remove(endpoint)
    return selected

def gettoken(refresh_token):
    headers={'Content-Type':'application/x-www-form-urlencoded'
            }
    data={'grant_type': 'refresh_token',
          'refresh_token': refresh_token,
          'client_id':id,
          'client_secret':secret,
          'redirect_uri':'http://localhost:53682/'
         }
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',data=data,headers=headers)
    jsontxt = json.loads(html.text)
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    return access_token
def main():
    fo = open(path, "r+")
    refresh_token = fo.read()
    fo.close()
    global num1
    # localtime = time.asctime( time.localtime(time.time()) )
    access_token=gettoken(refresh_token)
    headers={
    'Authorization':'Bearer '+access_token,
    'Content-Type':'application/json'
    }
    print('此次运行开始时间为 :', localtime)
    with open(sys.path[0]+r'/time.log','a',encoding="utf-8") as fd:
        fd.write('运行开始时间为: %s \n' % localtime)
    for name, url, _ in choose_endpoints():
        try:
            response = req.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                num1 += 1
                print(name + " 调用成功" + str(num1) + '次')
            elif response.status_code == 429:
                print(name + " 遇到限流，本轮剩余调用已跳过")
                break
            else:
                print(name + " 调用失败，HTTP " + str(response.status_code))
        except req.RequestException as error:
            print(name + " 请求异常: " + str(error))

run_times = random.randint(3,8)

for _ in range(run_times):
    main()
    for i in range(random.randint(30, 60),0,-1):
        time.sleep(1)
