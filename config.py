# encoding=utf-8

title = u"DNS切换提醒测试"
local_ip = "116.77.75.234"

view_rulers = {
    "tianbao_resolver": {
        'forwards': {
            "/negslb/nebind/etc/forward/sdns/sdns.list": {
                'testDNS': ['114.114.114.114'],
                'testA': ['10.0.140.50:8100', '10.0.140.27:443']
            },
            "/negslb/nebind/etc/forward/liantong/liantong.list": {
                'testDNS': ['8.8.8.8']
            }
        },
        "default": {
            "0": ["114.114.114.114"],
            "1": ["8.8.8.8"],
            "2": ['9.9.9.9']
        }
    },
    "other_resolver": {
        'forwards': {
            "/negslb/nebind/etc/forward/sdns/sdns.list": {
                'testDNS': ['114.114.1.1'],
                'testA': ['10.0.140.50:8100', '10.0.140.27:443']
            }
        },
        'default': {
            "0": ["114.114.114.114", "114.114.115.115"],
            "1": ["8.8.8.8"],
            "2": ['9.9.9.9']
        }
    }
}

####延迟切换dns设置
wait_time = 600
final_default_change_ip = ["2", ["9.9.9.9"]]

send_mail_info = {
    "From": "yybmonitor@net-east.com",
    "To": ["songsx@net-east.com"],
    "user": 'yybmonitor@net-east.com',
    "passwd": "Monitor123"
}

named_config_path = "./named.conf"

check_domain_list = [
    "www.qq.com",
    "www.baidu.com",
    "www.sina.com.cn",
    "www.taobao.com",
    "www.jd.com",
    "www.ifeng.com",
    "www.youku.com",
    "www.mgtv.com",
    "www.yhd.com",
    "www.vip.com",
    "www.suning.com",
    "www.mogujie.com"
]

# 配置文件预整理
title = '%s:%s' % (title, local_ip)


# def load_forwards_dns_list():  # 返回所有的forward DNS及个view中的forword详细信息
#     all_forwards_dns_list = []
#     views_forwards = []
#     for one in view_rulers:
#         for forwardName, testTarget in one['forwards'].iteritems():
#             all_forwards_dns_list.append(tuple(testTarget['testDNS']))
#             views_forwards.append([one['name'], forwardName, testTarget, True])
#     return set(all_forwards_dns_list), views_forwards


def load_test_info():  # 获取每个forward探测目标都在哪些view里生效
    testDNSInfo = {}
    testAInfo = {}
    for viewName, viewInfo in view_rulers.iteritems():
        for forwardName, forwardTestInfo in viewInfo['forwards'].iteritems():
            if ";".join(forwardTestInfo["testDNS"]) not in testDNSInfo:
                testDNSInfo[";".join(forwardTestInfo["testDNS"])] = {"status": True,"forwardInfo":[
                    {"viewName": viewName, "forwardName": forwardName}]}
            else:
                testDNSInfo[";".join(forwardTestInfo["testDNS"])]["forwardInfo"].append(
                    {"viewName": viewName, "forwardName": forwardName})
            if "testA" in forwardTestInfo:
                if ";".join(forwardTestInfo["testA"]) not in testAInfo:
                    testAInfo[";".join(forwardTestInfo["testA"])] ={"status": True,"forwardInfo":[
                        {"viewName": viewName, "forwardName": forwardName}]}
                else:
                    testAInfo[";".join(forwardTestInfo["testA"])]["forwardInfo"].append(
                        {"viewName": viewName, "forwardName": forwardName, "status": True})
    return testDNSInfo, testAInfo


if __name__ == "__main__":
    testDNSInfo, testAInfo = load_test_info()
    print testDNSInfo
    print testAInfo
