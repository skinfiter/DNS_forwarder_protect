# encoding=utf-8

import os
import sys
import time
import shutil
from config import *
from mylogger import *
from named_conf_parser import NamedConfig


def dump_named_conf():
    # 备份named.conf文件
    script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    time_step = time.strftime("%Y%m%d%H%M%S", time.localtime())
    back_config_path = os.path.join(script_path, ".back_config")
    config_name = os.path.split(named_config_path)[-1]
    back_config_name = os.path.join(back_config_path, "%s-%s" % (config_name, time_step))
    if os.path.isdir(back_config_path) is False:
        os.mkdir(back_config_path)
    shutil.copyfile(named_config_path, back_config_name)
    logger.info("dump config file to:%s" % back_config_name)


def read_named_conf():
    with open(named_config_path, 'r') as f:
        named_conf = f.read()
        f.close()
    return named_conf


# def clear_conf():
#     # 清理配置文件中的注释
#     named_conf = read_named_conf()
#     cleared_conf_file = []
#     if "#" in named_conf or "//" in named_conf:
#         for _line in named_conf.splitlines():
#             if "#" in _line:
#                 line = _line.split("#")[0]
#             elif "//" in _line:
#                 line = _line.split("//")[0]
#             else:
#                 line = _line
#             if len(line) == 0:
#                 continue
#             cleared_conf_file.append(line)
#         dump_named_conf()
#         write_conf_file(cleared_conf_file)
#         logger.info("clear config file!")
#     else:
#         cleared_conf_file = [one for one in named_conf.splitlines()]
#     return cleared_conf_file


def check_conf_file(conf):
    # 检查各个forwarder方向是否一致，并返回当前forwarder方向
    every_view_default_forwarders = {}
    if len(view_rulers) != len(conf.view_list):
        print('some view not match,please check...')
        return False
    else:
        for namedView in conf.view_list:
            print('check view %s config...' % namedView['name'])
            if namedView['name'] not in view_rulers:  # check conf和named conf中相同的view name进行比较
                print("%s not in check config,please check ...")
                return False
            else:
                checkView = view_rulers[namedView['name']]
                if checkView['forwards'] != {} and 'include' in namedView['info']:
                    if not cmp_forwards(checkView['forwards'], namedView['info']['include']):
                        return False
                elif checkView['forwards'] == {} and 'include' not in namedView['info']:
                    pass
                else:
                    print("%s has not forward list,but check_conf have,please check ..." % named_config_path)
                    return False
                default_forwarders_id = default_forwarders_in_list(checkView['default'],
                                                                   namedView['info']['forwarders'])
                if not default_forwarders_id:
                    print("default forward list not match check_conf,please check... ")
                    return False
                every_view_default_forwarders[namedView['name']] = default_forwarders_id
    return every_view_default_forwarders


def default_forwarders_in_list(setting_default_forwarders, conf_forwarders_list):
    for ruler_id, ruler in setting_default_forwarders.iteritems():
        if set(ruler) == set(conf_forwarders_list):
            return ruler_id
    return False


def cmp_forwards(setting_forwards_list, conf_forwards_list):
    # 比较两个forwards list是否相同
    if len(conf_forwards_list) != len(setting_forwards_list):  # 数量不同，直接跳出
        return False
    for forward in conf_forwards_list:  # 某个forward在check conf中没有配置
        if forward[0] not in setting_forwards_list:
            return False
    return True


if __name__ == "__main__":
    conf = NamedConfig(named_config_path)
    print check_conf_file(conf)
