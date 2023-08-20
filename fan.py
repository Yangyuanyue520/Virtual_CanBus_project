from device import Device
import commonParameter
from commonParameter import get_parameter
import can


class Fan(Device):
    def __init__(self,  can_id, log):
        super().__init__(can_id, log)
        self._can_bus = can.interface.Bus('vcan0', bustype='socketcan')

    def start(self, data):
        # Here I implement the specific way for the fan to send its state.
        # In this simple example, we're always sending an START state.
        try:
            message = can.Message(arbitration_id=self._can_id, data=data)
            self._can_bus.send(message)
        except Exception as e:
            self._log.error(f"Failed to send message: {e}")
        self._log.info(f"Device {self._can_id}: sent START state.")

    def stop(self, data):
        # Here I implement the specific way for the fan to send its state.
        # In this simple example, we're always sending an STOP state.
        try:
            message = can.Message(arbitration_id=self._can_id, data=data)
            self._can_bus.send(message)
        except Exception as e:
            self._log.error(f"Failed to send message: {e}")
        self._log.info(f"Device {self._can_id}: sent STOP state.")

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
            if message and message.arbitration_id == commonParameter.ADDRESS_FAN_CA and message.data[0] == commonParameter.FAN_STATE_OK:
                self._log.info("get fan message")
                self.check_state([commonParameter.FAN_STATE_IS_OK])
            # if receive message about ask open fan
            elif message and message.arbitration_id == commonParameter.ADDRESS_FAN_CA and message.data[0] == commonParameter.FAN_OPEN:
                self._log.info("get message to open")
                if not get_parameter(commonParameter.AUTO_MODE_NAME):
                    print("fan has opened")
                self.start([commonParameter.FAN_OPEN])
            # if receive message about ask close fan
            elif message and message.arbitration_id == commonParameter.ADDRESS_FAN_CA and message.data[0] == commonParameter.FAN_CLOSE:
                if not get_parameter(commonParameter.AUTO_MODE_NAME):
                    print("fan has closed")
                self.stop([commonParameter.FAN_CLOSE])
