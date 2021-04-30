import json
import requests
import time
def get_mercator(addr):
    url= 'http://api.map.baidu.com/geocoder/v2/?address=%s&output=json&ak=kTWetyXuPLx38KRbCHxswZRkFKPLtw0H&callback=showLocation'%(addr)
    response = requests.get(url)
    return response
def getLngAndLat(addrs):
    result = {}
    for addr in addrs:
        response=get_mercator(addr)
        #print(response.text)
        lngAndLat = []
        try:
            jsonRe = json.loads(response.text.split("showLocation&&showLocation(")[1].strip(")"))["result"]["location"]
            lngAndLat.append(jsonRe["lng"])
            lngAndLat.append(jsonRe["lat"])
            result[addr] = lngAndLat
        except Exception:
            result[addr] = lngAndLat
        time.sleep(1)

    return result

if __name__=="__main__":
    addrs=["湖南省石门县"]
    print(getLngAndLat(addrs))