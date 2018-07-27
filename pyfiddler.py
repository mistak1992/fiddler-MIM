# coding:utf-8

import clr
import sys
import demjson
import win32api
import win32con
from datetime import datetime
from certificate import *

# sys.path.append("./")
clr.FindAssembly("FiddlerCore4")
clr.AddReference("FiddlerCore4")
import Fiddler as FC


# do some thing when Ctrl-c or colse
def onClose(sig):
    print chr(7)
    FC.FiddlerApplication.Shutdown()
    win32api.MessageBox(win32con.NULL, 'See you later', 'Exit', win32con.MB_OK)


# will be invoked when it is called by delegate.
def printLog(source, oLEA):
    print "\n** LogString: **\n" + oLEA.LogString


def printSession(s):
    if s is None or s.oRequest is None or s.oRequest.headers is None:
        return

    # Ignore HTTPS connect requests
    if s.RequestMethod == "CONNECT":
        return

    # Filter for host
    host_obmit = "api.map.baidu.com"
    host = s.hostname.lower()
    if host_obmit not in host:
        return

    # Filter for path
    url = s.url.lower()
    if '/v3' not in url:
        return
    datetime_now = datetime.now().strftime('%a, %Y %b %d %H:%M:%S')
    datetime_now_utc = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    reqHeaders = s.oRequest.headers.ToString()
    reqBody = s.GetRequestBodyAsString()
    respCode = s.responseCode
    respHeaders = s.oResponse.headers.ToString()
    # print
    # print '--->'
    # print datetime_now
    # print reqHeaders
    #
    # # deal with cookie
    # if s.oRequest.headers.Exists("cookie"):
    #     cookie = s.oRequest.headers.AllValues("cookie")
    #     print "Request cookie are:", cookie
    #
    # # if reqBody: print "!! Request body:\n",reqBody
    # print '<---'
    # print respCode


def onBeforeResponse(s):
    if s is None or s.oRequest is None or s.oRequest.headers is None:
        return

    # Ignore HTTPS connect requests
    if s.RequestMethod == "CONNECT":
        return

    # Filter for host
    # host_obmit = "api.map.baidu.com"
    host_obmit = "wx.tenpay.com"
    host = s.hostname.lower()
    if host_obmit not in host:
        return

    # Filter for path
    url = s.url.lower()
    if '/readtemplate' in url:
        return

    order = '{"bill_id":"11f63a5b20a1070022f0fc47","trans_id":"11500002118070302071209426696653","title":"习主席","timestamp":1530590737,"fee":99900,"fee_type":"CNY","fee_attr":"positive","current_state":"","current_state_type":"","bill_type":11,"icon_url":"https://ss2.baidu.com/6ONYsjip0QIZ8tyhnq/it/u=3680604140,401532791&fm=179&app=42&f=JPEG?w=121&h=140","out_trade_no":"257006804385601530528909","classify_type":31,"pay_bank_name":"招商银行","remark":"美团订单-257006804385601530528909","business_data":"","charge_fee":0,"payer_remark":"","payer_uin":0,"payer_wxid":"","is_friend":false}'
    orderArr = '[' + order + ',' + order + ',' + order + ',' + order + ',' + order + ',' + order + ',' + order + ']'
    orderObj = demjson.decode(orderArr)
    print(orderObj)
    responseBodyOrignal = s.GetResponseBodyAsString()
    responseBodyString = responseBodyOrignal.encode('utf-8')
    print(type(responseBodyOrignal))
    responseBodyJson = demjson.decode(responseBodyString)
    responseBodyJson['record'] = orderObj
    responseBodyResult = demjson.encode(responseBodyJson).decode('utf-8')
    print(type(responseBodyResult))
    s.utilSetResponseBody(responseBodyResult)


def onBeforeRequest(s):
    s.bBufferResponse = True


def fiddler(FC, flags):
    # register event handler
    # object.SomeEvent += handler
    #
    # unregister event handler
    # object.SomeEvent -= handler
    #
    # passed a callable Python object to get a delegate instance.
    FC.FiddlerApplication.Log.OnLogString += printLog
    FC.FiddlerApplication.AfterSessionComplete += printSession
    FC.FiddlerApplication.BeforeResponse += onBeforeResponse
    FC.FiddlerApplication.BeforeRequest += onBeforeRequest
    # When decrypting HTTPS traffic,ignore the server certificate errors
    FC.CONFIG.IgnoreServerCertErrors = False

    # start up capture
    FC.FiddlerApplication.Startup(8888, flags)


if __name__ == '__main__':

    win32api.SetConsoleCtrlHandler(onClose, 1)
    captureType = "http"

    # RegisterAsSystemProxy:1
    # OptimizeThreadPool:512
    # MonitorAllConnections:32
    # DecryptSSL:2
    # AllowRemoteClients:8
    if captureType == "https":
        prepareCert(FC)
        fiddler(FC, 1 + 512 + 32 + 2 + 8)
    else:
        fiddler(FC, 1 + 512 + 32 + 2 + 8)
    try:
        # keep console window be open
        raw_input()
    except:
        pass