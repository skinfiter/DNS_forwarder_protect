#!/usr/bin/env python
# encoding=utf-8
import sys
import os
import time
import re
import dns.resolver
from config import *
from mylogger import *
from send_mail import *
from pro_check_named_file import *
from named_conf_parser import NamedConfig
from pstool import *
import json


def pro_check(test_dns, domain):
    try:
        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = [test_dns]
        my_resolver.timeout = 2
        my_resolver.lifetime = 2
        answer = my_resolver.query(domain)
        result = answer.rrset.items
        iplist = [ip.address for ip in answer.rrset.items]
        if len(iplist) > 0:
            return True
        else:
            return False
    except Exception, e:
        # print Exception, e
        return False


def check_dns(dns_list):
    domain_list = check_domain_list
    faild1 = 0
    for dns in dns_list:
        faild = 0
        for domain in domain_list:
            if not pro_check(dns, domain):
                faild += 1
                logger.error("resolve " + domain + " @" + dns + " faild")
            else:
                logger.info("resolve " + domain + " @" + dns + " ok")
                return True
        if faild == len(domain_list):  # 某一dns全部探测失败才算作失败
            faild1 += 1
    if faild1 >= len(dns_list):
        return False  # 多个dns全部失败才算做该方向失败
    else:
        return True


def view_default_forward_check(view_name, current_rule_id):
    # 检查当前的默认forwarders方向是否故障，检查优先级较高的dns是否恢复
    # 返回值：
    #   1、当前dns正常，且优先级较高的dns故障，返回true
    #   2、当前优先级较高的dns恢复正常或者当前dns故障而有优先级较低的dns正常，返回可用DNS列表
    #   3、所有DNS均故障，返回false

    for checkViewName, checkViewInfo in view_rulers.iteritems():
        if checkViewName == view_name:
            rulers = checkViewInfo['default'].iteritems()
            for ruler_id, dns_list in sorted(rulers, key=lambda a: a[0], reverse=False):
                if (ruler_id == current_rule_id) and check_dns(dns_list):
                    return True
                elif (ruler_id != current_rule_id) and check_dns(dns_list):
                    return (ruler_id, dns_list)
    return False


def check_named_conf_by_named_check():
    cmd = "named-checkconf %s" % named_config_path
    result = os.popen(cmd).read()
    if result != '':
        print(result)
        send_mail(title,
                  '<html><head></head><body>named-checkconf has faild:%s<br/>named will not restart and check script stopd</body></html>' % result)
        exit()


def restart_named_on_7():
    cmd = "systemctl restart named"
    result = os.popen(cmd).read()


def restart_named_on_6():
    cmd = "/etc/init.d/named restart"
    result = os.popen(cmd).read()


def restart_named():
    check_named_conf_by_named_check()
    import platform
    os_version = platform.platform()
    if 'centos-7' in os_version:
        restart_named_on_7()
    else:
        restart_named_on_6()


