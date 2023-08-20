#   Mock Cooling Schematic system

##  summary

This is a small project writen by Shuyang Jiang

**Current Version:** 0.0.1
**Last Updated:** July 23, 2023

## Project overview
This topic is to simulate a cooling schematic system. It uses Python programs to simulate the operation of different components of the cooling system, including sensor, coolant, fan, pump, and controller. The controller acts as the master, managing the operation of the slave equipment (sensor, coolant, fan, and pump) based on the data received from the sensor.

Here's how each component works:

Sensor: The sensor generates an analog temperature value and sends it to the controller. It also records and plots changes in sensor state, cooler state, fan state, and pump state over time in auto mode.

Coolant: The coolant assembly receives commands from the controller to start or stop the coolant. 

Fan: Similarly, the fan receives commands from the controller to start or stop the fan and reports the status of the fan.

Pump: The pump also receives commands from the controller to start or stop the pump and reports its status.

Controller: Manages the operations of other devices. It receives temperature data from sensors and decides whether to turn on or off coolant, fans and pumps based on the received temperature. If the temperature exceeds a certain threshold, the coolant, fan, and pump are started, and if the temperature is below a certain threshold, the coolant, fan, and pump are stopped. In the auto state, manages the operations of other devices through a [state machine] 

Communication between the controller and other devices is carried out via the virtual CAN bus.

The goal of the project is to demonstrate a model of a cooling schematic system that provides insights into how different components interact and respond to changing temperature conditions.


## Environment Configuration
This project runs on a Linux-based operating system and simulates CAN communication using virtual CAN (vcan). The Python programming language is used with the specific version being Python 3.8. The project also requires the installation of specific Python libraries: python-can==4.2.2 and matplotlib==3.7.2.
1. set up virtual can
```shell script
    sudo modprobe vcan # Load the vcan module
    sudo ip link add dev vcan0 type vcan # Create a vcan network interface
    sudo ip link set up vcan0 # Activate the vcan network interface
```
after setting this, then can use
```shell script
    candump
```
to monitor the message on vcan
2. install the necessary Python libraries, they are listed in the `requirements.txt` file. can install them by running 
```shell script
    pip install -r requirements.txt
```

## project structure
1. commonParameter: Is a global object used to share and manage parameters across classes and functions. It has methods to get and set parameter values.

2. Device: This is a parent class that defines the basic functionality that all devices need to implement. This includes starting the device, stopping the device, and checking the device status.

3. Sensor: This is a subclass that inherits from the Device class and has some specific functions, such as sending simulated values and generating report graphs. It also maintains logs that record information such as temperature, sensor status, cooler status, fan status, and pump status.

4. CoolStateMachine: This class is used to manage the state machine of the cooling process(Auto mode)

5. Controller: The controller is the class responsible for coordinating the various devices

6. Log: There is mylog.log in the project directory. Logging is used in the project to record key operations and information. This can help me understand how my program is performing and provide useful debugging information when problems arise.

7. Plot: The Sensor class has a function for generating report graphs. Help me test the state machine

8. Multithreading: the program uses multiple threads. Each device (pump, fan, sensor, and cooler) runs in its own thread. In this way, individual devices can work on tasks in parallel without waiting for other devices to complete their tasks.

9. Can_service: Try to write a can service to manage can behaviour, but not finish, so leave it here.

## project operation
1. start the project
Go to the current project folder and execute
```
python main.py
```
2. system operate
Enter the following command on the console
under manual mode:
```
cooler open： open coolant 
cooler close: close coolant
fan open: open fan
fan close: close fan
pump open: open pump
pump close: close pump
auto: switch to auto state
```
when switch into auto mode, the state machine will automatically run, in order to test, I don't let it fail, so can't go back to manual mode, When the timer reaches 30, a png file is generated in the project folder, showing the status values of all devices during this time 

## Key function introduction
### state machine
1. Two Main Modes: The system operates in two primary modes, Automatic and Manual. 

2. Automatic Mode: This mode is further divided into four sub-states: 

3. Init State: This is the default state when none of the conditions for the other states are met. In this state, all motors are turned off, and the system attempts to start the coolant. If the coolant startup is successful, it transitions to the second state. 

4. Coolant_On State: There are two conditions that lead to this state. The first is if the system is in the Init state and the coolant startup is successful. The second is if the system is in the Fan_On state and the temperature drops below 30 degrees Celsius, causing the fan to turn off. If the temperature rises above 32 degrees Celsius and the fan successfully turns on, the system transitions to the Pump_On state. If the fan fails to start, the system transitions back to the Init state. 

