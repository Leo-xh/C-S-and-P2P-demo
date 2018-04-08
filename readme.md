Computer Networking Project - C/S and P2P demo

A python project of Computer Networking Course

Note that python will use tcp if we use socket packet and use its connection.

Both the C/S project and P2P project require a well designed protocol in application layer. 

### What is Protocol in Application Layer
A protocol should includes：

1. Code Control(decoder and encoder).
2. Procedures Control

#### Hand in hand to design a application  protocol

协议分类：

+ 按编码分类：
    * 二进制
    * 明文
    * 混合
+ 按协议边界
    * 固定边界，即能够明确得知一个协议报文的长度。
    * 模糊边界，即无法明确知道协议报文的长度，通常需要通过某些特定的字节来界定报文是否结束。

协议评判：

+ 高效，包括打包解包，数据压缩率
+ 简单
+ 易于扩展
+ 容易兼容

知识储备

+ 大小端
+ 网络字节序，一般是大端的。
    socket库中提供了htonl(s)和ntohl(s)来实现本地字节序和网络字节序的转化。
+ 序列化与反序列化

协议设计

协议头和协议体，注意协议魔数

协议的基本单元

消息是协议的基本单元。有许多种方式将数据流正确切分成消息，对于文本协议，可以采用标志的方法，或向json或xml一样区分出多个首尾相连的JSON或XML的边界。而对于二进制数据流，最简单的方法是再数据开头明确地写出这个消息的长度。

对消息是否具有明确的标识，比如对于客户端发送的每个请求，服务器都需要给出一个相应的应答消息，而且顺序完全一致；或者是较为优越的使用ID的机制。

协议头内容参考：类型、长度、版本、ID、魔数、服务号

错误信息的处理：最好有一种不随版本升级变化的错误信息，比如用一个字段来表示错误类型，再最佳一个字段来表示错误码，还有一个字段来表示错误描述。

应用层探活：
服务器和客户端都需要定时探测对方的连接是否通畅，通过echo-reply机制。一般来说reply将echo数据包原封不动地返回，数据包上还可以包含其他的数据，来进行贷款或者时延等等的检查。

RFC 4101
----

[Writing Protocol Models](https://tools.ietf.org/html/rfc4101)

A protocol model needs to answer three basic questions:

1. What problem is the protocol trying to achieve?
2. What messages are being transmitted and what do they mean?
3. What are the important, but unobvious, features of the protocol?

Basic Principles
----
### C/S Transfer Protocol Model
----

TCP principles(the contents that can be found in the textbook is omitted):

短连接：连接 $\to$ 传输数据 $\to$ 关闭连接，即短连接是指socket连接后发送后接受完数据后马上断开连接。

长连接：连接 $\to$ 传输数据 $\to$ 保持连接 $\to$ 传输数据 $\to$ $\dots$ $\to$ 关闭连接，即长连接指建立socket连接后不管是否使用都保持连接。

TCP disadvantages:

注意TCP中只有数据流的概念而没有数据包的概念，所以会出现以下“包”的问题。

1. 粘包、半包、分包。

    reasons:
    粘包：发送方将较小的数据包进行合并，或者接收方没有将数据包即使取走，一次性取出了多个数据包。

    半包：指接受方没有接受到一个完整的包，只接受了部分，这种情况主要是由于TCP为提高传输效率，将一个包分配的足够大，导致接受方并不能一次接受完。

    分包：可能是IP分片传输导致的，也可能是传输过程中丢失部分包导致出现的半包，还有可能就是一个包可能被分成了两次传输，在取数据的时候，先取到了一部分（还可能与接收的缓冲区大小有关系），总之就是一个数据包被分成了多次接收。
    
    什么时候需要考虑粘包的情况?  

    如果发送数据无结构，如文件传输，这样发送方只管发送，接收方只管接收存储就ok，也不用考虑粘包。
    注意粘包情况有两种，一种是粘在一起的包都是完整的数据包，另一种情况是粘在一起的包有不完整的包。

    solutions:

    + adding delimiters to the packets.
    + adding length information in the packets.
    + RingBuf
    
    What is RingBuf?

    感觉没什么用。
    
#### 协议设计

1. 报文设计

    4.6 讨论：

    二进制和固定边界的协议。

    请求和响应分开

    请求报文：
        类型（协议）、服务、版本、文件名（200bytes)、序号（指明是哪一个请求）

    响应：
        类型（协议）、服务、版本、序号、错误码、长度、数据（数据中加入分隔符）

    长度为0时代表文件传输完毕

    ​错误码：

