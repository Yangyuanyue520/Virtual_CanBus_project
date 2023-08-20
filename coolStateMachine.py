import commonParameter
from commonParameter import get_parameter, set_parameter
import time

"""
CoolStateMachine is a state machine used to automatically control the working state of the cooling system. State 
machines can switch between the following states:
- MANUAL: indicates the manual mode. The device does not automatically turn on or off.
- AUTO_INIT: The initial state of automatic mode, where pump and fan are turned off and the cooler is tried to start if it is not start.
- AUTO_COOLANT_ON: The cooler is started. If the temperature exceeds 32 ° C and the fan successfully starts, the cooler 
switches to the AUTO_FAN_ON state. If the temperature is lower than 30 degrees and the fan is successfully turned off, 
the fan remains in this state.
- AUTO_FAN_ON: The fan is turned on. If the pump is turned on successfully and the temperature exceeds 35 ° C, the fan 
is switched to AUTO_PUMP_ON. If the temperature is lower than 30 ° C and the fan module is turned off successfully, 
switch to the AUTO_COOLANT_ON state.
- AUTO_PUMP_ON: The pump is turned on and switched to AUTO_FAN_ON if the pump is successfully turned off at a 
temperature below 33 ° C. If the temperature is higher than 33 degrees and the pump is successfully turned on, 
the fan remains in this state.

The state machine controls each device through the controller object and gets and sets parameters through 
commonParameter.

Method introduction:
- stop_fan_and_pump: disables fan and pump. True is returned if they are disabled successfully.
- start_cooler: Turn on the cooler and return True if the cooler succeeds.
- start_fan: Enables the fan. True is returned if the fan is enabled successfully.
- stop_fan: disables the fan. True is returned if the fan is stopped successfully.
- start_pump: Starts the pump and returns True if the pump is successfully started.
- stop_pump: Disables the pump. True is returned if the pump is successfully turned off.
- temperature_above_32: Returns True if the temperature exceeds 32 degrees.
- temperature_below_30: returns True if the temperature is below 30 degrees.
- temperature_above_35: Returns True if the temperature exceeds 35 degrees.
- temperature_below_33: returns True if the temperature is below 33 degrees.
- temperature_in_range: returns True if the temperature is within a reasonable range and the sensor is in good 
condition.
- switch_to_manual_mode: Switches to the MANUAL mode.
- run_auto_mode: Runs the automatic mode and switches the status based on the temperature and device status.
- step: checks device errors. If there are no errors and the device is in automatic mode, the device runs automatic 
mode.
"""
class CoolStateMachine:
    def __init__(self, log, controller):
        self._state = "MANUAL"
        self._sensor_error = get_parameter(commonParameter.SENSOR_ERROR_STATUS_NAME)
        self._cooler_error = get_parameter(commonParameter.COOLANT_ERROR_STATUS_NAME)
        self._fan_error = get_parameter(commonParameter.FAN_ERROR_STATUS_NAME)
        self._pump_error = get_parameter(commonParameter.PUMP_ERROR_STATUS_NAME)
        self._sensor_status = get_parameter(commonParameter.SENSOR_VALUE_NAME)
        self._cooler_status = get_parameter(commonParameter.COOLANT_START_STATUS_NAME)
        self._fan_status = get_parameter(commonParameter.FAN_START_STATUS_NAME)
        self._pump_status = get_parameter(commonParameter.PUMP_START_STATUS_NAME)
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        self._log = log
        self._controller = controller
        self._pre_sensor_value = 0

    def stop_fan_and_pump(self):
        self._controller.close_device(
            commonParameter.ADDRESS_FAN_CA,
            commonParameter.FAN_CLOSE,
            commonParameter.FAN_START_STATUS_NAME,
            commonParameter.FAN_ERROR_STATUS_NAME,
        )
        self._controller.close_device(
            commonParameter.ADDRESS_PUMP_CA,
            commonParameter.PUMP_CLOSE,
            commonParameter.PUMP_START_STATUS_NAME,
            commonParameter.PUMP_ERROR_STATUS_NAME,
        )
        time.sleep(0.5)
        self._fan_status = get_parameter(commonParameter.FAN_START_STATUS_NAME)
        self._pump_status = get_parameter(commonParameter.PUMP_START_STATUS_NAME)
        if not self._fan_status and not self._pump_status:
            return True

    def start_cooler(self):
        self._controller.open_device(
            commonParameter.ADDRESS_COOLER_CA,
            commonParameter.COOLER_OPEN,
            commonParameter.COOLANT_START_STATUS_NAME,
            commonParameter.COOLANT_ERROR_STATUS_NAME,
        )
        time.sleep(0.5)
        self._cooler_status = get_parameter(commonParameter.COOLANT_START_STATUS_NAME)
        if self._cooler_status:
            return True
        else:
            return False

    def start_fan(self):
        self._controller.open_device(
            commonParameter.ADDRESS_FAN_CA,
            commonParameter.FAN_OPEN,
            commonParameter.FAN_START_STATUS_NAME,
            commonParameter.FAN_ERROR_STATUS_NAME,
        )
        time.sleep(0.5)
        self._fan_status = get_parameter(commonParameter.FAN_START_STATUS_NAME)
        if self._fan_status:
            return True
        else:
            return False

    def stop_fan(self):
        self._controller.close_device(
            commonParameter.ADDRESS_FAN_CA,
            commonParameter.FAN_CLOSE,
            commonParameter.FAN_START_STATUS_NAME,
            commonParameter.FAN_ERROR_STATUS_NAME,
        )
        time.sleep(0.5)
        self._fan_status = get_parameter(commonParameter.FAN_START_STATUS_NAME)
        if not self._fan_status:
            return True
        else:
            return False

    def start_pump(self):
        self._controller.open_device(
            commonParameter.ADDRESS_PUMP_CA,
            commonParameter.PUMP_OPEN,
            commonParameter.PUMP_START_STATUS_NAME,
            commonParameter.PUMP_ERROR_STATUS_NAME,
        )
        time.sleep(0.5)
        self._pump_status = get_parameter(commonParameter.PUMP_START_STATUS_NAME)
        if self._pump_status:
            return True
        else:
            return False

    def stop_pump(self):
        self._controller.close_device(
            commonParameter.ADDRESS_PUMP_CA,
            commonParameter.PUMP_CLOSE,
            commonParameter.PUMP_START_STATUS_NAME,
            commonParameter.PUMP_ERROR_STATUS_NAME,
        )
        time.sleep(0.5)
        self._pump_status = get_parameter(commonParameter.PUMP_START_STATUS_NAME)
        if not self._pump_status:
            return True
        else:
            return False

    # def temperature_above_32(self):
    #     self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
    #     return self._temperature >= 32

    def temperature_below_37(self):
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        return self._temperature < 37

    def temperature_above_37(self):
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        return self._temperature >= 37

    def temperature_between_33_and_37(self):
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        return 33 <= self._temperature < 37

    def temperature_below_32(self):
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        return self._temperature < 32

    def temperature_below_33(self):
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        return self._temperature < 33

    def temperature_above_33(self):
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        return self._temperature >= 33

    def temperature_in_range(self):
        self._temperature = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
        return commonParameter.TEMPER_BOT_THRESHOLD < self._temperature < commonParameter.TEMPER_TOP_THRESHOLD and self._sensor_status

    def temperature_difference_under_control(self):
        if abs(commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME) - self._pre_sensor_value) >= commonParameter.TEMPER_MAX_DIFFERENCE:
            return False
        else:
            self._pre_sensor_value = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
            return True

    def switch_to_manual_mode(self):
        self._state = "MANUAL"

    def run_auto_mode(self):
        self._log.info("State machine start")
        # Self.state.startswith ("AUTO") checks whether the value of self.state begins with "AUTO"
        while self._state.startswith("AUTO"):
            if self._state == "AUTO_INIT":
                # print is for debug, so leave it here
                # print("Now in init state")
                self._log.info("Now in init state")
                self.stop_fan_and_pump()
                if self.start_cooler():
                    # print("try to enter coolant_on")
                    self._state = "AUTO_COOLANT_ON"
                else:
                    self._state = "AUTO_INIT"

            elif self._state == "AUTO_COOLANT_ON":
                self._log.info("Now in the coolant_on state")
                # print("Now in the coolant_on state")
                if self.temperature_above_33() and self.start_fan():
                    self._state = "AUTO_FAN_ON"
                elif self.temperature_below_33():
                    self._state = "AUTO_COOLANT_ON"
                else:
                    self._state = "AUTO_INIT"

            elif self._state == "AUTO_FAN_ON":
                self._log.info("Now in the fan_on state")
                # print("Now in the fan_on state")
                if self.temperature_below_33() and self.stop_fan():
                    self._state = "AUTO_COOLANT_ON"
                elif self.temperature_above_37() and self.start_pump():
                    self._state = "AUTO_PUMP_ON"
                # miss one condition, if 30 < temp < 35 and self.start_fan(), self._state = "AUTO_FAN_ON"
                elif self.temperature_between_33_and_37():  # Add this condition
                    self._state = "AUTO_FAN_ON"
                else:
                    self._state = "AUTO_INIT"

            elif self._state == "AUTO_PUMP_ON":
                self._log.info("Now in the pump_on state")
                # print("Now in the pump_on state")
                if self.temperature_below_37() and self.stop_pump():
                    self._state = "AUTO_FAN_ON"
                # miss one
                elif self.temperature_above_37():
                    self._state = "AUTO_PUMP_ON"
                else:
                    self._state = "AUTO_INIT"

            # Exit auto mode if temperature error occurs
            if not self.temperature_in_range() or not self.temperature_difference_under_control():
                self._state = "MANUAL"
                self._log.info("Now in the manual state")
                self._log.info("State machine end")
                # print("State machine start")
                set_parameter(commonParameter.AUTO_MODE_NAME, False)

    def step(self):
        while True:
            if self._sensor_error or self._cooler_error or self._fan_error or self._pump_error:
                return
            if get_parameter(commonParameter.AUTO_MODE_NAME):
                self._pre_sensor_value = commonParameter.get_parameter(commonParameter.SENSOR_VALUE_NAME)
                # begin with init state, easy to let the state machine under control
                self._state = "AUTO_INIT"
                self.run_auto_mode()
