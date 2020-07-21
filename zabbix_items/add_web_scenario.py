import json
import os
import urllib
import time
from urllib import request
import re
import ssl
import chardet

'''
web monitor paused
'''


class Url(object):
    def __init__(self, url_entry):
        self.url_entry = url_entry

    def get_group_url_ip(self):
        headers_pachong = {
            "User-Agent": "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        url_group_list = dict()
        for x in self.url_entry:
            ssl._create_default_https_context = ssl._create_unverified_context
            rq = urllib.request.Request(url=x, headers=headers_pachong)
            try:
                response = urllib.request.urlopen(rq)
            except Exception as e:
                print(x + " is 404")
                continue
            html = response.read()
            encode_type = chardet.detect(html)
            html = html.decode(encode_type['encoding'])
            reg = r'<td>[0-9]{1,}.[0-9]{1,}.[0-9]{1,}.[0-9]{1,}:[0-9]{1,}</td>'
            url_reg = re.compile(reg)
            url_list = re.findall(url_reg, html)
            url_ip_port = []
            for y in url_list:
                y = y.rstrip("</td>").lstrip("<td>")
                y = "http://" + y + "/"
                url_ip_port.append(y)
            x = x.lstrip("http://").rstrip("/status").lstrip("https://")
            url_group_list.update({x: url_ip_port})
        return url_group_list

# ip replaced
zabbix_url = "http://192.168.1.1/zabbix/api_jsonrpc.php"
headers = {
    "Content-Type": "application/json-rpc"
}


def get_token():
    if os.path.exists("/tmp/zabbix_token.txt"):
        with open("/tmp/zabbix_token.txt", "r") as f:
            zabbix_token = f.read()
    else:
        post_data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": "Admin",
                # password replaced
                "password": "Admin"
            },
            "id": 1
        }
        rqs = request.Request(url=zabbix_url, data=json.dumps(post_data).encode('utf-8'), headers=headers,
                              method='POST')
        response = request.urlopen(rqs)
        dict_access_token = json.loads(response.read())
        zabbix_token = dict_access_token["result"]
        with open("/tmp/zabbix_token.txt", "w") as f1:
            f1.write(zabbix_token)
    return zabbix_token


def get_web_scenario(hostid="14782"):
    post_data = {
        "jsonrpc": "2.0",
        "method": "httptest.get",
        "params": {
            "output": ["name"],
            "hostids": hostid
        },
        "auth": get_token(),
        "id": 1
    }
    rqs = request.Request(url=zabbix_url, data=json.dumps(post_data).encode('utf-8'), headers=headers,
                          method='POST')
    response = request.urlopen(rqs)
    return json.loads(response.read())["result"]


def create_web_scenario(scenario_name, scenario_url, hostid="14782", applicationid="74700"):
    post_data = {
        "jsonrpc": "2.0",
        "method": "httptest.create",
        "params": {
            "name": scenario_name,
            "hostid": hostid,
            'applicationid': applicationid,
            "steps": [
                {
                    "name": "web_url",
                    "url": scenario_url,
                    "status_codes": "200",
                    "no": 1
                }
            ]
        },
        "auth": get_token(),
        "id": 1
    }
    rqs = request.Request(url=zabbix_url, data=json.dumps(post_data).encode('utf-8'), headers=headers,
                          method='POST')
    try_times = 1
    while try_times < 4:
        try:
            response = request.urlopen(rqs)
            return json.loads(response.read())["result"]
        except Exception as e:
            print(e)
            time.sleep(5)
            print(str(try_times) + " times reconnecting ...")
            try_times += 1


def get_trigger(hostid="14782"):
    post_data = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "hostids": hostid,
            "output": ["description"]
        },
        "auth": get_token(),
        "id": 1
    }
    rqs = request.Request(url=zabbix_url, data=json.dumps(post_data).encode('utf-8'), headers=headers,
                          method='POST')
    response = request.urlopen(rqs)
    return json.loads(response.read())["result"]


def create_trigger(trigger_params):
    post_data = {
        "jsonrpc": "2.0",
        "method": "trigger.create",
        "params": trigger_params,
        "auth": get_token(),
        "id": 1
    }
    rqs = request.Request(url=zabbix_url, data=json.dumps(post_data).encode('utf-8'), headers=headers,
                          method='POST')
    try_times = 1
    while try_times < 4:
        try:
            response = request.urlopen(rqs)
            return json.loads(response.read())["result"]
        except Exception as e:
            print(e)
            time.sleep(5)
            print(str(try_times) + " times reconnecting ...")
            try_times += 1


if __name__ == "__main__":
    '''
    add nginx status DR monitor
    '''
    '''

    web_scenario_all = []
    trigger_all = []
    for i in get_web_scenario():
        web_scenario_all.append(i["name"].split("(")[0])
    for i in get_trigger():
        trigger_all.append(i["description"])

    with open("/home/cloud/PycharmProjects/zabbix_report/nginx_new_dr.txt", "r") as url_list:
        url_group = []
        for k in url_list:
            url_group.append(k.rstrip("\n"))
    url_all_list = Url(url_group)
    entry_url_dic = url_all_list.get_group_url_ip()
    for i in entry_url_dic:
        for j in entry_url_dic[i]:
            if j not in web_scenario_all:
                create_web_scenario(j + "(" + i + ")", j)
                print(j + "(" + i + ") scenario OK")
                web_scenario_all.append(j)
                time.sleep(1)

            trigger = []
            trigger1_name = "web " + j + " is unreachable"
            if trigger1_name not in trigger_all:
                trigger1_exp = "{web monitor:web.test.fail[" + j + "(" + i + ")" + "].count(#2,1,eq)}=2"
                trigger.append(
                    {
                        "description": trigger1_name,
                        "expression": trigger1_exp,
                        "priority": 4
                    }
                )
                trigger_all.append(trigger1_name)
            trigger2_name = "web " + j + " Response Code is {ITEM.LASTVALUE}"
            if trigger2_name not in trigger_all:
                trigger2_exp = "{web monitor:web.test.rspcode[" + j + "(" + i + ")" + ",web_url].count(#2,200,ne)}=2"
                trigger.append(
                    {
                        "description": trigger2_name,
                        "expression": trigger2_exp,
                        "priority": 4
                    }
                )
                trigger_all.append(trigger2_name)
            if trigger:
                create_trigger(trigger)
                print(j + "(" + i + ") trigger OK")
                time.sleep(1)
    '''
    print(get_trigger())
