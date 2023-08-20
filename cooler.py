from device import Device
import commonParameter
from commonParameter import get_parameter
import can


class Cooler(Device):
    def __init__(self,  can_id, log):
        super().__init__(can_id, log)
        self._can_bus = can.interface.Bus('vcan0', bustype='socketcan')

    def start(self, data):
        # Here I implement the specific way for the Cooler to send its state.
        # In this simple example, we're always sending an START state.
        message = can.Message(arbitration_id=self._can_id, data=data)
        self._can_bus.send(message)
        self._log.info(f"Device {self._can_id}: sent START state.")

    def stop(self, data):
        # Here I implement the specific way for the Cooler to send its state.
        # In this simple example, we're always sending an STOP state.
        message = can.Message(arbitration_id=self._can_id, data=data)
        self._can_bus.send(message)
        self._log.info(f"Device {self._can_id}: sent STOP state.")

    def check_state(self, data):
        # Here I implement the specific way for the Pump to send its state.
        # In this simple example, we're always sending an OK state.
        message = can.Message(arbitration_id=self._can_id, data=data)
        self._can_bus.send(message)
        self._log.info(f"Device {self._can_id}: sent OK state.")

    def step(self):
        while True:
            message = self._can_bus.recv()
            # if receive message about check state
            if message and message.arbitration_id == commonParameter.ADDRESS_COOLER_CA and message.data[0] == commonParameter.COOLER_STATE_OK:
                self._log.info("get message to check state")
                self.check_state([commonParameter.COOLER_STATE_IS_OK])
            # if receive message about ask open cooler
            elif message and message.arbitration_id == commonParameter.ADDRESS_COOLER_CA and message.data[0] == commonParameter.COOLER_OPEN:
                self._log.info("get message to open")
                if not get_parameter(commonParameter.AUTO_MODE_NAME):
                    print("Cooler has opened")
                self.start([commonParameter.COOLER_OPEN])
            # if receive message about ask close cooler
            elif message and message.arbitration_id == commonParameter.ADDRESS_COOLER_CA and message.data[0] == commonParameter.COOLER_CLOSE:
                if not get_parameter(commonParameter.AUTO_MODE_NAME):
                    print("Cooler has closed")
                self.stop([commonParameter.COOLER_CLOSE])
