def ip2int(ip):
    return sum([256**j * int(i) for j, i in enumerate(ip.split('.')[::-1])])
