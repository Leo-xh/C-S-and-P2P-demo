## Client & Server Mode
-------------
![license](https://img.shields.io/github/license/mashape/apistatus.svg) ![continuousphp](https://img.shields.io/continuousphp/git-hub/doctrine/dbal/master.svg)

### Explain
The protocol body is shown below:

![protocol body](https://github.com/Leo-xh/C-S-and-P2P-demo/blob/master/imgs/Message.PNG)


### Services provided:
+ Origin data transfer(Service field is filled with 0).
+ Encryted data transfer(Service field is filled with 1).
+ Look up the catalogue of the server(Service field is filled with 2).

### Server
Provides service, and supports multiple clients requesting resources simultaneously.

### Client
The download folder is set to './downloads'.

### Example
![Example](https://github.com/Leo-xh/C-S-and-P2P-demo/blob/master/imgs/example.gif)
