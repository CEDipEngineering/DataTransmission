from helper import Helper

helper = Helper()

HANDSHAKEMSG = helper.constructParcel(head = bytes([0,0,0,0,0,0,0,0,0,1]), data = bytes([]))
FAILMSG = helper.constructParcel(head = bytes([0,0,0,0,0,0,0,0,0,2]), data = bytes([]))
SUCCESSMSG = helper.constructParcel(head = bytes([0,0,0,0,0,0,0,0,0,3]), data = bytes([]))
SERVERERRORMSG = helper.constructParcel(head = bytes([0,0,0,0,0,0,0,0,0,4]), data = bytes([]))
CLIENTERRORMSG = helper.constructParcel(head = bytes([0,0,0,0,0,0,0,0,0,5]), data = bytes([]))