| 错误码 | 描述           |
| ------ | -------------- |
| 0      | successful     |
| 1      | does not exist |

​	协议如下图所示：

​	![协议体](https://github.com/Leo-xh/C-S-and-P2P-demo/blob/master/imgs/Message.PNG)

​	数据体：
        1. 需要分隔符（0xffff）来处理TCP粘包、半包、分包问题。
        2. 如何切分数据：按最大的切分（2MB）

客户端：
​	1. 发请求
​	2. 多线程
​	3. 交互式

服务器端：
​	1. 接受请求并解析
​		+ 文件存在：根据长度打包
​		+ 文件不存在：设置错误码返回
​	2. 支持多线程

支持加密功能


控制流程设计

clients request

- if the resource request exists

  server reply, and then send the required resource.

- if it doesn't exists

  server reply, and send message.

server close the connection.


文件样例：

![test1.gif](https://github.com/Leo-xh/C-S-and-P2P-demo/blob/master/C-S/Resources/test1.gif)
![test2.gif](https://github.com/Leo-xh/C-S-and-P2P-demo/blob/master/C-S/Resources/test2.gif)








|\|类型\|魔数\|版本\|服务号\||
|---|
|ID|
|长度|
|数据体|

+ 类型：指明协议
+ 魔数：用以判断协议数据传输是否出错
+ 版本：协议版本
+ 服务号：指明协议上的服务
+ ID：同一个响应的第几个报文
+ 长度：报文的总长度
+ 数据体：数据

前四个各一字节，后两个各4字节。

则数据体的大小范围足够大，ID也足够多。

数据体可以根据类型的不同和服务号的不同而不同，分为二进制和明文类型。

大概思路就是根据类型和版本、服务号来确定数据体中的内容含义。

客户端请求数据报时可以将服务号设置，服务器响应则是设置相同的服务号，内容再数据体的特定位置。

1. 控制流程设计

    clients request

    + if the resource request exists

        server reply, and then send the required resource.

    + if it doesn't exists

        server reply, and send message.

    server close the connection.

### P2P Transfer Protocol Model
----
+ BitTorrent Protocol--BTP/1.0

    The details of BitTorrent Protocol are shown in this [website](http://jonas.nitro.dk/bittorrent/bittorrent-rfc.html)(**I think this one is much better**).
    
    And this [wikipedia page](https://wiki.theory.org/index.php/Main_Page).

    [Official website](http://www.bittorrent.org/beps/bep_0000.html)

+ Implementation
  
    1. [Lita's BitTorrent Implementation](https://github.com/lita/bittorrent) may be my main reference.

        * Pay attention to Pull Requests.
        * The issue #3 tells that there is a bug in the implementation. 

    2. [Zadexter's Implementation](https://github.com/zdexter/py-bittorrent/issues)
        * 这个大哥的博客不见了，待回复。

    3. [Over middle boxes such as NAT](https://github.com/pannzh/P2P-Over-MiddleBoxes-Demo)

+ Good tutorials
    * [How to Write a Bittorrent Client - Part 1](http://www.kristenwidman.com/blog/33/how-to-write-a-bittorrent-client-part-1/)
        - Why did pip install bencode doesn't work?
    * [How to Write a Bittorrent Client - Part 2](http://www.kristenwidman.com/blog/71/how-to-write-a-bittorrent-client-part-2/)
        - use [bitstring.BitArray](https://pythonhosted.org/bitstring/bitarray.html) to handle "bitfield" message.
        - block size is in debate, and a short answer is $2^{14}(16384)$.
        - design when to write the received data to the files, remember that a piece may contains data for multiple files.

+ BitTorrent Specification Reading Notes
    * Specification Terminology
        - peers refers to BitTorrent clients running on other machines.
        - piece refers to a portion of the downloaded data described in the metainfo file. A block is a portion of data that a client request from a peer. Two or more blocks make up a whole piece.
        - Swarm refers to peers that actively operate on a given torrent.
        - Seeder refers to a peer that has a complete copy of a torrent.
    * Metainfo File Structure
        - piece size is set to 512KB, of best-practice.
    * Overall Operation
        - Tracker HTTP Protocol(THP)
            + The tracker is an HTTP/HTTPS service which responds to HTTP GET requests.
            + THP defines a method for contacting a tracker for the purposes of joining a swarm, reporting progress etc. 
            + The selected port number is stored in Tracker.
        - Peer Wire Protocol(PWP)
            + PWP defines a mechanism for communication between peers, and is thus responsible for carrying out the actual download and upload of the torrent.
        - Details
            + In order for a client to download a torrent the following steps 
            must be carried through:
                1. A metainfo file must be retrieved.
                2. Instructions that will allow the client to contact other peers must be periodically requested from the tracker using THP.
                3. The torrent must be downloaded by connecting to peers in the swarm and trading pieces using PWP.
            + To publish a torrent the following steps must be taken:
                1. A tracker must be set up.
                2. A metainfo file pointing to the tracker and containing information on the structure of the torrent must be produced and published.
                3. At least one seeder with access to the complete torrent must be set up(the "origin").

+ Advanced and Accepted Extended Protocol
    * DHT(The most expected to implement)
        - This is implemented over UDP.
        - Distance metric is XOR : 
            $$distance(A, B) = |A \ xor \ B|.$$
        - Nodes maintain routing table.
    * Peer Exchange(PEX)
        - Peer Exchange (PEX) provides an alternative peer discovery mechanism
        for swarms once peers have bootstrapped via other mechanisms such as DHT or Tracker announces.
    * UDP Tracker Protocol for BitTorrent
        - To discover other peers in a swarm a client announces it's existance to a tracker. The HTTP protocol is used and a typical request contains the following parameters: info_hash, key, peer_id, port, downloaded, left, uploaded and compact. A response contains a list of peers (host and port) and some other information. The request and response are both quite short. Since TCP is used, a connection has to be opened and closed, introducing additional overhead.

### Programming Details
----
+ how to use socket in python?

    [A brief tutorial](https://blog.csdn.net/weixin_37656939/article/details/79813704)

+ how to design a protocol?

    [A hand in hand tutorial](https://segmentfault.com/a/1190000008740863) 
    (learning its codes carefully!)

+ Python Network Programming Cookbook

    * How to reuse the port:
      
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

+ [Send and receive files by python](https://blog.csdn.net/luckytanggu/article/details/53491892)

+ Deal with big file
    * [reference-1](http://www.jb51.net/article/103392.htm)
    * [reference-2](https://blog.csdn.net/m0_37886429/article/details/78730766)

    The main thought is to loop and send the data part by part.

+ Multithreading in Python
    * [Xuefeng Liao's toturials](https://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001386832360548a6491f20c62d427287739fcfa5d5be1f000)
    * [Another toturials](http://www.runoob.com/python/python-multithreading.html)

+ Protocol Buffer
    To serialize and deserialize pakcet, [see](https://developers.google.com/protocol-buffers/docs/pythontutorial).

+ Struct in Python
    Deal with the header with struct library.
    [usage of struct](https://docs.python.org/2/library/struct.html)
    [An example](http://lib.csdn.net/article/python/39858)
    
    使用方法：可以再unpack的时候只unpack某几个字节，得到长度再继续unpack。

+ Twisted Framework
    * [Chinese Introduction](https://blog.csdn.net/hanhuili/article/details/9389433)
    * [Official Document](https://blog.csdn.net/hanhuili/article/details/9389433)

+ [Encryption](https://www.cnblogs.com/yyds/p/7072492.html)
    * [Sha1 Hash(Unidirectional encryption)](https://docs.python.org/2/library/hashlib.html)
    * [AES(Symmetric encryption)](http://pythonhosted.org/pycrypto/)
