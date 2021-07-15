from websocket import create_connection
import json
import random
import string
import re
import pandas as pd
import csv
from datetime import datetime


def filter_raw_message(text):
    try:
        found = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
        print(found)
        print(found2)
        return found, found2
    except AttributeError:
        print("error")


def generateSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(stringLength))
    return "qs_" + random_string


def generateChartSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(stringLength))
    return "cs_" + random_string


def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st


def constructMessage(func, paramList):
    # json_mylist = json.dumps(mylist, separators=(',', ':'))
    return json.dumps({
        "m": func,
        "p": paramList
    }, separators=(',', ':'))


def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))


def sendRawMessage(ws, message):
    ws.send(prependHeader(message))


def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))


def generate_csv(a):
    out = re.search('"s":\[(.+?)\}\]', a).group(1)
    x = out.split(',{\"')

    with open('data_file.csv', mode='w', newline='') as data_file:
        employee_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        employee_writer.writerow(['index', 'date', 'open', 'high', 'low', 'close', 'volume'])

        for xi in x:
            xi = re.split('\[|:|,|\]', xi)
            # print(xi)
            ind = int(xi[1])
            ts = datetime.fromtimestamp(float(xi[4])).strftime("%Y/%m/%d, %H:%M:%S")
            employee_writer.writerow([ind, ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])


# Initialize the headers needed for the websocket connection
headers = json.dumps({
    "Connection": "upgrade",
    "Host": "data.tradingview.com",
    "Origin": "https://data.tradingview.com",
    "Cache-Control": "no-cache",
    # "Upgrade": "websocket",
    "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
    "Sec-WebSocket-Key": "4C2syPMu6ylDUG4Nhbr5tQ==",
    "Sec-WebSocket-Version": "13",
    "User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56",
    "Pragma": "no-cache",
    "Upgrade": "websocket"
})

# Then create a connection to the tunnel
ws = create_connection(
    'wss://data.tradingview.com/socket.io/websocket?date=2020_03_26-18_50', headers=headers)

session = generateSession()
print("session generated {}".format(session))

chart_session = generateChartSession()
print("chart_session generated {}".format(chart_session))

