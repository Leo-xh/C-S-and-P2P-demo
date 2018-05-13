## Bittorrent
----
![license](https://img.shields.io/github/license/mashape/apistatus.svg) ![continuousphp](https://img.shields.io/continuousphp/git-hub/doctrine/dbal/master.svg)
A p2p application, using bittorrent protocol. We name it Compact Bittorrent Protocol.

Features:
1. Using Twisted and asynchronous programming.
    We use Twisted programming framework and thus our program is asynchronous. It won't wasting the CPU resource when there is no job, which is different from using raw sockets.
    The event-driven mode we used also improve the behavior of our program.
2. We implement a basic Bittorrent protocol, and apply some extension to out extension:
    + UDP tracker protocol.
    + Compact format of peer list.
3. As for normal functions, the program support broken point re-continue.

    