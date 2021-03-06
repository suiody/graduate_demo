#!/usr/bin/env python
from gnuradio.eng_option import eng_option
from gnuradio import gr
from optparse import OptionParser
import struct, sys
from transceiver import transceiver


import time

def main():
    global n_rcvd, n_right
        
    n_rcvd = 0
    n_right = 0

    def rx_callback(ok, payload):
        global n_rcvd, n_right
        n_rcvd += 1
        (pktno,) = struct.unpack('!H', payload[0:2])
        if ok:
            n_right += 1
            print "he says:", payload[2:]
        print "ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right)

    tr = transceiver(rx_callback)
    
    tr.start()
    sendPktno = 0
    try:
        while True:
            content = raw_input("I say:")
            content = struct.pack("!H", sendPktno) + content
            sendPktno += 1
            tr.send_pkt(content)
            time.sleep(0.1)
            if content == 'end':
                break
    except KeyboardInterrupt:
        pass
    print ''
    tr.send_pkt(eof = True)
    tr.stop()
    tr.wait()

if __name__ == '__main__':
    main()

