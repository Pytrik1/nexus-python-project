#!/usr/bin/env python

import rospy
import matplotlib.pyplot as pl
import numpy as np
from rospy_tutorials.msg import Floats
from rospy.numpy_msg import numpy_msg
from geometry_msgs.msg import Twist

class controller:
    ''' The controller uses the interagent distances to determine the desired velocity of the Nexus '''
    
    def __init__(self):
        ''' Initiate self and subscribe to /z_values topic '''
        # controller variables
        self.running = np.float32(1)
        self.d = np.float32(0.8)
#        self.dd = np.float32(np.sqrt(np.square(self.d)+np.square(self.d))*1.05)        
        self.dd = np.float32(np.sqrt(np.square(self.d)+np.square(self.d)))        
        self.c = np.float32(0.5)
        self.U_old = np.array([0, 0])
        self.U_oldd = np.array([0, 0])
        self.mu_hat = np.array([[0], [0]])

        # Motion parameters
        self.x_dot = np.float32(0)
        self.y_dot = np.float32(0)
        self.r_dot = np.float32(0)
        self.mu_x = self.x_dot*np.array([0, -1, 0, -1, 0])
        self.mut_x = self.x_dot*np.array([0, 1, 0, 1, 0])
        self.mu_y = self.y_dot*np.array([-1, 0, 0, 0, 1])
        self.mut_y = self.y_dot*np.array([1, 0, 0, 0, -1])
        self.mu_r = self.r_dot*np.array([-1, -1, 0, 1, -1])
        self.mut_r = self.r_dot*np.array([1, 1, 0, -1, 1])

        self.mu = self.mu_x+self.mu_y+self.mu_r
        self.mut = self.mut_x+self.mut_y+self.mut_r        
        
        # prepare Log arrays
        self.E1_log = np.array([])
        self.E2_log = np.array([])
        self.E3_log = np.array([])
        self.mu_hat2_log = np.array([])
        self.mu_hat3_log = np.array([])
        self.DT_log = np.array([])
        self.Un = np.float32([])
        self.U_log = np.array([])
        self.time = np.float64([])
        self.time_log = np.array([])
        self.now = np.float64([rospy.get_time()])
        self.old = np.float64([rospy.get_time()])
        self.begin = np.float64([rospy.get_time()])
        self.k = 0

        # prepare shutdown
        rospy.on_shutdown(self.shutdown)
        
        # prepare publisher
        self.pub = rospy.Publisher('/nexus2/cmd_vel', Twist, queue_size=1)
        self.velocity = Twist()
                
        # subscribe to z_values topic
        rospy.Subscriber('/nexus2/z_values', numpy_msg(Floats), self.controller)
        
        # subscribe to controller_variables
        rospy.Subscriber('/controller_variables', numpy_msg(Floats), self.update_controller_variables)
        
    def update_controller_variables(self, data):
        ''' Update controller variables '''
        if self.running < 10:
            # Assign data 
            self.controller_variables = data.data

            # Safe variables
            self.running = np.float32(self.controller_variables[0])
            self.d = np.float32(self.controller_variables[1])
