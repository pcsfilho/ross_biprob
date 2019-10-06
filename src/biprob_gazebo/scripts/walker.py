#!/usr/bin/env python
from threading import Thread
import rospy
import math
from biprob_gazebo.biprob import Biprob
from geometry_msgs.msg import Twist

class WJFunc:
    def __init__(self):
        self.offset=0
        self.scale=1
        self.in_offset=0
        self.in_scale=1
        
    def get(self,x):
        """ x between 0 and 1"""
        f=math.sin(self.in_offset+self.in_scale*x)
        return self.offset+self.scale*f        
        
    def clone(self):
        z=WJFunc()
        z.offset=self.offset
        z.scale=self.scale
        z.in_offset=self.in_offset
        z.in_scale=self.in_scale
        return z
    
    def mirror(self):
        z=self.clone()
        z.offset*=-1
        z.scale*=-1
        return z
        
class WFunc:
    """
    Multi-joint funcao de caminhada para o biprob    
    """
    def __init__(self,**kwargs):
        self.parameters={}
        self.parameters["swing_scale"]=0
        self.parameters["step_scale"]=0.3
        self.parameters["step_offset"]=0.55
        self.parameters["ankle_offset"]=0
        self.parameters["vx_scale"]=0.5
        self.parameters["vy_scale"]=0.5
        self.parameters["vt_scale"]=0.4        
        for k,v in kwargs.items():
            self.parameters[k]=v        
        self.generate()
        
    def generate(self):
        """
        Construir funcoes CPG para a caminhada no local (sem translacao ou rotacao, somente pes para subir/descer)
        """         
        self.pfn={} # phase joint functions    
        self.afn={} # anti phase joint functions 

        f1=WJFunc()
        f1.in_scale=math.pi
        f1.scale=-self.parameters["swing_scale"]
        self.pfn["j_front_ankle_l"]=f1
        self.pfn["j_front_hip_l"]=f1      
        
        f2=f1.mirror()  
        self.afn["j_front_ankle_l"]=f2
        self.afn["j_front_hip_l"]=f2

        f3=WJFunc()
        f3.in_scale=math.pi
        f3.scale=self.parameters["step_scale"]
        f3.offset=self.parameters["step_offset"]
        self.pfn["j_sagittal_hip_l"]=f3
        f33=f3.mirror()
        f33.offset+=self.parameters["ankle_offset"]
        self.pfn["j_sagittal_ankle_l"]=f33
        
        f4=f3.mirror()
        f4.offset*=2
        f4.scale*=2
        self.pfn["j_knee_l"]=f4
        
        s2=0
        f5=f3.clone()
        f5.in_scale*=2
        f5.scale=s2
        self.afn["j_sagittal_hip_l"]=f5        
        
        f6=f3.mirror()
        f6.in_scale*=2
        f6.scale=f5.scale
        f6.offset+=self.parameters["ankle_offset"]
        self.afn["j_sagittal_ankle_l"]=f6
        
        f7=f4.clone()
        f7.scale=0
        self.afn["j_knee_l"]=f7
        
        self.forward=[f5,f6]        
        self.generate_right()
        self.joints=self.pfn.keys()      
       
       
    def generate_right(self):
        """
        Funcao espelho CPG da esquerda para a direita e da antifase direita 
        """
        l=[ v[:-2] for v in self.pfn.keys()]
        for j in l:
            self.pfn[j+"_r"]=self.afn[j+"_l"].mirror()
            self.afn[j+"_r"]=self.pfn[j+"_l"].mirror()
        
    def get(self,phase,x,velocity):
        """ Obter os angulos das juntas para uma determinada fase, posicao em ciclo (0,1 x)) e parametros de velocidade """
        angles={}
        for j in self.pfn.keys():
            if phase:
                v=self.pfn[j].get(x)
                angles[j]=v
            else:
                angles[j]=self.afn[j].get(x)
        self.apply_velocity(angles,velocity,phase,x)
        return angles       
    
    def apply_velocity(self,angles,velocity,phase,x):
        """Modifica na caminhada no local angulos das juntas para aplicar o vetor de velocidade"""
        
        # VX
        v=velocity[0]*self.parameters["vx_scale"]
        d=(x*2-1)*v
        if phase:
            angles["j_sagittal_hip_l"]+=d
            #angles["j_sagittal_ankle_l"]+=d
            angles["j_sagittal_hip_r"]+=d
            #angles["j_sagittal_ankle_r"]+=d
        else:
            angles["j_sagittal_hip_l"]-=d
            #angles["j_sagittal_ankle_l"]-=d
            angles["j_sagittal_hip_r"]-=d
            #angles["j_sagittal_ankle_r"]-=d
        # VY
        v=velocity[1]*self.parameters["vy_scale"]
        d=(x)*v
        d2=(1-x)*v
        if v>=0:
            if phase:
                angles["j_front_hip_l"]-=d
                #angles["j_front_ankle_l"]-=d
                angles["j_front_hip_r"]+=d
                #angles["j_front_ankle_r"]+=d
            else:
                angles["j_front_hip_l"]-=d2
                #angles["j_front_ankle_l"]-=d2
                angles["j_front_hip_r"]+=d2
                #angles["j_front_ankle_r"]+=d2
        else:
            if phase:
                angles["j_front_hip_l"]+=d2
                #angles["j_front_ankle_l"]+=d2
                angles["j_front_hip_r"]-=d2
                #angles["j_front_ankle_r"]-=d2
            else:
                angles["j_front_hip_l"]+=d
                #angles["j_front_ankle_l"]+=d
                angles["j_front_hip_r"]-=d
                #angles["j_front_ankle_r"]-=d                
        # VT
        v=velocity[2]*self.parameters["vt_scale"]
        d=(x)*v
        d2=(1-x)*v

