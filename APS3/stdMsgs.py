from helper import Helper

helper = Helper()

SERVERALIVEMSG = helper.constructParcel(head = bytes([2,0,0,0,0,0,0,0,0,0]), data = bytes([]))
TIMEOUTMSG = helper.constructParcel(head = bytes([5,0,0,0,0,0,0,0,0,0]), data = bytes([]))
