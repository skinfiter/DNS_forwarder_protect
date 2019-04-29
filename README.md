#### 执行
nohup python main_check_dns.py &

#### 2019-04-28更新：
1. 增加了tcpping探测主机端口服务状态的功能
2. 增加了初始化时部分对比提示
3. 增加了监控启动时的邮件提醒

#### 2017-12-18更新：
1. 增加配置文件修改检查，若有人修改了配置文件，脚本将停止执行并邮件通知负责人
2. 支持多个view默认forwarder方向不相同
3. 增加了对view中没有include的支持
4. 修正了python2.6环境下的执行错误
5. 修正了psutil判断named进程是否存在时，因某进程结束导致的错误
#### 依赖：dnspython psutil
	http://1.180.208.166:81/soft/python/psutil-3.2.2.tar.gz
	http://1.180.208.166:81/soft/python/dnspython-1.9.4.tar.gz  