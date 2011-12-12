from socket import *
from SocketUtils import recvFixedLen
import time
import struct
import threading

host = 'localhost'
port = 12341
addr = (host,port)

REQUEST=1
ALLOCATE=2
RELEASE=3

class EstServer(object):
    def __init__(self):
        self.tcpSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpSocket.bind(addr)
        self.tcpSocket.listen(5)
        self.requestId = 0
        self.reqs = {}
        self.reqInstance = []
        self.serviceTimes = []
        self.maxFreq = 300000
        self.freeFreq = self.maxFreq
        time.clock()
        self.f2 = 0.8
        self.f3 = 0.9
        self.f1 = 0.7
        self.f4 = 0.99
        self.nowSatis = 1.0
        self.minSatis = 0.3
        self.est_serviceTime = 72
        self.est_lambda = 1

        self.oneBw = 1300
        self.logThread = threading.Thread(target=self.logFreeSpectrum,args=())
        self.endLog = False
        
        self.estimate_num = 300
        self.queue_len = 0
    def calSatisfaction(self,lamb):
        queueLen = lamb * self.serviceTime
        r = self.f2*self.maxFreq/(queueLen*self.oneBw)
        if r>1:
            r = 1
        print "satisfaction %f" % r
        return r
        pass
    def stop(self):
        self.stopListen = True

    def listen(self):
        self.stopListen = False
        self.logThread.start()
        print 'wait for connection'
        self.tcpCliSock,addr = self.tcpSocket.accept()
        print 'receive one connection'
        try:
            while not self.stopListen:
                data = recvFixedLen(self.tcpCliSock,1)
                
                command = struct.unpack('!b',data)[0]
                if command == REQUEST:
                    #print 'receive one request'
                    #add one request time instance
                    self.reqInstance.append(time.clock())
                    #recv the request bw
                    data = recvFixedLen(self.tcpCliSock,8)
                    (bw, serTime) = struct.unpack('!ff',data)
                    self.serviceTimes.append(serTime)
                    bwAllo = self.dealWithOneRequest(bw)
                    self.freeFreq -= bwAllo
                    self.buildOneAllocation(bwAllo)
                    self.queue_len += 1
                elif command == RELEASE:
                    #print 'receive one release'
                    data = recvFixedLen(self.tcpCliSock,4)
                    bwAllo = struct.unpack('!f',data)[0]
                    print 'add spectrum ' + str(bwAllo) + ' '+str(time.clock())
                    self.freeFreq += bwAllo
                    self.queue_len -= 1
        except:
            pass
        self.endLog = True
        self.logThread.join()
    def estimateLambda(self,estimateNum = 100):
        if len(self.reqInstance) < estimateNum + 1:
            return -1
        averageTime = self.reqInstance[-1]-self.reqInstance[-1-estimateNum]
        averageTime /= estimateNum
        estLambda = 1.0/averageTime
        print 'estimate lambda '+str(estLambda)
        allServiceTimes = 0
        for i in range(estimateNum):
            allServiceTimes += self.serviceTimes[-1-i]
        self.serviceTime = allSercieTimes/estimateNum
        return estLambda
    def dealWithOneRequest(self,bw):
        if (1-self.f1)*self.maxFreq < self.freeFreq:
            # rich state
            self.estimate_num = 100
            if self.nowSatis < 1.0:
                self.est_lambda = self.estimateLambda()
                if self.est_lambda > 0:
                    self.nowSatis = self.calSatisfaction(self.est_lambda)
            return self.nowSatis * bw
        elif (1-self.f3)*self.maxFreq < self.freeFreq:
            #Normal state
            self.estimate_num += 1
            if self.estimate_num % 5 == 0:
                self.est_lambda = self.estimateLambda(self.estimate_num)
                if self.est_lambda > 0:
                    self.nowSatis = self.calSatisfaction(self.est_lambda)
            return self.nowSatis * bw
        elif (1-self.f4)*self.maxFreq < self.freeFreq:
            self.estimate_num = 100
            #poor state
            self.est_lambda = self.estimateLambda()
            if self.est_lambda > 0:
                self.nowSatis = self.calSatisfaction(self.est_lambda)
            return self.nowSatis * bw
        else:
            #terrible state
            self.estimate_num = 100
            return 0
    def buildOneAllocation(self,bwAllo):
        data = struct.pack('!bf',ALLOCATE,bwAllo)
        self.tcpCliSock.send(data)
        pass
    
    def logFreeSpectrum(self):
        logFile = file('server_spectrum.txt','w')
        time.clock()
        while not self.endLog:
            logFile.write(str(time.clock()) +' '+ str(self.freeFreq)+' '+str(self.nowSatis)+' '+str(self.est_lambda)+' '+str(self.queue_len)+'\n')
            time.sleep(1)
        logFile.close()

if __name__ == '__main__':
    ser = EstServer()
    ser.listen()