def start():
    testDNSInfo, testAInfo = load_test_info()  # 加载配置文件
    # check_named_conf_by_named_check()
    conf = NamedConfig(named_config_path)
    current_status = check_conf_file(conf)
    if not current_status:
        print("settings is different from %s" % named_config_path)
        exit()
    start_time = 0
    send_mail(title, "<h3>DNS探测保护脚本已开启。</h3>")
    while conf.check_hash():
        all_msg = "<html><head></head><body>"
        flag = 0
        if not check_named_process():
            msg = "named process is not existed,try restart;"
            logger.info(msg)
            restart_named()
            send_mail(title, msg)
            time.sleep(300)
            continue
        msg = "current DNS is %s" % json.dumps(current_status)
        logger.info(msg)
        # 检查各个view中的默认forward方向
        for view_name, current_rule_id in current_status.iteritems():
            status = view_default_forward_check(view_name, current_rule_id)
            if (type(status) is bool) and (status is False):
                ##全部dns探测失败，准备切换到楚天
                if start_time == 0:  ##初次发现，开始计时，策略不变
                    start_time = time.time()
                    msg = "all of view %s's default forwarders has filed;plan to change dns to %s;left %d s" % (
                        view_name, ";".join(final_default_change_ip[1]), wait_time)
                    logger.info(msg.strip())
                    all_msg += ("%s<br/>" % msg)
                elif time.time() - start_time > wait_time:  ##计时达到标准，切换到楚天方向
                    for one in conf.view_list:
                        if one['name'] == view_name:
                            msg = "change view %s default forwarders to %s;" % (view_name, ';'.join(status[1]))
                            one['info']['forwarders'] = final_default_change_ip[1]
                            current_status[view_name] = final_default_change_ip[0]
                            flag += 1
                            logger.info(msg.strip())
                            all_msg += ("%s<br/>" % msg)
                else:
                    pass
            elif (type(status) is bool) and (status is True):  ##当前策略探测成功，且没有优先级更高的策略成功
                if start_time != 0:  ##若已经开始切换计时，则停止计时
                    start_time = 0
            else:  ## 当前dns探测失败，且有其他dns探测成功
                if status[0] == final_default_change_ip[0]:  ## 其他所有dns探测失败，楚天方向dns探测成功
                    if start_time == 0:  # 初次发现，准备切换到楚天方向
                        start_time = time.time()
                        msg = "plan change view %s default forwarders to %s;left %d s" % (
                            view_name, ";".join(final_default_change_ip[1]), wait_time)
                        logger.info(msg.strip())
                        all_msg += ("%s<br/>" % msg)
                    elif time.time() - start_time > wait_time:
                        for one in conf.view_list:
                            if one['name'] == view_name:
                                msg = "change view %s default forwarders to %s;" % (view_name, ';'.join(status[1]))
                                one['info']['forwarders'] = status[1]
                                current_status[view_name] = status[0]
                                flag += 1
                                logger.info(msg.strip())
                                all_msg += ("%s<br/>" % msg)
                else:  # 其他dns探测成功，正常切换
                    if start_time != 0:  # 若已经开始切换计时，则停止计时
                        start_time = 0
                    for one in conf.view_list:
                        if one['name'] == view_name:
                            msg = "change view %s default forwarders to %s;" % (view_name, ';'.join(status[1]))
                            one['info']['forwarders'] = status[1]
                            current_status[view_name] = status[0]
                            flag += 1
                            logger.info(msg.strip())
                            all_msg += ("%s<br/>" % msg)
        # 检查各view中除默认外的其他forward方向
        for testDNSIp, forwardInfos in testDNSInfo.iteritems():  # forward DNS 监测
            status = check_dns(testDNSIp.split(';'))
            for forwardInfo in forwardInfos["forwardInfo"]:
                if (status is True) and (forwardInfos['status'] is False):  # 链路恢复，forward DNS测试成功
                    flag += 1
                    msg = "add view %s include %s,test dns %s;" % (
                        forwardInfo["viewName"], forwardInfo["forwardName"], testDNSIp)
                    logger.info(msg.strip())
                    all_msg += ("%s<br/>" % msg)
                elif (status is False) and (forwardInfos['status'] is True):  # 链路故障，forward DNS测试失败
                    flag += 1
                    msg = "delete view %s include %s,test dns %s;" % (
                        forwardInfo["viewName"], forwardInfo["forwardName"], testDNSIp)
                    logger.info(msg.strip())
                    all_msg += ("%s<br/>" % msg)
                else:  # 链路状态没有变化
                    pass
            testDNSInfo[testDNSIp]["status"] = status
        for testA, forwardInfos in testAInfo.iteritems():  # CDN主机监测
            status = check_host_by_tcp_ping(testA.split(';'))
            for forwardInfo in forwardInfos["forwardInfo"]:
                if (status is True) and (forwardInfos['status'] is False):  # 主机测试成功
                    flag += 1
                    msg = "view %s include %s,test IP %s success;" % (
                        forwardInfo["viewName"], forwardInfo["forwardName"], testA)
                    logger.info(msg.strip())
                    all_msg += ("%s<br/>" % msg)
                elif (status is False) and (forwardInfos['status'] is True):  # 主机测试失败
                    flag += 1
                    msg = "delete view %s include %s,test A %s;" % (
                        forwardInfo["viewName"], forwardInfo["forwardName"], testA)
                    logger.info(msg.strip())
                    all_msg += ("%s<br/>" % msg)
                else:  # 链路状态没有变化
                    pass

            testAInfo[testA]["status"] = status
        for one in conf.view_list:  # 将探测结果同步到named conf中
            one["info"]["include"] = []
            for forwardName, testInfo in view_rulers[one["name"]]["forwards"].iteritems():
                testDNS = ';'.join(testInfo["testDNS"])
                if "testA" in testInfo:  # 如果存在test host, 判断test host是否成功
                    if (testAInfo[';'.join(testInfo["testA"])]["status"] is True) and (testDNSInfo[testDNS][
                        "status"] is True):
                        one["info"]["include"].append((forwardName, 100))
                else:
                    if testDNSInfo[testDNS]["status"] is True:
                        one["info"]["include"].append((forwardName, 100))
        if flag != 0:
            dump_named_conf()
            if not conf.save():
                break
            restart_named()
            msg = "restart named service"
            logger.info(msg)
            all_msg += ("%s<br/></body></html>" % msg)
            send_mail(title, all_msg)
        time.sleep(5)
    send_mail(title, "%s has been modified by someone,check script stop" % named_config_path)


def tcp_connect(host, port):  #
    from socket import socket, AF_INET, SOCK_STREAM
    tcpClient = socket(AF_INET, SOCK_STREAM)
    tcpClient.settimeout(TCP_TIME_OUT)
    try:
        tcpClient.connect((host, int(port)))
        tcpClient.close()
        return True
    except:
        return False

def check_host_by_tcp_ping(iplist):
    # 通过tcpping检查目标主机是否存活
    for addr in iplist:
        tmp = addr.split(":")
        for _ in range(TCP_RETRY):
            print("%d try"% _ )
            if tcp_connect(tmp[0],tmp[1]) is True:
                return True
    return False

if __name__ == "__main__":
    print check_host_by_tcp_ping(["114.114.114.114:43","8.8.8.8:53"])