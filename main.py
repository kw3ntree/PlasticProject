from evdev import InputDevice, categorize, ecodes
from multiprocessing import Process
import multiprocessing
import time
from datetime import datetime
import csv
import serial
from datetime import datetime


import RPi.GPIO as GPIO
from time import sleep

class StepperHandler():

    __CLOCKWISE = 1
    __ANTI_CLOCKWISE = 0

    def __init__(self, stepPin, directionPin, delay=0.208, stepsPerRevolution=200):

        self.CLOCKWISE = self.__CLOCKWISE
        self.ANTI_CLOCKWISE = self.__ANTI_CLOCKWISE
        self.StepPin = stepPin
        self.DirectionPin = directionPin
        self.Delay = delay
        self.RevolutionSteps = stepsPerRevolution
        self.CurrentDirection = self.CLOCKWISE
        

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.StepPin, GPIO.OUT)
        GPIO.setup(self.DirectionPin, GPIO.OUT)

    def Step(stepPin, stepsToTake, directionPin, direction = __CLOCKWISE, delay=0.0025):

        print("Step Pin: " + str(stepPin) + " Direction Pin: " + str(directionPin) + " Delay: " + str(delay))
        print("Taking " + str(stepsToTake) + " steps.")

        # Set the direction
        GPIO.output(directionPin, direction)
        CurrentStep = 0
        # Take requested number of steps
        for x in range(stepsToTake):
            print("Step " + str(x))
            GPIO.output(stepPin, GPIO.HIGH)
            CurrentStep += 1
            sleep(delay)
            GPIO.output(stepPin, GPIO.LOW)
            sleep(delay)

class sensorProcess ():

    def readStream():
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.reset_input_buffer()
        

        raw_line = ser.readline().decode('utf-8').rstrip()
        print(raw_line) #debugging
        return raw_line
        

    def saveData(data):
        f = open('analyze.csv','w', newline='\n')
        wr = csv.writer(f)
        wr.writerow(data)
        
        f.close()

    def detection(list):
        phase1 = float(list[0])
        phase2 = float(list[1])

        if(phase1 > 500 and phase2 > 500):
            setServoPos("PP")
            print("pp 입니다.")
        else:
            setServoPos("PE")
            print("PE 입니다.")

def setServoPos(state):
    servoPin1 = 12   
    servoPin2 = 17   
    
    SERVO_MAX_DUTY    = 12  
    SERVO_MIN_DUTY    = 3   
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPin1, GPIO.OUT) 
    GPIO.setup(servoPin2, GPIO.OUT) 

    servo1 = GPIO.PWM(servoPin1, 50)  
    servo2 = GPIO.PWM(servoPin2, 50) 
    
    servo1.start(0)  
    servo2.start(0)  
    
    degree1 = 0
    degree2 = 0

    if(state == "PP"):
        degree1 = 180
        degree2 = 0
    elif(state == "PE"):
        degree1 = 0
        degree2 = 180
  
    duty1 = SERVO_MIN_DUTY+(degree1*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
    duty2 = SERVO_MIN_DUTY+(degree2*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
  
    print("Degree1: {} to {}(Duty1)".format(degree1, duty1))
    print("Degree2: {} to {}(Duty2)".format(degree2, duty2))

  
    servo1.ChangeDutyCycle(duty1)
    servo2.ChangeDutyCycle(duty2)



def sub_stream(r_dict):
    print("starting sub_stream")
    sensorProcess = sensorProcess()
    raw_line = sensorProcess.readStream()
        #stepperHandler.Step(200, stepperHandler.ANTI_CLOCKWISE)
    if(raw_line != ""):
        if(raw_line[0] == "@" and raw_line[1:] == "stop" and state == 0):
            p1.kill()
            print("phase1 started")
            while(True):
                raw_line = sensorProcess.readStream()
                time.sleep(0.1)
                #print(raw_line)#debugging
                if(raw_line != ""):
                    if(raw_line[0] == "@" and raw_line[1:] == "start"):
                        r_dict[0] = 0
                        p1.start()
                        print("phase1 finished")
                        state = 1
                        break
        
        elif(raw_line[0] == "@" and raw_line[1:] == "stop" and state == 1):
            p1.kill()
            print("phase2 started")
            while(True):
                raw_line = sensorProcess.readStream()
                time.sleep(0.1)
                #print(raw_line)#debugging
                if(raw_line != ""):
                    if(raw_line[0] == "@" and raw_line[1:] == "start"):
                        print(raw_line)#debugging
                        while(True):
                            raw_line = sensorProcess.readStream()
                            time.sleep(0.1)
                            if(raw_line != ""):
                                if(raw_line[0] =="@"):
                                    r_dict[0] = 0
                                    p1.start()
                        
                                    print("phase2 finished")
                                    pre = raw_line[1:].split('/')
                                    pre.append(datetime.now())
                                    sensorProcess.saveData(pre)#전송받은 기록용 데이터, csv로 저장
                                    discrimination = raw_line[1:].split('/')
                                    sensorProcess.detection(discrimination)
                                    state = 0
                                        
                                    break
                        break
def main_stream():
    print("starting main_stream")
    print("status : ", status[0])
    
    STEP_PIN = 16
    DIRECTION_PIN = 21
    stepperHandler = StepperHandler(STEP_PIN, DIRECTION_PIN, 0.0025)
    
    while True :
        stepperHandler.Step(STEP_PIN,200,DIRECTION_PIN) #1 rotation

        

def runInParallel(main, sub, r_dict):    
    global p1;
    global status;
    
    status = r_dict.values()
    print("status : ", status[0])
    if(status[0] == 1):
        p1 = Process(target=main)
        p1.start()
        #p1.join()

    p2 = Process(target=sub, args = (r_dict))
    p2.start()
    #p2.join()
    

    
manager = multiprocessing.Manager()
return_dict = manager.dict()

while True:
    runInParallel(main_stream, sub_stream(return_dict), return_dict)
    

