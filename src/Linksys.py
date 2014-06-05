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
            print "First time setup: Done!"
        except Exception, e:
            print "First time setup: " + str(e) + " (This is normal if router has been setup before)"
        
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
        print "Login: Done!"
                
    def ConfigureSSID(self, ssid, channel):
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
            "channel_24g":channel,
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
        print "Wireless: SSID configured!"
        
    def ConfigureWirelessKey(self, wirelessKey):    
        headers = [('Referer', 'http://192.168.1.1/WL_WPATable.asp;' + self.sessionId)]
        self.opener.addheaders = headers

        params = urllib.urlencode(dict({
            "submit_button":"WL_WPATable",
            "change_action":"",
            "submit_type":"",
            "gui_action":"Apply",
            "security_mode_last":"",
            "wl_wep_last":"",
            "wait_time":"3",
            "wsc_nwkey0":wirelessKey,
            "wl0_crypto":"tkip+aes",
            "wsc_security_auto":"0",
            "wl0_security_mode":"wpa_wpa2_mixed",
            "wl0_wpa_psk":wirelessKey                    
        }))
        self.opener.open(self.applyUrl+self.sessionId, params)
        print "Wireless: Wireless security configured!"
        print "Wireless: Done!"
    
    def DisableWMMSupport(self):
        headers = [('Referer', 'http://192.168.1.1/QoS.asp;' + self.sessionId)]
        self.opener.addheaders = headers
        
        params = urllib.urlencode(dict({
            "qos_list":"",
            "QoS_cnt":"0",
            "enable_game":"0",
            "submit_button":"QoS",
            "change_action":"",
            "gui_action":"Apply",
            "need_action":"restart",
            "wait_time":"30",
            "wl_wme":"off",
            "QoS":"0",
            "fport1":"",
            "tport1":"",
            "pro1":"0",
            "pro2":"0",
            "pro3":"0"}))
        
        self.opener.open(self.applyUrl+self.sessionId, params)
        print "WMM Support: Done!"
        
if __name__ == '__main__':
    ssid = raw_input("Enter SSID: ")
    wirelessKey = raw_input("Enter wireless key: ")
    channel = raw_input("Enter wireless channel: ")
    
    print "SSID: " + ssid
    print "Wireless key: " + wirelessKey
    print "Channel: " + channel
    yn = raw_input("Continue? (y/n)")
    
    if(yn == 'y'):
        router = E900()
        print "First time setup: Dealing with unsecure.."
        router.DealWithUnsecure()
        print "Login: Trying to login.."
        router.LoginToRouter()
        print "Wireless: Trying to setup wireless.."
        router.ConfigureSSID(ssid, channel)
        router.ConfigureWirelessKey(wirelessKey)
        print "WMM Support: Trying to disable.."
        router.DisableWMMSupport()
    print "Router setup is complete!"
    