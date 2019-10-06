#!/usr/bin/env python
"""
Author: Paulo Cezar dos Santos Filho
version: 2.0
Class name: Biprob
"""
import random
from threading import Thread
import math
import rospy
import time
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist

"""
Esta classe
"""

class Biprob:
    """
    Classe Cliente ROS para controle do Biprob no Gazebo
    """
    rospy.loginfo("Biprob")
    def __init__(self,ns="/biprob/"):
        self.ns=ns
        self.joints=None
        self.angles=None
        """
        A funcao Subscriber() diz ao ROS que deseja-se receber mensagens
        do topico /biprob/joint_states.  Com o tipo de mensagens sensor_msgs.msg.
        Esta eh uma mensagem que contem os dados que descrevem o estado de um conjunto
        de articulacoes controladas. Este procedimento invoca uma chamada para o
        no mestre ROS, que mantem um registro sobre quem eh a publicacao e quem 
        esta subscrevendo. As mensagens sao passadas para uma funcao de retorno,
        aqui chamada  _cb_joints, como argumento. O ultimo parametro para a funcao
        Subscriber() eh o tamanho da fila de mensagens. Se as mensagens estao chegando
        mais rapido do que eles estao sendo processados, entao, este eh o numero de 
        mensagens que serao bufferizadas.
        """
        self._sub_joints=rospy.Subscriber(ns+"joint_states",JointState,self._cb_joints,queue_size=1)
        rospy.loginfo("Povoando juntas...")

        while not rospy.is_shutdown():
            if self.joints is not None: break
            rospy.sleep(0.2)            
            rospy.loginfo("Povoando juntas...")
        rospy.loginfo("Juntas Povoadas")
        
        
        rospy.loginfo("Criando Editores de comando de juntas")
        self._pub_joints={}

        """
        A funcao Publisher() declara que o no esta publicando para o topico
        /biprob/joint_name_position_controller/command uma mensagem do tipo
        std_msgs.msg.Float64. 
        """
        for i in self.joints:
            publisher=rospy.Publisher(self.ns+i+"_position_controller/command",Float64)
            self._pub_joints[i]=publisher            
        
        rospy.sleep(1)
        """
        A funcao Publisher() declara que o no esta publicando para o topico
        /biprob/cmd_vel uma mensagem do tipo  geometry_msgs/Twist.msg. 
        """
        self._pub_cmd_vel=rospy.Publisher(ns+"cmd_vel",Twist) 

    #Funcoes para manipulacao das juntas
    """
    Esta funcao
    """
    def set_walk_velocity(self,x,y,t):
        msg=Twist()
        msg.linear.x=x
        msg.linear.y=y
        msg.angular.z=t
        self._pub_cmd_vel.publish(msg)
    """
    Esta funcao
    """    
    def _cb_joints(self,msg):
        if self.joints is None:
            self.joints=msg.name
        self.angles=msg.position
        
    """
    Esta funcao retorna o angula de uma junta
    """
    def get_angles(self):
        if self.joints is None: return None
        if self.angles is None: return None
        return dict(zip(self.joints,self.angles))
    """
    Esta funcao seta um angulo para a junta recebida em rad.
    """
    def set_angles(self,angles):
        for j,v in angles.items():
            if j not in self.joints:                
                rospy.logerror(j)
                continue
            self._pub_joints[j].publish(v)

