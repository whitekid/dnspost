> **dnsmasq has better functionality. please use dnsmasq**
> 
> ```sh
> server=/github.com/168.126.63.1
> server=/google.com/8.8.8.8
> address=/my.local/192.168.0.1
> ```
> 

----
DNS Proxy similar to OSX resolver functionality.

You can specify dns server by requested host name

Installation
============
```
$ apt-get install python-twisted-names
$ git clone https://github.com/whitekid/dnspost.git
$ cd dnspost
# edit dnspost.conf
$ ./dnspost.py
```

register to upstart to run on system startup
============================================
```
$ cp upstart/dnspost.conf /etc/init/dnspost.conf
$ cp dnspost.py /usr/bin/dnspost
$ cp dnspost.conf /etc/dnspost.conf
$ ln -s /lib/upstart-job /etc/init.d/dnspost
$ service start dnspost
```

Ubuntu and NetworkManager Note
==============================
1. disable NetworkManager's dnsmasq usage
comment out dnsmasq settings in /etc/NetworkManager/NetworkManager.conf
```
#dns=dnsmasq
```

2. set default dns server to 127.0.0.1

3. restart network-manager
```
$ service network-manager restart
```

4. edit dnspost.conf to dnspost run on port 53
```
listen_port=53
```

4. restart dnspost
```
$ service dnspost restart
```

5. test
```
$ dig github.com
```