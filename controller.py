import commonParameter
from commonParameter import set_parameter, get_parameter
import time
from datetime import datetime, timedelta
import can
import threading
import matplotlib.pyplot as plt


# Create a list where each tuple contains a device's CAN address and a command to check or request a device status value.
# This list will be used to periodically check the status of the device and get the current value of the device.
check_information = [
    (commonParameter.ADDRESS_PUMP_CA, commonParameter.PUMP_STATE_OK),
    (commonParameter.ADDRESS_COOLER_CA, commonParameter.COOLER_STATE_OK),
    (commonParameter.ADDRESS_FAN_CA, commonParameter.FAN_STATE_OK),
    (commonParameter.ADDRESS_SENSOR_CA, commonParameter.SENSOR_STATE_OK),
    (commonParameter.ADDRESS_SENSOR_CA, commonParameter.SENSOR_VALUE_REQUEST)
]


class Controller:
    def __init__(self, log, can_address):
        self._log = log
        self._can_address = can_address
        self._can_bus = can.interface.Bus('vcan0', bustype='socketcan')
        self.last_received_time = {}
        self._test_temperature_log = []
        self._test_sensor_status_log = []
        self._test_cooler_status_log = []
        self._test_fan_status_log = []
        self._test_pump_status_log = []
        self._timestamp_log = []
        self._index = 0
        self._start_time = datetime.now()
        self._pre_temp_value = 35

    def controller_send(self, can_id, data):
        try:
            message = can.Message(arbitration_id=can_id, data=data)
            self._can_bus.send(message)
        except Exception as e:
            self._log.error(f"Failed to send CAN message: {str(e)}")
            raise

    def communicate_to_device(self, can_id):
        # self.start_check(can_id, check_message)

        # initialize the time
        if can_id not in self.last_received_time:
            self.last_received_time[can_id] = datetime.now()

        time.sleep(1)
        message = self._can_bus.recv(5)
        # handle sensor message
        if message is not None and message.arbitration_id == commonParameter.ADDRESS_CONTROLLER_CA and get_parameter(commonParameter.AUTO_MODE_NAME):
            if self._index != 30:
                set_parameter(commonParameter.SENSOR_VALUE_NAME, float(message.data[0]))
                self._index += 1
                self._sensor_status = get_parameter(commonParameter.SENSOR_VALUE_NAME)
                self._cooler_status = get_parameter(commonParameter.COOLANT_START_STATUS_NAME)
                self._fan_status = get_parameter(commonParameter.FAN_START_STATUS_NAME)
                self._pump_status = get_parameter(commonParameter.PUMP_START_STATUS_NAME)
                self._test_temperature_log.append(float(message.data[0]))
                self._test_sensor_status_log.append(self._sensor_status)
                self._test_cooler_status_log.append(self._cooler_status)
                self._test_fan_status_log.append(self._fan_status)
                self._test_pump_status_log.append(self._pump_status)
                self._timestamp_log.append(datetime.now())
                if datetime.now() - self._start_time > timedelta(minutes=10):
                    self._test_temperature_log = []
                    self._test_sensor_status_log = []
                    self._test_cooler_status_log = []
                    self._test_fan_status_log = []
                    self._test_pump_status_log = []
                    self._timestamp_log = []
                    self._start_time = datetime.now()  # reset the start time
                    self._index = 0
                    print(f"after 10 minutes need to clean mock data in case of memory broken")
            else:
                self.generate_picture()
                self._index = 0
            print(
                f"mock_temperature_number: {self._index}, when it arrives at 30, will generate a log picture a log analysis picture in fold")

        # update the check time
        if message is not None and message.arbitration_id == commonParameter.ADDRESS_PUMP_CA and message.data[0] == commonParameter.PUMP_STATE_IS_OK:
            self.last_received_time[commonParameter.ADDRESS_PUMP_CA] = datetime.now()
        elif message is not None and message.arbitration_id == commonParameter.ADDRESS_COOLER_CA and message.data[0] == commonParameter.COOLER_STATE_IS_OK:
            self.last_received_time[commonParameter.ADDRESS_COOLER_CA] = datetime.now()
        elif message is not None and message.arbitration_id == commonParameter.ADDRESS_FAN_CA and message.data[0] == commonParameter.FAN_STATE_IS_OK:
            self.last_received_time[commonParameter.ADDRESS_FAN_CA] = datetime.now()
        elif message is not None and message.arbitration_id == commonParameter.ADDRESS_SENSOR_CA and message.data[0] == commonParameter.SENSOR_STATE_IS_OK:
            self.last_received_time[commonParameter.ADDRESS_SENSOR_CA] = datetime.now()
        else:
            # compare the interval to check the each device's state, now for test, I set the interval very long
            if (datetime.now() - self.last_received_time[can_id]) > timedelta(seconds=60):
                self._log.info("Last received time: %s, current time: %s", self.last_received_time[can_id], datetime.now())
                self._log.error("Device check failed for device with CAN ID: %s", can_id)
                if can_id == commonParameter.ADDRESS_PUMP_CA:
                    set_parameter(commonParameter.PUMP_ERROR_STATUS_NAME, True)
                elif can_id == commonParameter.ADDRESS_COOLER_CA:
                    set_parameter(commonParameter.COOLANT_ERROR_STATUS_NAME, True)
                elif can_id == commonParameter.ADDRESS_FAN_CA:
                    set_parameter(commonParameter.FAN_ERROR_STATUS_NAME, True)
                elif can_id == commonParameter.ADDRESS_SENSOR_CA:
                    set_parameter(commonParameter.SENSOR_ERROR_STATUS_NAME, True)

    # used to open cooler, fan and pump
    def open_device(self, device_address, open_command, start_status_name, error_status_name):
        if not get_parameter(error_status_name):
            if not get_parameter(start_status_name):
                self.controller_send(device_address, [open_command])
                set_parameter(start_status_name, True)
            else:
                if not get_parameter(commonParameter.AUTO_MODE_NAME):
                    print(f"The device with address {device_address} is already started")
                self._log.info(f"The device with address {device_address} is already started")
        else:
            print(f"The device with address {device_address} has error")
            self._log.error(f"The device with address {device_address} is already started")

    # used to stop cooler, fan and pump
    def close_device(self, device_address, close_command, start_status_name, error_status_name):
        if not get_parameter(error_status_name):
            if get_parameter(start_status_name):
                self.controller_send(device_address, [close_command])
                set_parameter(start_status_name, False)
            else:
                if not get_parameter(commonParameter.AUTO_MODE_NAME):
                    print(f"The device with address {device_address} is already stopped")
                self._log.info(f"The device with address {device_address} is already stopped")
        else:
            print(f"The device with address {device_address} has error")
            self._log.error(f"The device with address {device_address} has error")

    # change to auto model
    @staticmethod
    def switch_to_auto():
        if not get_parameter(commonParameter.AUTO_MODE_NAME) and get_parameter(commonParameter.SENSOR_VALUE_NAME) and commonParameter.TEMPER_BOT_THRESHOLD < get_parameter(
                commonParameter.SENSOR_VALUE_NAME) \
                < commonParameter.TEMPER_TOP_THRESHOLD:
            set_parameter(commonParameter.AUTO_MODE_NAME, True)

    # TODO change to manual model
    @staticmethod
    def switch_to_manual():
        print("send command to manual")
        if get_parameter(commonParameter.AUTO_MODE_NAME):
            set_parameter(commonParameter.AUTO_MODE_NAME, False)
        else:
            print("you already in manual state")

    # use console to send commands
    def send_commands(self):
        while True:
            if get_parameter(commonParameter.AUTO_MODE_NAME):
                # add a short sleep to avoid excessive printing
                print(get_parameter(commonParameter.AUTO_MODE_NAME))
                time.sleep(1)
                continue
            user_input = input("Enter command:")
            if user_input.strip().lower() == "cooler open":
                self.open_device(
                    commonParameter.ADDRESS_COOLER_CA,
                    commonParameter.COOLER_OPEN,
                    commonParameter.COOLANT_START_STATUS_NAME,
                    commonParameter.COOLANT_ERROR_STATUS_NAME,
                )
            elif user_input.strip().lower() == "cooler close":
                self.close_device(
                    commonParameter.ADDRESS_COOLER_CA,
                    commonParameter.COOLER_CLOSE,
                    commonParameter.COOLANT_START_STATUS_NAME,
                    commonParameter.COOLANT_ERROR_STATUS_NAME,
                )
            elif user_input.strip().lower() == "fan open":
                self.open_device(
                    commonParameter.ADDRESS_FAN_CA,
                    commonParameter.FAN_OPEN,
                    commonParameter.FAN_START_STATUS_NAME,
                    commonParameter.FAN_ERROR_STATUS_NAME,
                )
            elif user_input.strip().lower() == "fan close":
                self.close_device(
                    commonParameter.ADDRESS_FAN_CA,
                    commonParameter.FAN_CLOSE,
                    commonParameter.FAN_START_STATUS_NAME,
                    commonParameter.FAN_ERROR_STATUS_NAME,
                )
            elif user_input.strip().lower() == "pump open":
                self.open_device(
                    commonParameter.ADDRESS_PUMP_CA,
                    commonParameter.PUMP_OPEN,
                    commonParameter.PUMP_START_STATUS_NAME,
                    commonParameter.PUMP_ERROR_STATUS_NAME,
                )
            elif user_input.strip().lower() == "pump close":
                self.close_device(
                    commonParameter.ADDRESS_PUMP_CA,
                    commonParameter.PUMP_CLOSE,
                    commonParameter.PUMP_START_STATUS_NAME,
                    commonParameter.PUMP_ERROR_STATUS_NAME,
                )
            elif user_input.strip().lower() == "auto":
                self.switch_to_auto()
            elif user_input.strip().lower() == "manual":
                print("to manual")
                self.switch_to_manual()
            else:
                self._log.info("enter the wrong command")
                print("please enter the right command!")

    def generate_picture(self):
        plt.figure(figsize=(10, 6))

        plt.subplot(511)
        plt.plot(self._timestamp_log, self._test_temperature_log)
        plt.title('Temperature Log')

        plt.subplot(512)
        plt.plot(self._timestamp_log, self._test_sensor_status_log)
        plt.title('Sensor Status Log')

        plt.subplot(513)
        plt.plot(self._timestamp_log, self._test_cooler_status_log)
        plt.title('Cooler Status Log')

        plt.subplot(514)
        plt.plot(self._timestamp_log, self._test_fan_status_log)
        plt.title('Fan Status Log')

        plt.subplot(515)
        plt.plot(self._timestamp_log, self._test_pump_status_log)
        plt.title('Pump Status Log')

        plt.tight_layout()
        # generate a plot.png in project fold, this is based
        plt.savefig('plot.png')

    def step(self):
        input_thread = threading.Thread(target=self.send_commands)
        input_thread.start()

        while True:
            for information in check_information:
                self.controller_send(information[0], [information[1]])
                self.communicate_to_device(information[0])



