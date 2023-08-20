import can


class CanService:
    def __init__(self, channel, bustype):
        self.bus = can.interface.Bus(channel, bustype=bustype)

    def send_message(self, can_id, data):
        message = can.Message(arbitration_id=can_id, data=data)
        self.bus.send(message)
        print(f"Message sent on {self.bus.channel_info}")

    def receive_message(self):
        while True:
            return self.bus.recv()

    def shutdown(self):
        self.bus.shutdown()
