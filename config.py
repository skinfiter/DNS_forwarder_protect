# encoding=utf-8

title = u"DNS切换提醒测试"
local_ip = "172.31.180.226"

## testDNS
## testA


view_rulers = {
    "boce_resolver": {
        'forwards': {
            "/var/named/boce/web.list": {'testDNS': ['172.31.180.213']},
            "/etc/named.rfc1912.zones": {'testDNS': ['172.31.180.194']}
        },
        "default": {
            "0": ["211.137.64.163", "211.137.58.20"],
            "1": ["103.78.124.66", "103.78.124.88"],
            "2": ["211.98.2.4"],
            "3": ["114.114.114.114", "118.118.118.118"]
        }
    },
    "shiyan_resolver": {
        'forwards': {
            "/var/named/domainSY/teshu.list": {'testDNS': ['211.137.58.20', '211.137.64.163']},
            "/var/named/domainSY/baidu.list": {'testDNS': ['180.76.76.76']}
        },
        'default': {
            "0": ["211.137.64.163", "211.137.58.20"],
            "1": ["103.78.124.66", "103.78.124.88"],
            "2": ["211.98.2.4"],
            "3": ["114.114.114.114", "118.118.118.118"]
        }
    },
    "jingzhou_resolver": {
        'forwards': {
            "/var/named/domain/liantong.list": {'testDNS': ['202.99.224.68', '202.99.224.8']},
            "/var/named/domain/baidu.list": {'testDNS': ['180.76.76.76']}
        },
        "default": {
            "0": ["211.137.64.163", "211.137.58.20"],
            "1": ["103.78.124.66", "103.78.124.88"],
            "2": ["211.98.2.4"],
            "3": ["114.114.114.114", "118.118.118.118"],
            "4": ["172.16.23.16"]
        }
    },
    "user_resolver": {
        'forwards': {
            "/var/named/domain/baidu.list": {'testDNS': ['180.76.76.76']}
        },
        "default": {
            "0": ["211.137.64.163", "211.137.58.20"],
            "1": ["103.78.124.66", "103.78.124.88"],
            "2": ["211.98.2.4"],
            "3": ["114.114.114.114", "118.118.118.118"],
            "4": ["172.16.23.16"]
        }
    }
}

####延迟切换dns设置,当所有DNS都失败后，延迟一定的时间切换到配置的DNS上
wait_time = 600
final_default_change_ip = ["4", ["172.16.23.16"]]  ## 请始终配置最后一个forward

TCP_TIME_OUT = 2
TCP_RETRY = 5
send_mail_info = {
    "From": "",
    "To": [""],
    "user": '',
    "passwd": ""
}

named_config_path = "/etc/named.conf"

check_domain_list = [
    "www.qq.com",
    "www.baidu.com",
    "www.sina.com.cn",
    # "www.taobao.com",
    # "www.jd.com",
    # "www.ifeng.com",
    # "www.youku.com",
    # "www.mgtv.com",
    # "www.yhd.com",
    # "www.vip.com",
    # "www.suning.com",
    # "www.mogujie.com"
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
                testDNSInfo[";".join(forwardTestInfo["testDNS"])] = {"status": True, "forwardInfo": [
                    {"viewName": viewName, "forwardName": forwardName}]}
            else:
                testDNSInfo[";".join(forwardTestInfo["testDNS"])]["forwardInfo"].append(
                    {"viewName": viewName, "forwardName": forwardName})
            if "testA" in forwardTestInfo:
                if ";".join(forwardTestInfo["testA"]) not in testAInfo:
                    testAInfo[";".join(forwardTestInfo["testA"])] = {"status": True, "forwardInfo": [
                        {"viewName": viewName, "forwardName": forwardName}]}
                else:
                    testAInfo[";".join(forwardTestInfo["testA"])]["forwardInfo"].append(
                        {"viewName": viewName, "forwardName": forwardName, "status": True})
    return testDNSInfo, testAInfo


if __name__ == "__main__":
    testDNSInfo, testAInfo = load_test_info()
    print testDNSInfo
    print testAInfo