class Walker:
    """
    Classe que faz com que o biprob ande
    """
    def __init__(self,biprob):
        self.biprob=biprob
        self.running=False

        self.velocity=[0,0,0]
        self.walking=False
        self.func=WFunc()

        self.ready_pos=self.func.get(True,0,[0,0,0])        
        self._th_walk=None
        self._sub_cmd_vel=rospy.Subscriber(biprob.ns+"cmd_vel",Twist,self._cb_cmd_vel,queue_size=1)

    def _cb_cmd_vel(self,msg):
        """
        Ele captura o cmd_vel e atualiza a velocidade do biprob
        """
        vx=msg.linear.x
        vy=msg.linear.y
        vt=msg.angular.z
        self.start()
        self.set_velocity(vx,vy,vt)
    
    def start(self):
        if not self.running:
            self.running=True         
            self._th_walk=Thread(target=self._do_walk)
            self._th_walk.start()
            self.walking=True
    
    def set_velocity(self,x,y,t):
        self.velocity=[x,y,t]        

    def _do_walk(self):
        """
        Principal laco de caminhada. Atualiza os vetores de velocidade e aplica os angulos correspondentes
        """
        r=rospy.Rate(100)
        rospy.loginfo("Iniciando thread de caminhada")
        func=self.func      

        n=50
        p=True
        i=0
        self.current_velocity=[0,0,0]
        
        while not rospy.is_shutdown() and (self.walking or i<n or self.is_walking()):
            if not self.walking:
                self.velocity=[0,0,0]
            if not self.is_walking() and i==0: # Do not move if nothing to do and already at 0
                self.update_velocity(self.velocity,n)
                r.sleep()
                continue
            x=float(i)/n            
            angles=func.get(p,x,self.current_velocity)
            self.update_velocity(self.velocity,n)
            self.biprob.set_angles(angles)
            i+=1
            if i>n:
                i=0
                p=not p
            r.sleep()
        rospy.loginfo("Finalizando thread de caminhada")        
        self._th_walk=None

    def is_walking(self):
        e=0.02
        for v in self.current_velocity:
            if abs(v)>e: return True
        return False
        
    def update_velocity(self,target,n):
        a=3/float(n)
        b=1-a
        self.current_velocity=[a*t+b*v for (t,v) in zip(target,self.current_velocity)]    

if __name__=="__main__":
    rospy.init_node("walker")
    rospy.sleep(1)
    
    rospy.loginfo("Instanciando cliente Biprob")
    biprob=Biprob()
    rospy.loginfo("Instaciando classe Walker com objeto biprob")
    walker=Walker(biprob)
 
    rospy.loginfo("Biprob Walker pronto")
    while not rospy.is_shutdown():
        rospy.sleep(1)