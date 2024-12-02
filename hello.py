import pymysql
import json
import math
# from modules.util.globals import REMOTEDB_SERVER, REMOTEDB_UID, REMOTEDB_PWD, REMOTEDB_PORT

# Database connection details
# DB_CONFIG = {
#     "host": REMOTEDB_SERVER,
#     "port": int(REMOTEDB_PORT),
#     "user": REMOTEDB_UID,
#     "password": REMOTEDB_PWD,
#     "database": "axia"
# }
DB_CONFIG = {
    "host": "compilerbv",
    "port": 3306,
    "user": "BVAdmin",
    "password": "VectronAdmin",
    "database": "axia"
}

def connect_to_database(config):
    """
    Establishes a connection to a database using the provided configuration.

    This function attempts to connect to a database using the parameters in the `config` dictionary. If the connection is successful, a connection object is returned. If there is an error while attempting to connect, an error message is printed, and None is returned.

    :param config: A dictionary containing database connection parameters such as host, port, user, password, and database name.
    :type config: dict
    :return: A pymysql connection object if successful, or None if an error occurs.
    :rtype: pymysql.Connection or None
    """
    try:
        return pymysql.connect(**config)
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def fetch_query_results(connection, query):
    """
    Executes a SQL query on the given database connection and returns the results.

    :param connection: The database connection to use
    :type connection: pymysql.Connection
    :param query: The SQL query to execute
    :type query: str
    :return: The query results as a list of dictionaries
    :rtype: list
    """
   
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")
        return []
    
def process_string(input_string):
    # Define the prefixes to split
    """
    Process a string by splitting it into parts based on predefined prefixes.

    The function splits the input string into parts based on the prefixes defined in `prefixes_to_split` unless the part starts with one of the prefixes in `prefixes_to_exclude`. The part is then split into the prefix and the number part, which are added separately to the output list. If the part does not need to be split, it is added to the output list as is.

    The processed parts are then joined back into a single string using spaces as separators.

    Parameters
    ----------
    input_string : str
        The string to be processed

    Returns
    -------
    str
        The processed string
    """
    prefixes_to_split = ["BTD", "BX", "BCR"]
    # Prefixes to exclude from splitting
    prefixes_to_exclude = ["BXN"]

    # Split the string into parts
    parts = input_string.split()
    processed_parts = []

    for part in parts:
        # Check if part starts with any prefix that needs to be split
        if any(part.startswith(prefix) for prefix in prefixes_to_split) and not any(part.startswith(exclude) for exclude in prefixes_to_exclude):
            # Split the prefix from the number
            for prefix in prefixes_to_split:
                if part.startswith(prefix):
                    processed_parts.append(prefix)
                    processed_parts.append(part[len(prefix):])  # Append the number part
                    break
        else:
            # Keep the part as is
            processed_parts.append(part)
    
    # Join the processed parts back into a single string
    return " ".join(processed_parts)

def map_motor_type(motor_type):
    """
    Maps the motor type to a tuple of (motor type name, synchronous, reluctance)
    
    :param motor_type: The motor type ID
    :return: A tuple of (motor type name, synchronous, reluctance)
    """
    motor_type_map = {
        0: ("Asynchronous Induction AC", "no", "no"),
        1: ("Synchronous Reluctance", "yes", "yes"),
        2: ("Synchronous Servo AC", "yes", "no")
    }
    return motor_type_map.get(motor_type, ("", "", ""))

def calculate_rated_power(rated_torque, rated_speed, rated_mech_power):
    """
    Calculate the rated power of the motor.
    """
    if rated_torque and rated_speed:
        rated_power = round(((2 * math.pi * rated_torque * rated_speed) / 60) / 1000, 1)
    else:
        rated_power = rated_mech_power
    
    return str(rated_power) if rated_power else ""


def get_designation_size(designation, series):
    """
    Extract the designation size based on the series.
    """
    size = designation.split(" ")[1]
    if series[0] == "BMD":
        size = designation.split(" ")[1].split("_")[0]
    return size


def get_designation_rating(designation, series):
    """
    Extract the designation rating for BSR series.
    """
    if series[0] == "BSR":
        return designation.split(" ")[2]
    return ""

def calculate_rated_frequency(designation, pole_pair_number, rated_speed, rated_frequency):
    """
    Calculate the rated frequency based on motor type.
    """
    designation_name = designation.split(" ")[0]
    if designation_name == "BTD" or designation_name == "BCR":
        return round(((rated_speed / 60) * pole_pair_number )*100, 2)
    elif designation_name == "BMD":
        return round((rated_speed / 60) * pole_pair_number, 2)
    return rated_frequency

