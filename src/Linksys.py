'''
Created on Jun 5, 2014

@author: sveinbjorn
'''
import urllib2, urllib, cookielib, re, hashlib, base64, sys #@UnresolvedImport
from urllib2 import HTTPError #@UnresolvedImport

class FirmwareX:
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
        try:
            login = self.opener.open(self.loginUrl, params)
            for l in login:
                if 'document.location.href = "' in l:
                    p = re.compile(ur'\;(.*?)\"')
                    p = re.findall(p, l)
                    self.sessionId = ''.join(p)
            print "Login: Done!"
            
        except HTTPError, e:
            print "Login: Failed! Error: " + str(e.getcode())
            sys.exit()
                
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
        try:
            self.opener.open(self.applyUrl+self.sessionId, params)
            print "Wireless: SSID configured!"
            
        except HTTPError, e:
            print "Wireless: SSID configuration failed! Error: " + str(e.getcode())
            sys.exit()
        
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
        try: 
            self.opener.open(self.applyUrl+self.sessionId, params)
            print "Wireless: Wireless security configured!"
            print "Wireless: Done!"
        except HTTPError, e:
            print "Wireless: Wireless security configuration failed! Error: " + str(e.getcode())
            sys.exit()
    
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
        
        try:
            self.opener.open(self.applyUrl+self.sessionId, params)
            print "WMM Support: Done!"
        except HTTPError, e:
            print "WMM Support: Failed! Error: " + str(e.getcode())
            sys.exit()
        
class FirmwareY:
    def __init__(self):
        self.opener = None
        self.cj = None
        self.loginUrl = "http://192.168.1.1/"
        self.applyUrl = "http://192.168.1.1/cgi-bin/apply.cgi"
        self.base64Secret = ""
        
    def LoginToRouter(self):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)) 
        urllib2.install_opener(self.opener)
        
        self.base64Secret = base64.encodestring('%s:%s' % ("admin", "admin")).replace('\n', '')
        headers = [('Authorization', 'Basic ' + self.base64Secret)]
        self.opener.addheaders = headers

        try:
            self.opener.open(self.loginUrl)
            print "Login: Done!"
            
        except HTTPError, e:
            print "Login: Failed! Error: " + str(e.getcode())
            sys.exit()
    
    def ConfigureSSID(self, ssid, channel):
        headers = [('Referer','http://192.168.1.1/index.stm?title=Wireless-Basic%20Wireless%20Settings'),
                   ('Authorization', 'Basic ' + self.base64Secret)]
        self.opener.addheaders = headers
        
        params = urllib.urlencode(dict({
            "delay":"0",
            "submit_type":"",
            "wsc_result":"",
            "wsc_security_mode":"",
            "GoToWeb":"",
            "wlConf":"0",
            "op_mode":"7",
            "wl_ssid":ssid,
            "bandwidth":"0",
            "channel":channel,
            "wlan_broadcast":"1",
            "wsc_enrpin":"",
            "exec_cgis":"WirBWS",
            "ret_url":"/index.stm?title=Wireless-Basic%20Wireless%20Settings"}))
        try:
            self.opener.open(self.applyUrl, params)
            print "Wireless: SSID configured!"
            
        except HTTPError, e:
            print "Wireless: SSID configuration failed! Error: " + str(e.getcode())
            sys.exit()
        
    def ConfigureWirelessKey(self, key):
        headers = [('Referer','http://192.168.1.1/index.stm?title=Wireless-Wireless%20Security'),
                   ('Authorization', 'Basic ' + self.base64Secret)]
        self.opener.addheaders = headers
        
        params = urllib.urlencode(dict({
            "delay":"0",
            "sec_mode":"psk1",
            "enc_type":"1",
            "sharedkey":key,
            "rds_ip1":"0",
            "rds_ip2":"0",
            "rds_ip3":"0",
            "rds_ip4":"0",
            "rds_port":"1812",
            "rds_secret":"",
            "group_key_second":"3600",
            "encryption_type":"0",
            "passPhrase":"",
            "generate":"0",
            "key1":"",
            "key2":"",
            "key3":"",
            "key4":"",
            "TX_Key":"0",
            "exec_cgis":"WirWS",
            "ret_url":"/index.stm?title=Wireless-Wireless%20Security"}))
        
        try:
            self.opener.open(self.applyUrl, params)
            print "Wireless: Wireless key configured!"
            
        except HTTPError, e:
            print "Wireless: Wireless key configuration failed! Error: " + str(e.getcode())
            sys.exit()
    
    def DisableWMMSupport(self):
        headers = [('Referer','http://192.168.1.1/index.stm?title=Applications%20%26%20Gaming-QoS'),
                   ('Authorization', 'Basic ' + self.base64Secret)]
        self.opener.addheaders = headers
        
        params = urllib.urlencode(dict({
            "delay":"0",
            "qos":"0",
            "wmm_enable":"0",
            "noack_enable":"0",
            "iap_enable":"0",
            "cnt_game":"0",
            "cnt_name":"",
            "cnt_maddr":"00:00:00:00:00:00",
            "cnt_ethport":"0",
            "cnt_pfrom1":"",
            "cnt_pto1":"",
            "cnt_pproto1":"0",
            "cnt_pfrom2":"",
            "cnt_pto2":"",
            "cnt_pproto2":"0",
            "cnt_pfrom3":"",
            "cnt_pto3":"",
            "cnt_pproto3":"0",
            "cur_idx":"0",
            "mod_now":"0",
            "EntryNum":"0",
            "exec_cgis":"AppQ",
            "ret_url":"/index.stm?title=Applications%20%26%20Gaming-QoS"}))
        try:
            self.opener.open(self.applyUrl, params)
            print "WMM Support: Done!"
        except HTTPError, e:
            print "WMM Support: Failed! Error: " + str(e.getcode())
            sys.exit()
        
if __name__ == '__main__':
    ssid = raw_input("Enter SSID: ")
    wirelessKey = raw_input("Enter wireless key: ")
    channel = raw_input("Enter wireless channel: ")
    
    print "SSID: " + ssid
    print "Wireless key: " + wirelessKey
    print "Channel: " + channel
    
    router = FirmwareY()
    router.LoginToRouter()
    router.ConfigureSSID(ssid, channel)
    router.ConfigureWirelessKey(wirelessKey)
    router.DisableWMMSupport()
    
    '''yn = raw_input("Continue? (y/n)")
    
    if(yn == 'y'):
        router = FirmwareX()
        print "First time setup: Dealing with unsecure.."
        router.DealWithUnsecure()
        print "Login: Trying to login.."
        router.LoginToRouter()
        print "Wireless: Trying to setup wireless.."
        router.ConfigureSSID(ssid, channel)
        router.ConfigureWirelessKey(wirelessKey)
        print "WMM Support: Trying to disable.."
        router.DisableWMMSupport()
    print "Router setup is complete!"'''
    
    