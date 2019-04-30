# coding=utf-8

import psutil


def check_named_process():
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            if p.name() == 'named':
                return True
        except psutil.NoSuchProcess:
            pass
    return False


if __name__ == '__main__':
   print (check_named_process())