def calculate_max_rated_frequency(designation, pole_pair_number, rated_speed, rated_frequency):
    """
    Calculate the max rated frequency based on motor type.
    """
    designation_name = designation.split(" ")[0]
    fmax = 0
    if designation_name == "BTD" or designation_name == "BCR":
        fmax = round((rated_speed * 100) / 60, 2)
    else:
        fmax = round((rated_speed / 60), 2)
    return fmax * 2


def calculate_rated_speed_value(designation, rated_speed, raw_rated_speed):
    """
    Determine the rated speed value based on motor type and series.
    """
    designation_name = designation.split(" ")[0]
    if designation_name == "BTD" or designation_name == "BCR":
        return str(int(raw_rated_speed * 100))
    return str(rated_speed)


def process_motor(row):
    series = row["c_strMotorName"].split(" ")  # Extract the series
    motor_type_code = row["cr_ui32MotorType"]
    
    rated_voltage = 230 if row["c_f32RatedVoltage"] <= 230 else 400

    encoder_list = row["encoder_names"].split(",") if row["encoder_names"] else []
    brake_list = row["brakes_names"].split(",") if row["brakes_names"] else []

    motor_type, synchronous, reluctance = map_motor_type(motor_type_code)

    # Calculate rated speed based on series
    rated_speed = int(row["c_f32RatedSpeed"])

    # Convert to strings for certain fields
    rated_voltage_str = str(rated_voltage)

    # Construct _name and _designation
    if motor_type_code == 0:
        # Handle the asynchronous induction AC motor type
        rated_frequency = int(row["c_f32RatedFrequency"]) if row["c_f32RatedFrequency"] else ""
        if rated_frequency:
            name = f"{row['c_strMotorName']}_{row['c_strSize']} {row['c_ui32PolePairNumber']} {rated_voltage_str}-{rated_frequency}"
        else:
            name = f"{row['c_strMotorName']}_{row['c_strSize']} {row['c_ui32PolePairNumber']} {rated_voltage_str}"

    elif motor_type_code == 1:
        # Handle the synchronous reluctance motor type
        parts = row['c_strMotorName'].split()
        if len(parts) > 2:  # Ensure there are enough parts to modify
            parts[1] = f"{parts[1]}_{parts[2]}"
            del parts[2]  # Remove the third part after combining
        output_string = " ".join(parts)
        name = output_string

    elif motor_type_code == 2:
        # Handle the synchronous servo AC motor type
        rated_speed_str = str(rated_speed)  # Convert rated_speed to string
        name = f"{row['c_strMotorName']}_{row['c_strSize']}-{rated_speed_str}-{rated_voltage_str}"

    # Replace underscores and hyphens in the name to create the initial designation
    designation = name.replace("_", " ").replace("-", " ")
    
    designation_speed = str(rated_speed) if(designation.split(" ")[0] != "BSR") else str(int(rated_speed / 100))

    # Handle different motor type codes with corresponding logic
    if motor_type_code == 0:  # Asynchronous Induction AC
        if series[0] != "BMD":
            # Process the string differently for motors not in the "BMD" series
            designation = process_string(name.replace("_", ""))

    elif motor_type_code == 1:  # Synchronous Reluctance
        # Append rated voltage for synchronous reluctance motors
        designation = f"{name.replace('_', ' ')} {rated_voltage}"

    elif motor_type_code == 2:  # Synchronous Servo AC
        # Apply the `process_string` function for type 2 motors
        designation = process_string(designation)


    # Calculate _ratedpower
    rated_torque = row["c_f32RatedTorque"]  # Assuming peak torque as rated torque

    rated_power = calculate_rated_power(rated_torque, rated_speed, row["c_f32RatedMechPower"])

    designation_size = get_designation_size(designation, series)

    designation_rating = get_designation_rating(designation, series)

    rated_frequency = calculate_rated_frequency(
        designation,
        row["c_ui32PolePairNumber"], 
        row["c_f32RatedSpeed"], 
        row["c_f32RatedFrequency"]
    )

    rated_speed_value = calculate_rated_speed_value(
        designation, 
        rated_speed, 
        row["c_f32RatedSpeed"]
    )

   
    maximum_frequency = calculate_max_rated_frequency(
        designation,
        row["c_ui32PolePairNumber"], 
        row["c_f32RatedSpeed"], 
        row["c_f32RatedFrequency"]
    )
    # Build the motor object
    return {
        # General Motor Information
        "_name": name.replace(".0", ""),
        "_series": series[0],
        "_type": motor_type,
        "_synchronous": synchronous,
        "_reluctance": reluctance,

        # Designation Information
        "_designation": designation,
        "_designation_size": designation_size,
        "_designation_polenumber": str(row["c_ui32PolePairNumber"]),
        "_designation_voltagefrequency": (
            f"{rated_voltage_str}-{int(row['c_f32RatedFrequency'])}"
            if motor_type_code == 0 else rated_voltage_str
        ),
        "_designation_insulationclass": (
            ["CLF", "CLH"] if motor_type_code == 0
            else ["F", "H"] if series[0] == "BSR" 
            else []
        ),
        "_designation_braketype": brake_list,
        "_designation_feedbackdevice": encoder_list,
        "_designation_stalltorque": row["c_strSize"],
        "_designation_speed": designation_speed,
        "_designation_rating": designation_rating,

        # Rated Characteristics
        "_ratedvoltage": str(int(row["c_f32RatedVoltage"])),
        "_ratedcurrent": str(round(row["c_f32RatedCurrent"], 2)),
        "_ratedspeed": rated_speed_value,
        "_ratedtorque": str(rated_torque) if rated_torque else "",
        "_ratedfrequency": str(rated_frequency) if rated_frequency else "",
        "_cm_maximumfrequency": str(maximum_frequency) if maximum_frequency else "",
        "_ratedpower": str(rated_power),

        # Additional Characteristics
        "_polepairsnumber": str(row["c_ui32PolePairNumber"]),
        "_powerfactor": str(row["c_f32CosPhi"]) if row["c_f32CosPhi"] else "",
        "_cm_maximumtorque": str(row["c_f32Mmax"]) if row["c_f32Mmax"] else "",
        "_statorresistance": str(round(row["c_f32StatorResistance"],2)) if row["c_f32StatorResistance"] else "",
        "_statorinductance": str(round(row["c_f32StatorInductance_d"],4)),
        "_voltageconstant": (
            str(row["c_f32VoltageConstant"]) if row["c_f32VoltageConstant"] else ""
        ),
        "_ratedmagnetisingcurrent": (
            str(round(row["c_f32RatedMagnetisationCurrent"], 2))
            if row["c_f32RatedMagnetisationCurrent"] else ""
        ),
        "_stallcurrent": str(row["c_f32I0"]) if row["c_f32I0"] else "",
        "_peakcurrent": str(row["c_f32IMax"]) if row["c_f32IMax"] else "",

        # Resolver Configuration
        "_resolver_evalmode": "0" if motor_type_code == 2 else "",
        "_resolver_operationmode": "10" if motor_type_code == 2 else "",
        "_resolver_numberofpolepairs": (
            "1" if [device for device in encoder_list if device.startswith("RES")] else ""
        ),
        "_resolver_offset": (
            str(int(row["max_offset"])) if row["max_offset"] is not None else ""
        ),
        "_resolver_exitationphase": "0.0" if motor_type_code == 2 else "",

        # Thermal Properties
        "_protectiveswitchthermaltimemotor": (
            str(row["c_f32MotorTimeConstant"]) if row["c_f32MotorTimeConstant"] else ""
        ),
        "_protectiveswitchthermaltimestator": (
            str(row["c_f32CopperTimeConstant"]) if row["c_f32CopperTimeConstant"] else ""
        ),

        # Acceleration and Deceleration
        "_accelerationclockwise": "5.00" if motor_type_code == 1 else "",
        "_decelerationclockwise": "5.00" if motor_type_code == 1 else "",

        # Control Input/Output
        "_controlinputoutput_operationmode": "1" if motor_type_code == 1 else "",
        "_referencefrequencysource": "111" if motor_type_code == 1 else "",
        "_mtpaliteangle": "45.0" if motor_type_code == 1 else "",

        # Unimplemented Keys
        "_protectiveswitchoperationmode":"",
        "_ratedslipcorrectionfactor": "",
        "_leakagecoefficient": "",
        "_speedcontrolleramplification": "",
        "_speedcontrollerintegraltime": "",
        "_fieldcontrollerisdupperlimit": "",
        "_fieldcontrollerisdlowerlimit": "",
        "_frequencyswitchofflimit": "",
        "_fieldcontrollerintegraltime": "",
        "_minimumfrequency": "",
        "_maximumfrequency": "",
        "_breakawaycurrent": "",
        "_startingcurrent": "",
        "_frequencylimit": "",
        "_stoppingbehaviour_operationmode": "",
        "_holdingtime": "",
        "_minfluxformationtime": "",
        "_maxfluxformationtime": "",
        "_currentduringfluxformation": "",
        "_operationmodemtpa": "",
        "_holdingcurrent": "",
        "_selectionlookuptableforldlqlut": "",
        "_maximumtimefocfflimitcurrinjfflimit": "",
        "_ld": "",
        "_lq": "",
        "_ldlqadaptionatmtpa": "",
        "_minmtpamagnetisingcurrentsetpoint": "",
        "_maxmtpamagnetisingcurrentsetpoint": "",
        "_maximumcurrentofcurrentinjection": ""
    }

