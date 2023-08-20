from commonParameter import all_parameters, set_parameter
from controller import Controller
import commonParameter
import logging
from coolStateMachine import CoolStateMachine
from pump import Pump
from fan import Fan
from sensor import Sensor
from cooler import Cooler
import threading

if __name__ == "__main__":
    for parameter_name, parameter in all_parameters.items():
        if parameter.value_type is bool:
            set_parameter(parameter.name, False)
        elif parameter.value_type is float:
            set_parameter(parameter.name, 32.0)

    # Initialize logging
    logger = logging.getLogger("General")
    logger.setLevel(logging.INFO)

    # Create a file handler
    handler = logging.FileHandler('mylog.log')

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Instantiate the devices and controller
    pump = Pump(commonParameter.ADDRESS_PUMP_CA, logger)
    fan = Fan(commonParameter.ADDRESS_FAN_CA, logger)
    sensor = Sensor(commonParameter.ADDRESS_SENSOR_CA, logger)
    cooler = Cooler(commonParameter.ADDRESS_COOLER_CA, logger)
    controller = Controller(logger, commonParameter.ADDRESS_CONTROLLER_CA)
    cool_state_machine = CoolStateMachine(logger, controller)

    def control_step():
        controller.step()

    def pump_step():
        pump.step()

    def fan_step():
        fan.step()

    def sensor_step():
        sensor.step()

    def cooler_step():
        cooler.step()

    def cool_state_machine_step():
        cool_state_machine.step()

    # Create separate threads for each device and the state machine. This approach is beneficial for CAN bus communication
    pump_thread = threading.Thread(target=pump_step)
    fan_thread = threading.Thread(target=fan_step)
    sensor_thread = threading.Thread(target=sensor_step)
    cooler_thread = threading.Thread(target=cooler_step)
    cool_state_machine_thread = threading.Thread(target=cool_state_machine_step)

    try:
        pump_thread.start()
    except Exception as e:
        logger.error("Failed to start pump thread: {}".format(e))

    try:
        fan_thread.start()
    except Exception as e:
        logger.error("Failed to start pump thread: {}".format(e))

    try:
        sensor_thread.start()
    except Exception as e:
        logger.error("Failed to start pump thread: {}".format(e))

    try:
        cooler_thread.start()
    except Exception as e:
        logger.error("Failed to start pump thread: {}".format(e))

    try:
        cool_state_machine_thread.start()
    except Exception as e:
        logger.error("Failed to start pump thread: {}".format(e))

    control_step()

    pump_thread.join()
    fan_thread.join()
    sensor_thread.join()
    cooler_thread.join()
    cool_state_machine_thread.join()