# Then send a message through the tunnel 
sendMessage(ws, "set_auth_token", ["eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxNjg1NTQwOCwiZXhwIjoxNjE2OTgwNDQ1LCJpYXQiOjE2MTY5NjYwNDUsInBsYW4iOiIiLCJleHRfaG91cnMiOjEsInBlcm0iOiIiLCJzdHVkeV9wZXJtIjoiIiwibWF4X3N0dWRpZXMiOjMsIm1heF9mdW5kYW1lbnRhbHMiOjAsIm1heF9jaGFydHMiOjF9.NrWpR-bgGcJWQtYKpRkhpNx-V4hIVwThL8iM1u7aflXB339lbg4r-2dBSYXInlKacYBQ4PNOWy2zbYmq8-wuIkBY6yoivem7BqRVuJyPprwUeDcojDLXZFhCFfq-Nh3gLKV96RsB37s1e2cGubg8xWb43nuXW10LEttLBm92ou8"])
sendMessage(ws, "chart_create_session", [chart_session, ""])
sendMessage(ws, "quote_create_session", [session])
sendMessage(ws, "quote_set_fields",
            [session, "ch", "chp", "current_session", "description", "local_description", "language", "exchange",
             "fractional", "is_tradable", "lp", "lp_time", "minmov", "minmove2", "original_name", "pricescale",
             "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])
sendMessage(ws, "quote_add_symbols", [session, "BINANCE:ETHUSDT", {"flags": ['force_permission']}])
sendMessage(ws, "quote_fast_symbols", [session, "BINANCE:ETHUSDT"])

# st='~m~140~m~{"m":"resolve_symbol","p":}'
# p1, p2 = filter_raw_message(st)
sendMessage(ws, "resolve_symbol", [chart_session, "symbol_1",
                                   "={\"symbol\":\"BINANCE:ETHUSDT\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", "15", 300])

# sendMessage(ws, "create_study", [chart_session, "st1", "sessions_1", "s1", "Sessions@tv-basicstudies-121!",
#                                  {"length": 20, "col_prev_close": "false"}])
sendMessage(ws, "quote_hibernate_all", [session])
# ~m~831~m~{"m":"create_study","p":["cs_Cnufu5nazOB2","st7","st2","s1","Script@tv-scripting-101!",{"text":"M3+zxCWA/09qjN8bECQPuA==_6OKjBRW25wYVndQ7upK8at7asZoSepIKn0cFPwgbvtkzYLoc2db9JgUXGCJI/66Fb2yeOH8NobMo+Ozo/FYHV+ti8//Ptq81SYRPJMhHSjO9KqwHb/A6gCxygz/8/paSP5T+82O1AIgpjnaBBRIM699XhBsh9UdTz7/2+qiieMDxyLBLaHzL2tLDPqBehpZnLOwMntXUNzfTHnuYOION6azMoXJaP0yfj4hSQHW2tlOgoXo2C4tL5wfAErPe1HxX9/o5y8yYVuSznIxpyQ72nUVnvNcc1ZgBdGp40iy19cy5rz6dRk8V24FcgJEmphPRohr9JwILPNJE65Y35wxqSkW8+32jSLEipzSdzE/doeBuU0fAKWg8YLtAolqwuy67SKG6zIRNie2Hqukb2B06vRYkbrK6gVhnn6QI8WgHlbXRMrjd1Tr7GhiE3vHn8AZBdtcKyUg=","pineId":"STD;Bollinger_Bands","pineVersion":"15.0","in_4":{"v":"","f":true,"t":"resolution"},"in_0":{"v":20,"f":true,"t":"integer"},"in_1":{"v":"close","f":true,"t":"source"},"in_2":{"v":2,"f":true,"t":"float"},"in_3":{"v":0,"f":true,"t":"integer"}}]}
# sendMessage(ws, "create_study", [chart_session,"st4","st1","s1","ESD@tv-scripting-101!",{"text":"BNEhyMp2zcJFvntl+CdKjA==_DkJH8pNTUOoUT2BnMT6NHSuLIuKni9D9SDMm1UOm/vLtzAhPVypsvWlzDDenSfeyoFHLhX7G61HDlNHwqt/czTEwncKBDNi1b3fj26V54CkMKtrI21tXW7OQD/OSYxxd6SzPtFwiCVAoPbF2Y1lBIg/YE9nGDkr6jeDdPwF0d2bC+yN8lhBm03WYMOyrr6wFST+P/38BoSeZvMXI1Xfw84rnntV9+MDVxV8L19OE/0K/NBRvYpxgWMGCqH79/sHMrCsF6uOpIIgF8bEVQFGBKDSxbNa0nc+npqK5vPdHwvQuy5XuMnGIqsjR4sIMml2lJGi/XqzfU/L9Wj9xfuNNB2ty5PhxgzWiJU1Z1JTzsDsth2PyP29q8a91MQrmpZ9GwHnJdLjbzUv3vbOm9R4/u9K2lwhcBrqrLsj/VfVWMSBP","pineId":"TV_SPLITS","pineVersion":"8.0"}])


# Printing all the result
a = ""
cnt = 1
while True:
    try:
        if cnt%5 == 0:
            sendMessage(ws, "request_more_data", [chart_session, "s1", 50])
        result = ws.recv()
        pattern = re.compile("~m~\d+~m~~h~\d+$")
        if pattern.match(result):
            ws.recv()
            ws.send(result)
            print("\n\n\n hhhhhhhhhhhhhhhhhhhhhh " + str(result) + "\n\n")

        # ws.send(result)
        # sendRawMessage("")
        print(result)
        a = a + result + "\n"
        cnt += 1
        # sendMessage(ws, "request_more_data", [chart_session, "s1", 100])
        if cnt > 1000:
            break
        # sendMessage(ws, "request_more_tickmarks", [chart_session, "s1", 100])
    except Exception as e:
        print(e)
        break
    # try:
    #     sendMessage(ws, "request_more_data", [chart_session, "s1",  10000])
    # except Exception as e:
    #     print(e)
    #     break

generate_csv(a)
