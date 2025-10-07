from time import sleep
import random

import mariadb
import serial,time

conn = mariadb.connect(
    user="admin_prog",
    password="cvvljllv557",
    host="172.17.42.100",
    port=3306,
    database="jlr_hris",
)

def send_at(cmd, delay=3):
    ser.write((cmd + "\r\n").encode())  # send command with CR+LF
    time.sleep(delay)
    resp = ser.read_all().decode(errors="ignore")  # read response
    print(f"{cmd} -> {resp.strip()}")
    return resp

def read_response(timeout=45):
    end_time = time.time() + timeout
    resp = b""
    while time.time() < end_time:
        line = ser.readline()
        if line:
            resp += line
        else:
            break
    return resp.decode(errors="ignore")

def send_sms(recipient, message):
    # Step 1: send the command
    ser.write(f'AT+CMGS="{recipient}"\r\n'.encode())
    time.sleep(2)
    resp = read_response(timeout=45)
    print("CMGS prompt:", resp)

    # If we didn’t get '>' prompt, fail immediately
    if ">" not in resp:
        print("No prompt received, aborting.")
        return False

    # Step 2: send the message text + Ctrl+Z
    ser.write(message.encode() + b"\x1A")
    resp = read_response(timeout=45)
    print("Send response:", resp)

    # Step 3: check success/failure
    if "+CMGS:" in resp and "OK" in resp:
        return True
    elif "+CMS ERROR" in resp:
        return False
    else:
        return False

'''
conn = mariadb.connect(
    user="root",
    password="elmer",
    host="127.0.0.1",
    port=3307,
    database="jlr_hris",
)
'''

# Initiating
# ser = serial.Serial()
# ser.port = "COM5"
# ser.baudrate = 9600 # transmission speed depending on the device
# ser.writeTimeout = 20 # max time to wait for write operations to complete

ser = serial.Serial("COM3", 9600, timeout=10)

ser.close()
ser.open()

# ser.write(b'AT+CSCS="GSM"\n')
# time.sleep(2)

cur = conn.cursor()

cur.execute("SELECT * FROM sms WHERE sent_on IS NULL ORDER BY id asc;")

rows = cur.fetchall()

send_at("AT+CMGF=1")
send_at('AT+CSCS="GSM"')

for row in rows :
    # Sending SMS

    recipient_number = row[3]
    message = row[5]

    # ser.write('AT+CMGS="{}"\r\n'.format(recipient_number).encode())
    # ser.write(f'AT+CMGS="{recipient_number}"\r\n'.encode())

    resp = b""

    while True:
        line = ser.readline()
        # print("=" + str(line))
        if not line:
            break
        resp += line
        if b">" in line:
            break
    if send_sms(recipient_number, message):
        print(f"SMS sent to {recipient_number}")
        cur.execute("UPDATE sms SET sent_on = NOW() WHERE id = ?", (row[0],))
        conn.commit()
        sleep(random.randint(90, 120))
    else:
        print(f"SMS failed to {recipient_number}")



    # update = "update sms set sent_on = now() where id = " + str(row[0])

ser.close()