5. Fan_On State: There are two conditions that lead to this state. The first is if the system is in the Coolant_On state and the temperature rises above 32 degrees Celsius, causing the fan to turn on successfully. The second is if the system is in the Pump_On state and the temperature drops below 33 degrees Celsius, causing the pump to turn off successfully. If the temperature drops below 30 degrees Celsius, the fan is turned off and the system transitions to the Coolant_On state if successful. If the temperature rises above 35 degrees Celsius, the pump is turned on, and the system transitions to the Pump_On state if successful. If either operation fails, the system transitions back to the Init state. 

6. Pump_On State: This state is entered from the Fan_On state when the temperature rises above 35 degrees Celsius and the pump turns on successfully. If the temperature drops below 33 degrees Celsius and the pump turns off successfully, the system transitions back to the Fan_On state. If the pump fails to turn off, the system transitions back to the Init state. 

7. In any state, if the temperature sensor reports an error or the temperature exceeds or drops below specified thresholds, the system transitions to Manual Mode.

### device state check
The status-checking process in my system involves continuous communication from the controller to each device. Upon receiving a status-check request, each device is required to respond with appropriate information indicating its current status. 

The controller keeps track of the time it last received a response from each device. If a significant amount of time elapses without a response from a device, the controller concludes that the device is not operating correctly. 

This continuous monitoring and time-based assessment provides a way for the system to automatically detect and respond to potential device failures, increasing its reliability and robustness. 

In my particular system, all the message exchanges between the controller and the devices are simulated and are designed to always succeed.

### sensor monitor data
Send simulated values: The Sensor class is capable of sending simulated temperature values to the CAN bus, which are randomly generated in automatic mode and range from 29 to 42 degrees. If the system is in non-automatic mode, a fixed message is sent. After 30 simulated temperature values are sent in automatic mode, an image is generated and the temperature values are reset.

Generate picture: After 30 simulated temperature values have been sent, this method is called to generate a picture showing the various status logs and temperature logs.

## Project difficulty
Virtual CAN (vCAN) and python-can library: One of the significant challenges I encountered was implementing virtual communication using vCAN. I initially attempted to create a CAN service to manage the sending and receiving of messages functions, which I imported from the python-can library. For reasons unknown to me, this didn't work, which resulted in me being stuck for an extended period. However, when I attempted to import these functions directly from the library, it seemed to work fine. This experience highlighted an area for further exploration. Another issue I ran into was that the data wasn't persistent. After much investigation, I realized that implementing multithreading could solve this problem. 

Multithreading: To be honest, this is the first time I touch this area

State Machines: Although I had encountered state machines during my internship, my involvement had been minimal, mainly involving minor modifications such as adding a state to an existing machine. This project, however, required me to construct a state machine from scratch, which was a first for me. Despite the relatively simple functionalities, it was challenging since it was an entirely new experience. The state diagram I later created with matplotlib for testing purposes seemed to suggest that the functions were operating normally. 

## Project Limitations and Future Goals: 

1. Multithreading: At present, I have individually assigned a separate thread to each device for its operation, without any systematic management. This has resulted in slow communication speed. Unfortunately, I lack experience in multithreading programming and will need to further educate myself in this area. 

2. Unit Test: I should have added function tests, but the time constraints were pressing. I began writing the project code on Friday night (as I was working at the company during the day on Thursday and Friday, and spent the evenings researching how to draw diagrams, which was quite a challenge for me), and I've spent more than 20 hours to code. I plan to submit it by Sunday night. 

3. Language choice: I understand that communication projects like this are typically written in C or C++. However, due to my extensive experience writing Python code at my current company and lack of hands-on experience writing C, I chose Python for the sake of time efficiency. I would, however, love the opportunity to write in C or C++ in the future. 

4. Functional limitations: This project was designed for testing purposes, and as a result, many functions were not considered. For example, motor error handling should include retry mechanisms, and the temperature values were not processed or handled, merely passed along. Issues such as value fluctuation and confidence were also not considered. 

5. Use of Libraries: While Python offers a plethora of convenient libraries, they can sometimes bring unexpected issues. This was my first time using the python-can library and I encountered significant problems during its use. This will require further investigation in the future.

6. Mode Switching: Currently, I am unable to manually switch from auto mode to manual mode. This only occurs when the thermometer malfunctions. It appears that while the state machine is running, I am unable to operate the console, which might be related to multithreading. This warrants further investigation.

7. Logs should be classified, but for time reasons, I only have a general log

8. Add UI, but not this time

9. Since I didn't install Git on my personal computer (as I usually use my work computer for development), I didn't employ Git for version control. This made it difficult to retrospectively review my own code, particularly during the initial stages of debugging the send and receive messages on the CAN bus. The process was quite challenging as the messages would occasionally transmit successfully and other times not.

10. 

## Project summary
This project has been a highly enlightening experience for me. It has allowed me to gain valuable insights into CAN Bus communication programming, the creation of state machines, and simulating data for testing through graphical representation.
