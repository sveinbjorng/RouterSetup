'''
Created on Jun 5, 2014

@author: sveinbjorn
'''
import urllib2, urllib, cookielib, re, hashlib #@UnresolvedImport
from urllib2 import HTTPError #@UnresolvedImport

class E900:
    def __init__(self):
        self.unsecuredUrl = "http://192.168.1.1:52000/UnsecuredEnable.cgi"
        self.loginUrl = "http://192.168.1.1/login.cgi"
        self.applyUrl = "http://192.168.1.1/apply.cgi;"
        self.cj = cookielib.LWPCookieJar()
        self.opener = None
        self.sessionId = ""
    
    def MakeSekret(self, data):
        pseed2 = ""
        buffer1 = data
        md5str2 = ""
        length2 = len(data)
        
        if(length2 < 10):
            buffer1 = buffer1 + "0"
            buffer1 = buffer1 + str(length2)
        else:
            buffer1 = length2
        length2 = length2 + 2
        for x in xrange(0, 64):
            tempcount = x % length2;
            pseed2 = pseed2 + buffer1[tempcount:tempcount+1]
            
        md5str2 = hashlib.md5(pseed2).hexdigest()
        
        return md5str2
    
    def DealWithUnsecure(self):
        params = urllib.urlencode(dict({
                                        "submit_button":"UnsecuredEnable",
                                        "change_action":"",
                                        "gui_action":"Apply",
                                        "next_url":"192.168.1.1",
                                        "wait_time":"19",
                                        "submit_type":""})) 
        
        try:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)) 
            urllib2.install_opener(self.opener)
            
            self.opener.open(self.unsecuredUrl, params)
            
        except Exception, e:
            print str(e)
        
    def LoginToRouter(self):
        if(self.opener == None):
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)) 
            urllib2.install_opener(self.opener)
        params = urllib.urlencode(dict({
                                        "submit_button":"login",
                                        "change_action":"",
                                        "action":"Apply",
                                        "wait_time":"19",
                                        "submit_type":"",
                                        "http_username":"admin",
                                        "http_passwd":self.MakeSekret("admin"),
                                   }))
        login = self.opener.open(self.loginUrl, params)
        for l in login:
            if 'document.location.href = "' in l:
                p = re.compile(ur'\;(.*?)\"')
                p = re.findall(p, l)
                self.sessionId = ''.join(p)
    def ConfigureWireless(self, ssid, wirelessKey):
        headers = [('Referer','http://192.168.1.1/Wireless_Basic.asp;' + self.sessionId)]
        self.opener.addheaders = headers
        params = urllib.urlencode(dict({
            "submit_button":"Wireless_Basic",
            "gui_action":"Apply",
            "submit_type":"",
            "change_action":"",
            "next_page":"",
            "commit":"1",
            "wl0_nctrlsb":"upper",
            "channel_24g":"11",
            "nbw_24g":"20",
            "wait_time":"3",
            "guest_ssid":"",
            "wsc_security_mode":"",
            "wsc_smode":"1",
            "net_mode_24g":"mixed",
            "ssid_24g":ssid,
            "_wl0_nbw":"20",
            "_wl0_channel":"11",
            "closed_24g":"0"}))
        self.opener.open(self.applyUrl+self.sessionId, params)
            
if __name__ == '__main__':
    router = E900()
    #router.DealWithUnsecure()
    router.LoginToRouter()
    router.ConfigureWireless("SveimbaSSID", "SveimbaKey")