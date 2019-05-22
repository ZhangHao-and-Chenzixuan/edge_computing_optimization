import gym
import os
import sys
import random
import queue


class  Node():
    def __init__(self, nid, v1, task, data_num):
        """
        :param id: the id of this node
        :param v1: the speed of processing data
        :param task: the amount of calculation of this Node, i.e. the float calculation of each data
        :param data_num: the amount of data inthe queue at start, default float32 type
        """
        self.id = nid
        self.state = 0 # 0: free     1: forwading     2: waiting for back       3: backwarding
        self.process_speed = v1
        self.task = task # task volume of process one single data. Volume for batch needs to be calculated
        self.queue = queue.Queue()
        self.left_time = 0
        for i in range(data_num):
            self.queue.put(1)  # put data size in the queue, for batch, size >= 1, for a single data, size = 1

    """
    work: recieve forward sinal----->startProcess------>forward------->recieve backward signal------->backward------->endProcess
    """
    
    def startForward(self, num):
        """
        In this function, the node will fetch a data from queue, process it and send it to 
        another node as soon as the process finished
        :param num: the number of data in this batch, num <= max num
        """
        for i in range(num):
            data_size = self.queue.get()
            self.pkg_size += data_size # calculate the size of batch(package)
        # print("Node %d start to process data")
        self.state = 1
        
        t = (self.task -  1) //self.process_speed + 1  # TODO: time for batch with self.pkg_size
        self.left_time = t
        size = forward_backward()
        return size

    def startBackward(self):
        self.state = 3
        t = (self.task -  1) //self.process_speed + 1  # TODO: time for batch with self.pkg_size
        self.left_time = t
        size = forward_backward()
        return size

    def forward_backward(self):
        if self.left_time == 0:
            if self.state == 1:
                self.state = 2
                return self.pkg_size
            else:
                self.state = 0
                return (0 - self.pkg_size)  # Positive: forward return; Negative: backward return; 0: still working
        else:
            self.left_time -= 1
            return 0



class Channel():
    def __init__(self, v, ne, nc):
        self.velocity = v
        self.state = 0    # state: 0: free  1: transferring
        # these two nodes seem useless, might can be deleted -----
        self.edge_node = ne
        self.cent_node = nc
        #---------------------------------------------------------

    """
    work: recieve start signal------>startSendData------>send------->endSendData
    """
    
    def startSendData(self, data_size, to_center):
        """
        :param data_size: how many data in one batch, integer
        :param to_center: if this package is sent to center, boolean
        """
        t = (data_size - 1) // self.velocity + 1
        self.pkg_size = data_size
        self.state = 1
        self.left_time = t
        size = send()
        self.to_center = to_center
        return t

    def send(self):
        if self.left_time == 0:
            self.state = 0 # endSendData
            if self.to_center:
                return self.pkg_size
            else:
                return (0 - self.pkg_size)
        else:
            self.left_time -= 1
            return 0



class networkEnv_v0(gym.Env):
    def __init__(self):
        self.edgeNode1 = Node(0, 1, 0, 100)
        self.edgeNode2 = Node(1, 1, 0, 100)
        self.centerNode = Node(2, 10, 100, 0)
        self.action_space = range(0, 25)
        """
               edge1  0  1  2  3  4
        edge2
        0             0  1  2  3  4
        1             5  6  7  8  9
        2             10 11 12 13 14
        3             15 16 17 18 19
        4             20 21 22 23 24
        
        """

    def render(self):
        # TODO: draw the network figure

    def step(self, action):
        edge1_size = None
        edge2_size = None
        cent_size = None
        
        # State transfer: Node     0 ----> 1
        if action % 5 != 0 and self.edgeNode1.state == 0:
            edge1_size = self.edgeNode1.startForward(action % 5)
        else:
            pass
                #state != 0 means backwarding is not finished yet, no action can apply
        if action < 5 and self.edgeNode2.state == 0:
            edge2_size  = self.edgeNode2.startForward(action // 5)
        else:
            pass
        if self.centerNode.state == 0 and not self.centerNode.queue.empty():
            cent_size = self.centerNode.startForward(1)
        else:
            pass
        



