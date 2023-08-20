# Define CAN addresses for devices and controllers
ADDRESS_PUMP_CA = 0x10
ADDRESS_COOLER_CA = 0x20
ADDRESS_FAN_CA = 0x30
ADDRESS_SENSOR_CA = 0x40
ADDRESS_CONTROLLER_CA = 0x80

# Define status code
PUMP_STATE_OK = 0x01
COOLER_STATE_OK = 0x02
FAN_STATE_OK = 0x03
SENSOR_STATE_OK = 0x04
PUMP_STATE_IS_OK = 0x10
COOLER_STATE_IS_OK = 0x11
FAN_STATE_IS_OK = 0x12
SENSOR_STATE_IS_OK = 0x13
COOLER_OPEN = 0x05
COOLER_CLOSE = 0x06
FAN_OPEN = 0x07
FAN_CLOSE = 0x08
PUMP_OPEN = 0x0A
PUMP_CLOSE = 0x0B
SENSOR_VALUE_REQUEST = 0x0C

# if over 45 means There is a high probability that some abnormal conditions occur, and it is best to operate manually
TEMPER_TOP_THRESHOLD = 45
# if below 25 degree, it is no necessary to open cool system
TEMPER_BOT_THRESHOLD = 25
# If the deviation of the continuous sensor is greater than 5, the sensor is considered abnormal and exit auto mode,
# for test, I give much bigger
TEMPER_MAX_DIFFERENCE = 13

# Define parameter name
PUMP_START_STATUS_NAME = "Pump Start Status"
PUMP_ERROR_STATUS_NAME = "Pump Error Status"
FAN_START_STATUS_NAME = "Fan Start Status"
FAN_ERROR_STATUS_NAME = "Fan Error Status"
COOLANT_START_STATUS_NAME = "Coolant Start Status"
COOLANT_ERROR_STATUS_NAME = "Coolant Error Status"
SENSOR_ERROR_STATUS_NAME = "Temperature Sensor Error Status"
SENSOR_VALUE_NAME = "temp sensor value"
AUTO_MODE_NAME = "system running mode"

# Define parameter description
PUMP_START_STATUS_DESC = "Pump Start Status"
PUMP_ERROR_STATUS_DESC = "Pump Error Status"
FAN_START_STATUS_DESC = "Fan Start Status"
FAN_ERROR_STATUS_DESC = "Fan Error Status"
COOLANT_START_STATUS_DESC = "Coolant Start Status"
COOLANT_ERROR_STATUS_DESC = "Coolant Error Status"
SENSOR_ERROR_STATUS_NAME_DESC = "Temperature Sensor Error Status"
SENSOR_VALUE_DESC = "temp sensor value"
AUTO_MODE_DESC = "system running mode"


# The Parameter class is used to store the information and values of parameters
class Parameter:
    def __init__(self, name, value_type, description):
        self.name = name
        self.value_type = value_type
        self.value = None  # Initialize the value to None
        self.description = description


PARAMETER_DEFINITIONS = {
    # Define parameters for each device's status
    PUMP_START_STATUS_NAME: (bool, PUMP_START_STATUS_DESC),
    PUMP_ERROR_STATUS_NAME: (bool, PUMP_ERROR_STATUS_DESC),
    FAN_START_STATUS_NAME: (bool, FAN_START_STATUS_DESC),
    FAN_ERROR_STATUS_NAME: (bool, FAN_ERROR_STATUS_DESC),
    COOLANT_START_STATUS_NAME: (bool, COOLANT_START_STATUS_DESC),
    COOLANT_ERROR_STATUS_NAME: (bool, COOLANT_ERROR_STATUS_DESC),
    SENSOR_ERROR_STATUS_NAME: (bool, SENSOR_ERROR_STATUS_NAME_DESC),
    SENSOR_VALUE_NAME: (float, SENSOR_VALUE_DESC),
    # Define parameters for operation mode
    AUTO_MODE_NAME: (bool, AUTO_MODE_DESC)
}


# Group Parameters into a Dictionary
all_parameters = {}
for name, (value_type, description) in PARAMETER_DEFINITIONS.items():
    all_parameters[name] = Parameter(name, value_type, description)


# The function that sets the parameter
def set_parameter(parameter_name, new_value):
    parameter = all_parameters.get(parameter_name)
    if parameter is not None:
        # Check if the new value type matches the parameter value type
        if isinstance(new_value, parameter.value_type):
            parameter.value = new_value
        else:
            print(
                f"Error: The type of the new value does not match the value type of the parameter '{parameter_name}'.")
    else:
        print(f"Error: The parameter '{parameter_name}' does not exist.")


# Function to get parameter by name
def get_parameter(parameter_name):
    parameter = all_parameters.get(parameter_name)
    return parameter.value if parameter is not None else None
