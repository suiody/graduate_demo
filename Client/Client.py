#!/usr/bin/env python
import sys
sys.path.append('..')

from ClientData import ClientData
from ClientControl import ClientControl
import threading
import time
from threading import Timer
from Utils.Log import Log

Idle = 0
WaitAssign = 1
GetFreq = 2
StartData = 3
FreqRelease = 4

TimerDuration = 2 #sec

class Client(object):
    def __init__(self):
        self.dataChannel = None
        self.ctlChannel = None
        self.ctlChannel = ClientControl(2, self.freqAssignCB, self.freqReleaseACKCB)
        self.stateLock = threading.Lock()
        self.state = IDLE
        self.log = Log('ClientLog.txt')
        pass

    def startDataChannel(self):
        self.log.LogStr("start data channel")

        self.dataChannel = ClientData()
        self.dataChannel.start()

    def endDataChannel(self):
        if self.dataChannel:
            self.log.LogStr("stop data channel")
            self.dataChannel.stop()
            self.dataChannel.deconstruction()
            del self.dataChannel
            self.dataChannel = None
        else:
            self.log.LogStr("endDataChannel but dataChannel is none")

    def freqAssignThreadCB(self, width):
        self.log.LogStr("freqAssignThread call callback")
        self.stateLock.acquire()
        self.log.LogStr("the state is %d" % (self.state))
        if self.state == GetFreq:
            self.endCtlChannel()
            self.startDataChannel()
            self.state = StartData
        self.stateLock.release()

    def freqReleaseACKCB(self, payload):
        self.stateLock.acquire()
        if self.state == FreqRelease:
            self.endCtlChannel()
            self.ctlChannel.finishFreqReq()
            self.state = Idle
        self.stateLock.release()

    def userInteractThreadCB(self):
        while True:
            command = raw_input("command:")
            if command == 'start':
                self.stateLock.acquire()
                if self.state == Idle:
                    self.startCtlChannel()
                    self.sendCtlChannelRequest()
                    self.state = WaitAssign
                    self.freqReqTimer = Timer(TimerDuration, self.freqReqTimeoutCB)
                self.stateLock.release()
            elif command == 'end':
                self.stateLock.acquire()
                if self.state == WaitAssign:
                    self.ctlChannel.sendFreqRelease()
                elif self.state == GetFreq:
                    self.ctlChannel.sendFreqRelease()
                elif self.state == StartData:
                    self.endDataChannel()
                    self.startCtlChannel()
                    self.ctlChannel.sendFreqRelease()
                else:
                    continue
                self.state = FreqRelease
                self.stateLock.release()
                self.freqReleaseTimer = Timer(TimerDuration, self.freqReleaseTimeoutCB)
            elif command == 'quit':
                self.stateLock.acquire()
                if self.state == Idle:
                    self.ctlChannel = None
                    break
                break
            elif command == "help":
                print "start: start control channel and send request"
                print "end: end control channel and data channel"
                print "quit: end the client"
                print "help: show this message"
                
    def freqReqTimeoutCB(self):
        self.stateLock.acquire()
        if self.state == WaitAssign:
            self.sendCtlChannelRequest()
            self.freqReqTimer = Timer(TimerDuration, self.freqReqTimeoutCB)
        self.stateLock.release()

    def freqReleaseTimeoutCB(self):
        self.stateLock.acquire()
        if self.state == FreqRelease:
            self.ctlChannel.sendFreqRelease()
            self.freqReleaseTimer = Timer(TimerDuration, self.freqReleaseTimeoutCB)
    def freqAssignCB(self, width): #1 is big 2 is small
        if width == 1:
            self.freqAssignThread = threading.Thread(Target=self.freqAssignThreadCB, args=[width])
            self.freqAssignThread.start()
        else:
            self.startDataChannel()

    def startCtlChannel(self):
        if self.dataChannel:
            self.endDataChannel()
        if not self.ctlChannel:

        print "start ctl channel"
        self.ctlChannel.construct()
        self.ctlChannel.start()

    def sendCtlChannelRequest(self):
        if self.ctlChannel:
            print "send control channel request"
            self.ctlChannel.sendFreqReq()

    def endCtlChannel(self):
        print "end ctl channel"
        self.ctlChannel.stop()
        self.ctlChannel.deconstruct()

    def endAll(self):
        if self.ctlChannel:
            self.endCtlChannel()
            self.ctlChannel = None
        if self.dataChannel:
            self.endDataChannel()

    def reqTimeoutCB(self):
        self.timeoutNumber += 1
        if self.state != 1:
            return
        if self.timeoutNumber > 10:
            self.state = 3
        else:
            self.state = 0
        self.dealWithStateMachine()

    def work(self):
        self.startCtlChannel()
        time.sleep(1)
        self.endCtlChannel()
        self.startDataChannel()


if __name__ == "__main__":
    client = Client()
    try:
        client.userInteractThreadCB() 
    except KeyboardInterrupt:
        pass
    client.endAll()