#            self.dd = np.float32(self.controller_variables[2]*1.05)
            self.dd = np.float32(self.controller_variables[2])
            self.c = np.float32(self.controller_variables[3])
            self.x_dot = np.float32(self.controller_variables[4])
            self.y_dot = np.float32(self.controller_variables[5])
            self.r_dot = np.float32(self.controller_variables[6])
            
            # Calculate mu
            self.mu_x = self.x_dot*np.array([0, -1, 0, -1, 0])
            self.mut_x = self.x_dot*np.array([0, 1, 0, 1, 0])
            self.mu_y = self.y_dot*np.array([-1, 0, 0, 0, 1])
            self.mut_y = self.y_dot*np.array([1, 0, 0, 0, -1])
            self.mu_r = self.r_dot*np.array([-1, -1, 0, 1, -1])
            self.mut_r = self.r_dot*np.array([1, 1, 0, -1, 1])
            
            self.mu = self.mu_x+self.mu_y+self.mu_r
            self.mut = self.mut_x+self.mut_y+self.mut_r        
        
    def controller(self, data):
        ''' Calculate U based on z_values '''    
        if self.running < 10:
            # Input for controller
            self.z_values= data.data
            
            # Formation shape control
            self.BbDz = np.array([[self.z_values[1], self.z_values[4], self.z_values[7]], \
                                  [self.z_values[2], self.z_values[5], self.z_values[8]]])
            self.Dzt = np.array([[(self.z_values[0])**(-1), 0, 0], \
                                 [0, (self.z_values[3])**(-1), 0], \
                                 [0, 0, (self.z_values[6])**(-1)]])
            self.Ed = np.array([[self.z_values[0]-self.d], \
                                [self.z_values[3]-self.d], \
                                [self.z_values[6]-self.dd]])

            # Estimator
            self.now = np.float64([rospy.get_time()])
            self.DT = self.now-self.old
            mu_hat_dot = 2*(np.array([self.Ed[0]- self.mu_hat[0], self.Ed[2]- self.mu_hat[1]]))
            self.mu_hat = self.mu_hat + mu_hat_dot * self.DT
            self.S1bDz = np.array([[self.z_values[1]/self.z_values[0], self.z_values[7]/self.z_values[6]], \
                                   [self.z_values[2]/self.z_values[0], self.z_values[8]/self.z_values[6]]])

#            self.S1bDz = np.array([[self.z_values[1]/self.z_values[0], 0], \
#                                   [self.z_values[2]/self.z_values[0], 0], \
#                                   [0, self.z_values[7]/self.z_values[6]], \
#                                   [0, self.z_values[8]/self.z_values[6]]])

#            print 'mu_hat2_3= \n', self.mu_hat
#            print 's1bDz_2= \n', self.S1bDz
#            print 'mu_hat2_3 * s1bDz_2= \n', self.S1bDz.dot(self.mu_hat)

#            print "2estimator: ", self.S1bDz, #"\n \n", self.mu_hat
#            print self.mu_hat[0]
#            aux = self.S1bDz.dot(self.mu_hat)
#            aux_2 = aux[0:1] + aux[2:3]
#            print 'aux_2 = \n', aux_2
            
            # Formation motion control
            self.Ab = np.array([[self.mut[0], 0, self.mu[1], 0], \
                                [0, self.mut[0], 0, self.mu[1]]])
            self.z = np.array([self.z_values[4], self.z_values[5], self.z_values[1], self.z_values[2]])

            # Control law
            self.U = self.c*self.BbDz.dot(self.Dzt).dot(self.Ed) + (self.Ab.dot(self.z)).reshape((2, 1)) \
            - 0.5*self.S1bDz.dot(self.mu_hat)


            # Saturation
            for i in range(len(self.U)):          
                if self.U[i] > 0.5:
                    self.U[i] = 0.5
                elif self.U[i] < -0.5:
                    self.U[i] = -0.5
#                elif -0.02 < self.U[i]+self.U_old[i]+self.U_oldd[i] < 0.02 : # preventing shaking 
#                    self.U[i] = 0
            
            # Set old U values for moving average in order to prevent shaking
            self.U_oldd = self.U_old
            self.U_old = self.U

            # Append error and velocity in Log arrays
            self.E1_log = np.append(self.E1_log, self.Ed[1])
            self.E2_log = np.append(self.E2_log, self.Ed[0])
            self.E3_log = np.append(self.E3_log, self.Ed[2])
            self.mu_hat2_log = np.append(self.mu_hat2_log, self.mu_hat[0])
            self.mu_hat3_log = np.append(self.mu_hat3_log, self.mu_hat[1])
            self.Un = np.float32([np.sqrt(np.square(self.U[0])+np.square(self.U[1]))])
            self.U_log = np.append(self.U_log, self.Un)
            
            # Save current time in time log array
            if self.k < 1:
                self.begin = np.float64([rospy.get_time()])
                self.k = 10
#            self.now = np.float64([rospy.get_time()])
            self.old = self.now
            self.time = np.float64([self.now-self.begin])
            self.time_log = np.append(self.time_log, self.time)
            self.DT_log = np.append(self.DT_log, self.DT)

            # publish
            self.publish_control_inputs()

        elif 10 < self.running < 1000:
            self.shutdown()

    def publish_control_inputs(self):
        ''' Publish the control inputs to command velocities '''
        self.velocity.linear.x = self.U[0]
        self.velocity.linear.y = self.U[1]
