import requests
from wxConfig import APPID , SECRET

class getOpenIdObject(object):

    def __init__(self , jscode):
        self.appid = APPID
        self.secret = SECRET
        self.jscode = jscode
        self.url = "https://api.weixin.qq.com/sns/jscode2session"

    def getOpenId(self):
        url = self.url + "?appid=" + self.appid + "&secret=" + self.secret + "&js_code=" + self.jscode + "&grant_type=authorization_code"
        r = requests.get(url)
        print(r.json())
        openid = r.json()['openid']
        return openid