# Main function to orchestrate the process
def main():
    """
    Main function to orchestrate the process of fetching data from the database and generating a JSON file containing the processed data.

    The function connects to the database, fetches the results of a query, processes the results into a list of dictionaries, creates a JSON structure containing the processed data, and writes the JSON structure to a file named "devices.json".
    """
    connection = connect_to_database(DB_CONFIG)
    if not connection:
        return

    query = """
    SELECT 
        tm_motors.cp_ui32MotorID,
        tm_motors.cr_ui32MotorType,
        tm_motors.c_strMotorName,
        tm_motors.c_strSize,
        tm_motors.c_f32RatedVoltage,
        tm_motors.c_f32RatedCurrent,
        tm_motors.c_f32RatedSpeed,
        tm_motors.c_f32RatedMechPower,
        tm_motors.c_ui32PolePairNumber,
        tm_motors.c_f32CosPhi,
        tm_motors.c_f32StatorResistance,
        tm_motors.c_f32RatedTorque,
        tm_motors.c_f32I0,
        tm_motors.c_f32IMax,
        tm_motors.c_f32Mmax,
        tm_motors.c_f32VoltageConstant,
        tm_motors.c_f32StatorInductance_d,
        tm_motors.c_f32MotorTimeConstant,
        tm_motors.c_f32CopperTimeConstant,
        tm_motors.c_f32RatedMagnetisationCurrent,
        tm_motors.c_f32RatedFrequency,
        MAX(tm_encoders.c_f32Offset) AS max_offset,
        GROUP_CONCAT(DISTINCT tm_encoders.c_strName) AS encoder_names,
        GROUP_CONCAT(DISTINCT tm_brakes.c_strName) AS brakes_names
    FROM 
        tm_motors
    LEFT JOIN 
        (SELECT DISTINCT cr_motors_ui32ID, cr_encoders_ui32ID FROM tcr_motorencoders) tcr_motorencoders
        ON tm_motors.cp_ui32MotorID = tcr_motorencoders.cr_motors_ui32ID
    LEFT JOIN 
        tm_encoders 
        ON tcr_motorencoders.cr_encoders_ui32ID = tm_encoders.cp_ui32ID
    LEFT JOIN 
        (SELECT DISTINCT cr_motors_ui32ID, cr_brakes_ui32ID FROM tcr_motorbrakes) tcr_motorbrakes
        ON tm_motors.cp_ui32MotorID = tcr_motorbrakes.cr_motors_ui32ID
    LEFT JOIN 
        tm_brakes 
        ON tcr_motorbrakes.cr_brakes_ui32ID = tm_brakes.cp_ui32ID
    GROUP BY 
        tm_motors.cp_ui32MotorID,
        tm_motors.cr_ui32MotorType,
        tm_motors.c_strMotorName,
        tm_motors.c_strSize,
        tm_motors.c_f32RatedVoltage,
        tm_motors.c_f32RatedCurrent,
        tm_motors.c_f32RatedTorque,
        tm_motors.c_f32RatedMechPower,
        tm_motors.c_f32IMax,
        tm_motors.c_f32RatedFrequency;
    """

    rows = fetch_query_results(connection, query)
    devices = [process_motor(row) for row in rows]

    json_data = {
        "data": {
            "devices": devices
        }
    }

    with open("devices.json", "w") as json_file:
        json.dump(json_data, json_file, indent=2)

    print("JSON file 'devices.json' created successfully!")

    if connection.open:
        connection.close()

if __name__ == "__main__":
    main()
