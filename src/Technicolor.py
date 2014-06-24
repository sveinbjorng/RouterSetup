'''
Created on Jun 4, 2014

@author: sveinbjorn
'''
import urllib2, urllib, cookielib, re, hashlib, sys #@UnresolvedImport
from urllib2 import HTTPError #@UnresolvedImport
from py2app.script_py2applet import raw_input

class TG589:
    def __init__(self):
        self.loginUrl = "http://192.168.1.254/login.lp"
        self.wifiUrl = "http://192.168.1.254/cgi/b/_wli_/cfg/?be=0&l0=4&l1=1&name=WLAN:%20"
        self.pppoeUrl = "http://192.168.1.254/cgi/b/is/_pppoe_/ov/?be=0&l0=2&l1=2&name=Internet_ppp"
        self.cj = cookielib.LWPCookieJar()
        self.rn = []
        self.realm = "Technicolor Gateway"
        self.nonce = None
        self.opener = None
        
    def LoginToRouter(self):
        grabCookies = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)).open(self.loginUrl)
        for x in grabCookies:
            if '<input type="hidden" name="rn" ' in x:
                self.rn.append("-" + filter(str.isdigit, x.strip()))
            elif 'var nonce = ' in x:
                nonce = re.findall('"([^"]*)"', x)
                self.nonce = str(nonce[0])
                    
        HA1 = hashlib.md5("admin:"+self.realm+":admin").hexdigest()
        HA2 = hashlib.md5("GET:/login.lp").hexdigest()
        sekretPass = hashlib.md5(HA1 + ":" + self.nonce + ":" + "00000001" + ":" + "xyz" + ":auth:" + HA2).hexdigest();
        try:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)) 
            urllib2.install_opener(self.opener)
            params = urllib.urlencode(dict(rn=self.rn[0], hidepw=sekretPass, user='admin')) 
            op = self.opener.open(self.loginUrl, params)
            if(op):
                return 0
            
        except HTTPError, e:
            if(e.getcode() == 500):
                return 500
    
    def ConfigureWifi(self, ssid, channel, wirelessKey):
        headers = [('Referer','http://192.168.1.254/cgi/b/_wli_/cfg/?be=0&l0=4&l1=1&name=WLAN:%20')]
        self.opener.addheaders = headers
        #"(?:-\d|\d)[value=]*[^'*]"
        getRn = self.opener.open(self.wifiUrl)
        for x in getRn:
            if "<input type='hidden' name='2' value=" in x:
                p = re.compile(ur'(?:-\d|\d)[value=]*[^\'*]')
                rn = re.findall(p, x)
                rn = ''.join(rn)
        try:
            params = urllib.urlencode(dict({"0":"10","1":"","2":rn,"32":"WLAN: ","53":"0","31":"1","33": ssid,"35":"Manual","36": channel,"47":"1","53":"0","48":"TKIP&AES","37":"1","38":"unlock","39":"WPAWPA2PSK","41": wirelessKey})) 
            postWifi = self.opener.open(self.wifiUrl, params)
            for y in postWifi:
                if "HTTP/1.0 403 Forbidden" in y:
                    print "Wireless: setup failed!"
            print "Wireless: Done!"
            return 0
        
        except HTTPError, e:
            if(e.getcode() == 500):
                return 500
                
    def ConfigurePPPoE(self, username, password):
        getRn = self.opener.open(self.pppoeUrl)
        for x in getRn:
            if "<input type='hidden' name='2' value=" in x:
                p = re.compile(ur'(?:-\d|\d)[value=]*[^\'*]')
                rn = re.findall(p, x)
                rn = ''.join(rn)
        try:
            params = urllib.urlencode(dict({"0":"12", "1":"Internet_ppp","2":rn,"5":"1","30":username,"31":password,"32":"1"})) 
            postPPPoE = self.opener.open(self.pppoeUrl, params)
            for y in postPPPoE:
                if "HTTP/1.0 403 Forbidden" in y:
                    print "PPPoE: setup failed!"
                    return 500;
            print "PPPoE: Done!"
            return 0
        
        except HTTPError, e:
            if(e.getcode() == 500):
                return 500
             
if __name__ == '__main__':
    ssid = raw_input("Enter SSID: ")
    wirelessKey = raw_input("Enter wireless key: ")
    username = raw_input("Enter PPPoE username: ")
    password = raw_input("Enter PPPoE password: ")
    
    print "SSID: " + ssid
    print "Wireless key: " + wirelessKey
    print "PPPoE username: " + username
    print "Password : " + password
    yn = raw_input("Continue? (y/n)")
    
    if(yn == 'y'):
        router = TG589()
        login = router.LoginToRouter()
        while(login != 0):
            print "Login: Trying to login.."
            router = TG589()
            login = router.LoginToRouter()
        print "Login: Done!"
        
        print "Wireless: Trying to setup wireless.."
        wifi = router.ConfigureWifi(ssid, "11", wirelessKey)

        while(wifi != 0)
            wifi = router.ConfigureWifi(ssid, "11", wirelessKey)
            print "Wireless: Trying again.."
        
        print "PPPoE: Trying to setup PPPoE.."
        pppoe = router.ConfigurePPPoE(username, password)
        while(pppoe != 0)
            pppoe = router.ConfigurePPPoE(username, password)
            print "PPPoE: Trying again.."

    print "Router setup is complete!"
    bla = raw_input("Press enter to exit.")
    
    
    