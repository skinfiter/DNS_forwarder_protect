from check_dns import *

#   info:DNS check and change
# 	version: 0.0.3
# 	date: 2019-04-26
#   write by songsx@net-east.com


VERSION = "0.0.3"
VERSION_DATE = "2019-04-26"
DESCRIBE = """
    dns forward list and default forward protect.
    update 2018-05-30:
        add chuian special change
    update 2019-04-26:
        add test host status 
"""


def show_versions():
    print('Version:%s\nBuild date:%s' % (VERSION, VERSION_DATE))


if __name__ == "__main__":
    if sys.argv.__len__() == 1:
        start()
    else:
        show_versions()
