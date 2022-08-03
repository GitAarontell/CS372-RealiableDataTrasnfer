from segment import Segment
import math
import copy


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
    # used to count what bit we currently need to send, correlates to the index of string in dataToSend
    charCount = 0
    # adds up data received when that data is a data segment
    dataReceived = ''
    countSegmentTimeouts = 0
    ackNum = 0
    # used for holding segments that are not supposed to be received just yet when server is waiting for correct segment
    receivingListHistory = []
    # shows the bit range we are currently at in the window
    slidingWindow = [0, FLOW_CONTROL_WIN_SIZE - 1]
    # holds the packets that are waiting for acknowledgment
    awaitingAckSegments = []
    # used to stop checking the range of sliding window when final data char indices are reached
    lastCheck = False

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

        # used so only the client uses this send to send data packets
        if len(self.dataToSend) == 0:
            return
        print()
        print("###############################################################################")
        print("Client Process Send from Reliable Layer")
        print("###############################################################################")
        print()
        # ############################################################################################################ #
        # this tracks the number of iterations of current segments in the sliding window
        # and if the iterations reached 2, or whatever number you put in, then it will retransmit packets
        # that have not yet been acknowledged.
        for seg in self.awaitingAckSegments:
            if self.currentIteration - seg.getStartDelayIteration() == 2:
                self.countSegmentTimeouts += 1
                seg.setStartDelayIteration(self.currentIteration)
                copySeg = copy.deepcopy(seg)
                print("### Re-Sending segment: ", seg.to_string())
                self.sendChannel.send(copySeg)

        # if the sliding window is currently full or is waiting for ack's before it can move the sliding window
        # up, then it will not send any packets
        if self.charCount > self.slidingWindow[1]:
            print("Sliding Window Currently Full Waiting for ACK's")
        else:
            # if there is space in the sliding window to send packets then it will
            # this creats initial values to be used for the segment when we send
            segmentSend = Segment()
            data = ''
            # add the char, at the self.charCount index in dataToSend, to the data variable
            data += self.dataToSend[self.charCount]
            # set sequence number to the current charCount which will start as 0
            seqNum = self.charCount
            # increment charCount to point at next char in data to send
            self.charCount += 1
            # counter used to know what current packet size is
            counter = 1

            while True:
                # if the counter is 0, this means we have sent a packet and need a new one
                if counter == 0:
                    # create new segment, reset data variable for new packet, and set new seqnum
                    segmentSend = Segment()
                    data = ''
                    seqNum = self.charCount

                # add char in dataToSend at index charCount into data variable
                data += self.dataToSend[self.charCount]
                # increment charCount to set to index in dataToSend that we need to send
                # increment counter to make sure we are not going over the DATA_LENGTH limit
                self.charCount += 1
                counter += 1

                # if the counter is equal to the data length then we have to send the packet
                if counter == self.DATA_LENGTH:
                    # reset counter
                    counter = 0
                    # sets up segment with data
                    segmentSend.setData(seqNum, data)
                    # make data empty so it doesn't send again if the char count is greater than the slidingwindow[1]
                    data = ''
                    # create a copy of segment for possible resend later and keeping track of packets acks
                    copySegment = copy.deepcopy(segmentSend)
                    # start delay iteration for the copy which is used for timeout retransmits
                    copySegment.setStartDelayIteration(self.currentIteration)
                    # Display sending segment
                    print("Sending segment: ", segmentSend.to_string())
                    # Use the unreliable sendChannel to send the segment
                    self.sendChannel.send(segmentSend)
                    # store copy of segment in case we need to resend, and to keep track of acks
                    self.awaitingAckSegments.append(copySegment)

                # if we pass the sliding window's upper range then we need to send the packet and break out of loop
                if self.charCount > self.slidingWindow[1]:
                    # if the current data variable is 0 then we have just sent a packet and we need to just exit the
                    # loop. Else, we need to send the packet, it will also have a data size of less than DATA_LENGTH
                    if len(data) > 0:
                        # set up segment data
                        segmentSend.setData(seqNum, data)
                        # create deep copy of segment object
                        copySegment = copy.deepcopy(segmentSend)
                        # start delay iteration for the copy which is used for timeout retransmits
                        copySegment.setStartDelayIteration(self.currentIteration)
                        # send the segment
                        print("Sending segment: ", segmentSend.to_string())
                        self.sendChannel.send(segmentSend)
                        # store copy of segment in case we need to resend, and to keep track of acks
                        self.awaitingAckSegments.append(copySegment)
                    # exit loop which finishes this iterations sending
                    break

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        # print statments just used to see which part is doing what
        if len(self.dataToSend) == 0:
            print()
            print("###############################################################################")
            print("Server Process Receive from Reliable Layer")
            print("###############################################################################")
            print()
        else:
            print()
            print("###############################################################################")
            print("Client Process Receive from Reliable Layer")
            print("###############################################################################")
            print()

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

            # if the checksum of current segment has an error then just completely disregard it like it was being
            # dropped. If it is an ack it will be retransmitted, or if it is a data segment it will also be
            # retransmitted
            if not seg.checkChecksum():
                continue

            # if the current segment is not an ack segment then this will pertain to the server accepting data
            if seg.seqnum > -1 and len(self.dataToSend) == 0:
                # if the current packet is the packet we are looking for based on the acknum and seqnum, then we will
                # process it
                if seg.seqnum != self.ackNum:
                    # if segment is greater than the current ack number, then it is out of order and something we have
                    # not yet processed
                    if seg.seqnum > self.ackNum:
                        # if it is not then we will put it into the receiving buffer receivingListHistory to be looked
                        # at during the next iteration
                        print("Putting in receiving buffer")
                        self.receivingListHistory.append(seg)
                    else:
                        # if it is something we have already processed, this means that the ack packet was lost or
                        #  delayed so, we will just retransmit the ack segment to the client
                        segmentAck = Segment()
                        segmentAck.setAck(seg.seqnum + len(seg.payload))
                        self.sendChannel.send(segmentAck)
                        print("Re-Sending ack: ", segmentAck.to_string())
                    continue
                # if the packet is in the correct order then we print out the packet details
                seg.printToConsole()
                # add the data to our data received
                self.dataReceived += seg.payload

                segmentAck = Segment()  # Segment acknowledging packet(s) received

                # increment our ack number by the payload size
                self.ackNum += len(seg.payload)

                # Display response segment
                segmentAck.setAck(self.ackNum)
                print("Sending ack: ", segmentAck.to_string())

                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)
            # if the current segment is an ack segment then this will pertain to the client
            else:
                count = 0
                # see if the ack packet we have will ack any of the packets we have awaiting to be ack'd
                for awaitingSeg in self.awaitingAckSegments:
                    # get the size of the awaiting segments payload
                    sizeOfPayload = len(awaitingSeg.payload)
                    # if the ack number of the ack segment matches the sequence number plus the payload size of the
                    # segment that is awaiting an ack, then this ack indicates this segment was received
                    if seg.acknum == awaitingSeg.seqnum + sizeOfPayload:

                        # segLocation get the current awaitingSeg's seq number
                        segLocation = self.awaitingAckSegments[count].seqnum

                        # delete segment awaiting ack since ack was received
                        del self.awaitingAckSegments[count]

                        # checks to see if the packed that was deleted was the left most packet in the sliding window
                        # since only when this packet is ack'd we will change the sliding window to move forward
                        if segLocation == self.slidingWindow[0]:

                            # if the packet we just ack'd was the last packet then this is a special case where
                            # we move the whole sliding window by the size of the (self.FLOW_CONTROL_WIN_SIZE - 1)
                            if len(self.awaitingAckSegments) == 0:
                                # moves the lower part of the range to current self.charCount which is the variable
                                # that points to the next char we need to send
                                self.slidingWindow[0] = self.charCount
                                # if adding (self.FLOW_CONTROL_WIN_SIZE - 1) to the self.charCount would be over the
                                # length of the dataToSend then we would have errors since it would think there is more
                                # data to send, so we set the upper range to the len(self.dataToSend) - 1 if this is
                                # true, else we just increase by (self.FLOW_CONTROL_WIN_SIZE - 1)
                                if self.charCount + (self.FLOW_CONTROL_WIN_SIZE - 1) > (len(self.dataToSend) - 1):
                                    self.slidingWindow[1] = len(self.dataToSend) - 1
                                else:
                                    self.slidingWindow[1] = self.charCount + (self.FLOW_CONTROL_WIN_SIZE - 1)
                            else:
                                # else normally, if it was not the last ack, then we just need to move the range to the
                                # next lowest segment awaiting to be ack'd.
                                # upper calculates the difference between where the next segment char index is
                                # and where it the sliding window lower range is currently, this will be added to the
                                # upper range to make sure we stay withing the flow control window size
                                upper = self.awaitingAckSegments[count].seqnum - self.slidingWindow[0]
                                # set the new lower range of sliding window
                                self.slidingWindow[0] = self.awaitingAckSegments[count].seqnum
                                # if self.slidingWindow[1] + upper would be greater than the length of the data we have
                                # to send then we just set to len(self.dataToSend) - 1
                                if self.slidingWindow[1] + upper > (len(self.dataToSend) - 1):
                                    self.slidingWindow[1] = len(self.dataToSend) - 1
                                else:
                                    self.slidingWindow[1] += upper
                        # since we know that this ack segment acknowledged one of out data segments then we can break
                        break
                    # increments count
                    count += 1

    # https://www.geeksforgeeks.org/bubble-sort/ used this to just make sure my bubble sort worked correctly
    def segmentBubbleSort(self, arr):
        n = len(arr)
        swap = False
        # Traverse through all array elements
        for i in range(n - 1):
            for j in range(0, n - i - 1):
                # sorts elements by their seqnum
                if arr[j].seqnum > arr[j + 1].seqnum:
                    swap = True
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
            if not swap:
                return
