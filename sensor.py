from device import Device
import commonParameter
import can
import random
from commonParameter import get_parameter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


class Sensor(Device):
    def __init__(self, can_id, log):
        super().__init__(can_id, log)
        self._can_bus = can.interface.Bus('vcan0', bustype='socketcan')
        self._test_temperature_log = []
        self._test_sensor_status_log = []
        self._test_cooler_status_log = []
        self._test_fan_status_log = []
        self._test_pump_status_log = []
        self._timestamp_log = []
        self._index = 0
        self._start_time = datetime.now()
        self._pre_temp_value = 35

    def start(self, data):
        pass

    def stop(self, data):
        pass

    def send_mock_value(self):
        if not commonParameter.get_parameter(commonParameter.AUTO_MODE_NAME):
            self._index = 0
            try:
                message = can.Message(arbitration_id=commonParameter.ADDRESS_CONTROLLER_CA, data=[0x20])
                self._can_bus.send(message)
            except Exception as e:
                self._log.error(f"Failed to send message: {e}")
            self._log.info(f"Device {self._can_id}: sent a mock value.")
        else:
            # insure mock temp value under control, sacrificed a little time
            temp_value_to_send = int(random.uniform(29, 42))
            while abs(temp_value_to_send - self._pre_temp_value) > 7:
                temp_value_to_send = int(random.uniform(29, 42))
            self._pre_temp_value = temp_value_to_send

            try:
                message = can.Message(arbitration_id=commonParameter.ADDRESS_CONTROLLER_CA, data=[temp_value_to_send])
                self._can_bus.send(message)
            except Exception as e:
                self._log.error(f"Failed to send message: {e}")
            self._log.info(f"Device {self._can_id}: sent a mock value: {temp_value_to_send}")

    def check_state(self, data):
        # Here I implement the specific way for the Pump to send its state.
        # In this simple example, we're always sending an OK state.
        try:
            message = can.Message(arbitration_id=self._can_id, data=data)
            self._can_bus.send(message)
        except Exception as e:
            self._log.error(f"Failed to send message: {e}")
        self._log.info(f"Device {self._can_id}: sent OK state.")

    def step(self):
        while True:
            message = self._can_bus.recv()
            # if receive message about check state
            if message and message.arbitration_id == commonParameter.ADDRESS_SENSOR_CA and message.data[0] == commonParameter.SENSOR_STATE_OK:
                self._log.info("get sensor message")
                self.check_state([commonParameter.SENSOR_STATE_IS_OK])
            # if receive message about ask sensor value
            if message and message.arbitration_id == commonParameter.ADDRESS_SENSOR_CA and message.data[0] == commonParameter.SENSOR_VALUE_REQUEST:
                self._log.info("send sensor to controller")
                self.send_mock_value()


