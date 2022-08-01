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

        # calculate total chars left to send
        charsLeftToSend = len(self.dataToSend) - self.charCount
        # calculate packets based on the chars left to send and the data length constant
        totalPacketsLeft = math.ceil(charsLeftToSend / self.DATA_LENGTH)
        # segments to send is the rounded down flow control window size divided by the payout size
        segmentsToSend = math.floor(self.FLOW_CONTROL_WIN_SIZE / self.DATA_LENGTH)
        # if however, the total packets left is less than the current segments to send, then set segements to send
        # to the total packets left. So basically, when there is less than 3 packets to send, total packets left will
        # be either 1 or 2, and so that will be what segments to send is set to.
        if totalPacketsLeft < segmentsToSend:
            segmentsToSend = totalPacketsLeft

        # pipline segments depending on the flow control window size and the data length constants
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

        # get packets from receive channel
        listIncomingSegments = self.receiveChannel.receive()
        # add segments just received to the segments that have been delayed in processing
        listIncomingSegments += self.receivingListHistory
        # clear the delayed segments array
        self.receivingListHistory.clear()

        # sort the current listIncomingSegments to be viewed
        self.segmentBubbleSort(listIncomingSegments)
        # loop through all the segments in the list incoming segments that have now been ordered
        for seg in listIncomingSegments:

            seg.printToConsole()
            # if the sequence number matches the ack number we are looking for then process it, if not then it
            # is out of order, and we just put that segment into the receiving list history array to look at
            # on the next processing, and skip this iteration.
            if seg.seqnum > -1:
                if seg.seqnum != self.ackNum:
                    self.receivingListHistory.append(seg)
                    continue

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
                self.ackNum += len(seg.payload)

                # #################################################################################################### #
                # Display response segment
                segmentAck.setAck(self.ackNum)
                print("Sending ack: ", segmentAck.to_string())

                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)

    def segmentBubbleSort(self, arr):
        n = len(arr)
        swap = False
        # Traverse through all array elements
        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if arr[j].seqnum > arr[j + 1].seqnum:
                    swap = True
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
            if not swap:
                return
