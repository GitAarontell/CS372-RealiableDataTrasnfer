from segment import Segment
import math


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4  # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15  # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0  # Use this for segment 'timeouts'
    charCount = 0
    dataReceived = ''
    countSegmentTimeouts = 0
    ackNum = 0
    receivingListHistory = []

    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self, data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...

        # ############################################################################################################ #
        return self.dataReceived

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        if len(self.dataToSend) == 0:
            return

        # ############################################################################################################ #
        print('processSend(): Complete this...')

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqNum is the sequence number for the segment (in character number, not bytes)

        charsLeftToSend = len(self.dataToSend) - self.charCount
        totalPacketsLeft = math.ceil(charsLeftToSend / self.DATA_LENGTH)
        segmentsToSend = math.floor(self.FLOW_CONTROL_WIN_SIZE / self.DATA_LENGTH)

        if totalPacketsLeft < segmentsToSend:
            segmentsToSend = totalPacketsLeft

        for p in range(segmentsToSend):
            segmentSend = Segment()
            data = ''
            # set seqNum to index of first data being sent in packet
            seqNum = self.charCount
            # if the index of charCount is ever equal to the len of data to send, then all data has been sent
            # else continue to send data
            if self.charCount < len(self.dataToSend):
                # counter used to make sure each packet only gets a max of the data_length allowed per packet
                counter = 0
                # add rest of data after setting correct seqNum
                while self.charCount < len(self.dataToSend):
                    data += self.dataToSend[self.charCount]
                    # increment charCount to keep track of what index char of data we are on
                    # counter keeps track of how many char's we have sent within the limit of this packet size
                    self.charCount += 1
                    counter += 1
                    if counter == self.DATA_LENGTH:
                        break

            # ######################################################################################################## #
            # sets up segment with data
            segmentSend.setData(seqNum, data)
            # Display sending segment
            print("Sending segment: ", segmentSend.to_string())
            # Use the unreliable sendChannel to send the segment
            self.sendChannel.send(segmentSend)

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        print("Process Receive")
        # This call returns a list of incoming segments (see Segment class)...
        # receive() returns a list of all the sent packets

        listIncomingSegments = self.receiveChannel.receive()
        #listIncomingSegments += self.receivingListHistory
        #self.receivingListHistory.clear()

        self.bubbleSort(listIncomingSegments)
        for seg in listIncomingSegments:

            seg.printToConsole()
            # if the payload of the segment is not empty then it is a data segment else it is an ACK
            if seg.seqnum > -1:
                #if seg.seqnum != self.ackNum:
                #    self.receivingListHistory.append(seg)
                #    continue

                # #################################################################################################### #
                # What segments have been received?
                # How will you get them back in order?
                # This is where a majority of your logic will be implemented

                self.dataReceived += seg.payload
                # #################################################################################################### #
                # How do you respond to what you have received?
                # How can you tell data segments apart from ack segments?
                segmentAck = Segment()  # Segment acknowledging packet(s) received

                # Somewhere in here you will be setting the contents of the ack segments to send.
                # The goal is to employ cumulative ack, just like TCP does...
                print("Value we should be comparing it to")
                print(self.ackNum)
                print(seg.seqnum)
                self.ackNum = seg.seqnum + 1

                # #################################################################################################### #
                # Display response segment
                segmentAck.setAck(self.ackNum)
                print("Sending ack: ", segmentAck.to_string())

                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)

    def bubbleSort(self, arr):
        n = len(arr)
        # optimize code, so if the array is already sorted, it doesn't need
        # to go through the entire process
        swapped = False
        # Traverse through all array elements
        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if arr[j].seqnum > arr[j + 1].seqnum:
                    swapped = True
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

            if not swapped:
                return