#        rospy.loginfo(self.velocity)
         
        self.pub.publish(self.velocity)

    def shutdown(self):
        ''' Stop the robot when shutting down the controller_2 node '''
        rospy.loginfo("Stopping Nexus_2...")
        self.running = np.float32(10000)
        self.velocity = Twist()
        self.pub.publish(self.velocity)
        DT_average = np.mean(self.DT_log)
        print 'DT_nx2 =', DT_average

        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/E1_log_nx2', self.E1_log)
        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/E2_log_nx2', self.E2_log)
        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/E3_log_nx2', self.E3_log)
        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/U_log_nx2', self.U_log)
        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/time_log_nx2', self.time_log)
        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/mu_hat2_log_nx2', self.mu_hat2_log)
        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/mu_hat3_log_nx2', self.mu_hat3_log)
        np.save('/home/s2036975/Documents/Master Thesis/experiments/experiment_x/DT_log_nx2', self.DT_log)

#        pl.close("all")       
        pl.figure(2)
        pl.title("Inter-agent distance error measured by Nexus 2")
        pl.plot(self.time_log, self.E1_log, label="e1_nx2", color='b')
        pl.plot(self.time_log, self.E2_log, label="e2_nx2", color='g')
        pl.plot(self.time_log, self.E3_log, label="e3_nx2", color='r')
        pl.xlabel("Time [s]")
        pl.ylabel("Error [m]")
        pl.grid()
        pl.legend()
        
        pl.figure(3)
        pl.title("Input velocity Nexus 2 ")
        pl.plot(self.time_log, self.U_log, label="pdot_nx2", color='g')
        pl.xlabel("Time [s]")
        pl.ylabel("Velocity [m/s]")
        pl.grid()
#        pl.legend()
        
        pl.figure(9)
        pl.title("Mu_hat 2 and 3 estimated by Nexus 2")
        pl.plot(self.time_log, self.mu_hat2_log, label="mu_hat2_nx2", color='g')
        pl.plot(self.time_log, self.mu_hat3_log, label="mu_hat3_nx2", color='r')
        pl.xlabel("Time [s]")
        pl.ylabel("Error [m]")
        pl.grid()
        pl.legend()

        pl.figure(12)
        pl.title("DT Nexus 2")
        pl.plot(self.time_log, self.DT_log, label="DT_nx2", color='y')
        pl.xlabel("Time [s]")
        pl.ylabel("DT [s]")
        pl.grid()
        pl.legend()
                
        pl.pause(0)
        
        rospy.sleep(1)


if __name__ == '__main__':
    try:
        rospy.init_node('controller_2', anonymous=False)
        controller()
        rospy.spin()
    except:
        rospy.loginfo("Controller node terminated.")  

# 3 neighbours:
##            self.BbDz = np.array([[self.z_values[1], self.z_values[4], self.z_values[7]], \
##                                  [self.z_values[2], self.z_values[5], self.z_values[8]]])
##            self.Dzt = np.array([[(self.z_values[0])**(-1), 0, 0], \
##                                 [0, (self.z_values[3])**(-1), 0], \
##                                 [0, 0, (self.z_values[6])**(-1)]])
##            self.Ed = np.array([[self.z_values[0]-self.d], \
##                                [self.z_values[3]-self.d], \
##                                [self.z_values[6]-self.dd]])
##            self.U = self.c*self.BbDz.dot(self.Dzt).dot(self.Ed)

# 2 neighbours
##            self.BbDz = np.array([[self.z_values[1], self.z_values[4]], \
##                                  [self.z_values[2], self.z_values[5]]])
##            self.Dzt = np.array([[(self.z_values[0])**(-1), 0], \
##                                 [0, (self.z_values[3])**(-1)]])
##            self.Ed = np.array([[self.z_values[0]-self.d], \
##                                [self.z_values[3]-self.d]])
##            self.U = self.c*self.BbDz.dot(self.Dzt).dot(self.Ed)
