

import serial
import time

# /dev/serial/by-id/usb-Nuvoton_KORAD_USB_Mode_002800D40252-if00
class KoradPowerSupply:
    '''
    Class to control a single Korad KC3405 four channel power supply.
    Note that it allows each channel to be querried if run from different threads, hence the threadlock checks
    in the readbacks of the voltages and currents.  It assumes that only one voltage change, or current will be
    done at a time.

    The class is initialized with the serial device (assuming connected via USB serial device in linux).
    '''
    
    def __init__(self, port: str = "/dev/serial/by-id/usb-Nuvoton_KORAD_USB_Mode_000016E90000-if00", baudrate: int = 11520, timeout: float = 1):
        self.ser = serial.Serial(port, baudrate=baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE, timeout=timeout, rtscts=False, xonxoff=False, dsrdtr=False)
        self.threadlock = False
        time.sleep(1)
    
    def send_command(self, command: str):
        """Send a command to the power supply for the specified channel."""
        self.ser.write(f'{command}\r\n'.encode('utf-8'))
        time.sleep(0.1)
    
    def get_serialno(self):
        """Get the Serial number of the power supply."""
        self.send_command('*IDN?')
        response = self.read_response()
        return response

    def get_voltage(self, channel: str = '1') -> float:
        """Retrieve the output voltage from the power supply."""
        while self.threadlock:
            time.sleep(0.1)
        self.threadlock=True
        try:
            self.send_command('VOUT'+channel+'?')
            response = self.read_response()
        except:
            pass
        self.threadlock=False
        return float(response) if response else 0.0
    
    def get_current(self, channel: str = '1') -> float:
        """Retrieve the output current from the power supply."""
        while self.threadlock:
            time.sleep(0.1)
        self.threadlock=True
        try:
            self.send_command('IOUT'+channel+'?')
            response = self.read_response()
        except:
            pass
        self.threadlock=False
        return float(response) if response else 0.0
    
    def set_voltage(self, voltage: float, channel: str = '1'):
        """Set the output voltage of the power supply."""
        command = f'VSET{channel}:{voltage:.3f}'  
        print(command)
        self.send_command(command)
        time.sleep(0.1)
    
    def set_current(self, current: float, channel: str='1'):
        """Set the output current of the power supply."""
        self.send_command(f'ISET{channel}:{current:.3f}')
        time.sleep(0.1)
    
    
    def turn_output_on(self, channel:str='1'):
        """Turn the power supply output on."""
        self.send_command('OUT'+channel+':1')
        time.sleep(1)
        if self.get_output_onoff() == False:
            print("Failed to turn output on")
        else:
            print("Output turned on")
    
    def turn_output_off(self, channel:str='1'):
        """Turn the power supply output off."""
        self.send_command('OUT'+channel+':0')
        time.sleep(0.1)
        
        if self.get_output_onoff() == False:
            print("Output turned off")
        else:
            print("Failed to turn off output")
            
    def read_response(self):    
        """Read the response from the power supply."""
        response = self.ser.readline().decode('utf-8').strip()
        return response
    


    def get_output_onoff(self, channel:str='1'):
        """Check if the power supply output is on."""
        setV = self.get_voltage_set(channel)
        readV = self.get_voltage(channel)

        if abs(setV-readV) > 0.05:
            return False
        else:
            return True
        
    
    def get_voltage_set(self, channel='1') -> float:
        """Retrieve the output voltage from the power supply."""
        while self.threadlock:
            time.sleep(0.1)
        self.threadlock = True
        self.send_command('VSET'+channel+'?')
        response = self.read_response()
        self.threadlock = False
        return float(response) if response else 0.0
    
    def get_current_set(self, channel:str='1') -> float:
        """Retrieve the output current from the power supply."""
        while self.threadlock:
            time.sleep(0.1)
        self.threadlock = True
        self.send_command('ISET'+channel+'?')
        response = self.read_response()
        self.threadlock = False
        return float(response) if response else 0.0

    def report_IV(self,channel:str='1'):
        """Report the voltage and current set and readback
          of the power supply."""
        setV = self.get_voltage_set(channel)
        setI = self.get_current_set(channel)
        readV = self.get_voltage(channel)
        readI = self.get_current(channel)
        onoff = self.get_output_onoff(channel)
        # print as one line set voltage, current and on/off status
        print(f"Ch: {channel} Set V: {setV:.3f}V, Set I: {setI:.3f}A, Read V: {readV:.3f}V, Read I: {readI:.3f}A, Output: {onoff}")   

    def disconnect(self):
        """Disconnect the power supply."""
        self.ser.close()
        print("Disconnected")
            
# Example usage
if __name__ == "__main__":
    port = "/dev/serial/by-id/usb-Nuvoton_KORAD_USB_Mode_000016E90000-if00"
    #"/dev/serial/by-id/usb-Nuvoton_KORAD_USB_Mode_002800D40252-if00"
    channel='1' # for example test just this channel for now
    psu = KoradPowerSupply(port=port)
    print('Serial number: ' + psu.get_serialno())    

    print(f"Voltage set: {psu.get_voltage_set(channel)}V")
    print(f"Current set: {psu.get_current_set(channel)}A")

    psu.set_voltage(5.11,channel)
    print("Voltage set to 5.11 V")
        
    psu.set_current(0.1,channel)
    print("Current set to 0.1 A")

    psu.report_IV(channel)        

    psu.report_IV(channel)    
    psu.disconnect()


        
        
        
