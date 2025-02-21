

import serial
import time

class KoradPowerSupply:
    def __init__(self, id='01', port: str = "/dev/serial/by-id/usb-Nuvoton_KORAD_USB_Mode_002800D40252-if00", baudrate: int = 11520, timeout: float = 1):
        self.id = id
        self.ser = serial.Serial(port, baudrate=baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE, timeout=timeout, rtscts=False, xonxoff=False, dsrdtr=False)
        time.sleep(1)
    
    def send_command(self, command: str):
        """Send a command to the power supply."""
        self.ser.write(f'{command}\r\n'.encode('utf-8'))
        time.sleep(0.1)
    
    def beep_on(self):
        """Beep the power supply."""
        self.send_command('BEEP'+self.id+':1')
    
    def beep_off(self):
        """Stop the beep of the power supply."""
        self.send_command('BEEP'+self.id+':0')
    
    def get_id(self):
        """Get the ID of the power supply."""
        return self.id

    def get_serialno(self):
        """Get the Serial number of the power supply."""
        self.send_command('*IDN?')
        response = self.read_response()
        return response

    def get_voltage(self) -> float:
        """Retrieve the output voltage from the power supply."""
        self.send_command('VOUT'+self.id+'?')
        response = self.read_response()
        return float(response) if response else 0.0
    
    def get_current(self) -> float:
        """Retrieve the output current from the power supply."""
        self.send_command('IOUT'+self.id+'?')
        response = self.read_response()
        return float(response) if response else 0.0
    
    def set_voltage(self, voltage: float):
        """Set the output voltage of the power supply."""
        command = f'VSET{self.id}:{voltage:.3f}'  
        print(command)
        self.send_command(command)
        time.sleep(0.1)
    
    def set_current(self, current: float):
        """Set the output current of the power supply."""
        self.send_command(f'ISET{self.id}:{current:.3f}')
        time.sleep(0.1)
    
    def get_output_onoff(self):
        """Check if the power supply output is on."""
        self.send_command('OUT'+self.id+'?')
        response = self.read_response()
        return bool(int(response)) if response else False
    
    def turn_output_on(self):
        """Turn the power supply output on."""
        self.send_command('OUT'+self.id+':1')
        if self.get_output_onoff() == False:
            print("Failed to turn output on")
        else:
            print("Output turned on")
    
    def turn_output_off(self):
        """Turn the power supply output off."""
        self.send_command('OUT'+self.id+':0')
        if self.get_output_onoff() == False:
            print("Output turned off")
        else:
            print("Failed to turn off output")

    def read_response(self):    
        """Read the response from the power supply."""
        response = self.ser.readline().decode('utf-8').strip()
        return response
    
    def read_response_status(self):
        """Read the response from the power supply."""
        """ response is b'\x17\n' use int.from_bytes(response, byteorder='big')"""
        response = self.ser.read(2)
        return int.from_bytes(response, byteorder='big') if response else None
    
    def report_status(self):
        """Report the status of the power supply."""
        self.send_command('STATUS'+self.id+'?')
        response = self.read_response_status()
        if response:
            print(f"Status: {response}")  
            print(f"CC/CV: {response & 1}")  # bit 0
            print(f"Output: {(response & 2) >> 1}") # bit 1
            print(f"V/C priority: {(response & 4) >> 2}") # bit 2
            print(f"Buzzer: {(response & 16) >> 4}") # bit 4
            print(f"Lock: {(response & 32) >> 5}") # bit 5
            print(f"OVP status: {(response & 64) >> 6}") # bit 6
            print(f"OCP status: {(response & 128) >> 7}") # bit 7
            return response
        return None
    
    def get_voltage_set(self) -> float:
        """Retrieve the output voltage from the power supply."""
        self.send_command('VSET'+self.id+'?')
        response = self.read_response()
        return float(response) if response else 0.0
    
    def get_current_set(self) -> float:
        """Retrieve the output current from the power supply."""
        self.send_command('ISET'+self.id+'?')
        response = self.read_response()
        return float(response) if response else 0.0

    def report_IV(self):
        """Report the voltage and current set and readback
          of the power supply."""
        setV = self.get_voltage_set()
        setI = self.get_current_set()
        readV = self.get_voltage()
        readI = self.get_current()
        onoff = self.get_output_onoff()
        # print as one line set voltage, current and on/off status
        print(f"Set V: {setV:.3f}V, Set I: {setI:.3f}A, Read V: {readV:.3f}V, Read I: {readI:.3f}A, Output: {onoff}")   

    def disconnect(self):
        """Disconnect the power supply."""
        self.ser.close()
        print("Disconnected")
            
# Example usage
if __name__ == "__main__":
    port = "/dev/serial/by-id/usb-Nuvoton_KORAD_USB_Mode_002800D40252-if00"
    psu = KoradPowerSupply(port=port, id='01')
    print('Serial number: ' + psu.get_serialno())    
    print('id=' + psu.get_id())
    psu.beep_on()
    time.sleep(1)
    psu.beep_off()

    print(f"Voltage set: {psu.get_voltage_set()}V")
    print(f"Current set: {psu.get_current_set()}A")

    psu.set_voltage(5.11)
    print("Voltage set to 5.11V")
        
    psu.set_current(0.05)
    print("Current set to 0.05A")
        
    psu.turn_output_on()

    status = psu.report_status()
    psu.report_IV()        


    psu.turn_output_off()

    status = psu.report_status()

    psu.report_IV()    
    psu.disconnect()


        
        
        