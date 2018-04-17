while True:

    print('Pls input a number:', end='')
    num = input()
    if num.isdigit():  # 判断输入是否是纯数字(不包括'-')
        num = int(num)
        break
    else:
        print('\x1b[1A\x1b[2K' + '\r*****  ' + '\x1b[1;31m' + 'Not A Number!' + '\x1b[0m'
              + '  *****', end='')
        print('\x1b[2K\r')
        # 1 光标移到到上一行头部并清空光标所在行的所有字符
        # 2 光标回到头部 并打印'*****  '
        # 3 改变前景色为亮红色
        # 4 打印'Not A Number!'
        # 5 重置所有颜色为默认值
        # 6 打印'  *****'
        # 7 延迟后再次清空行 并使光标回到头部
