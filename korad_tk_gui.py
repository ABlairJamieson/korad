import kontrol_korad as korad
import tkinter as tk
from tkinter import ttk
import argparse
import time
import datetime
import threading

class KonradKontrolWindow(tk.Tk):
    '''
    Tk window that holds all of the channel widgets.  Each channel has its own frame tk.Frame object (KoradControlWidget)
    which runs its update in a separate thread.  Since we only want to connect serial port to one KoradPowerSupply the
    channels share the serial port connection, and some management of locking to not have two threads talking to the PS
    at once are implemented in kontrol_korad.
    '''
    def __init__(self, port, channel_ids, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.port = port
        self.channel_ids = channel_ids
        self.koradctl = korad.KoradPowerSupply(port=self.port)
        tk.Tk.wm_title(self,"Korad Kontrol")
        #self.geometry("800x200")
        self.create_widgets()

    def create_widgets(self):
        '''Create the widgets for the GUI.
            They include a button to add a channel
        '''
        # add a date and time label that updates every second
        self.date_time = ttk.Label(self, text="")
        self.date_time.pack()
        self.update_date_time()
        
        self.channels = {}
        for chan in self.channel_ids:
            self.channels[chan] = KonradChannelWidget( self.koradctl, chan )
            self.channels[chan].pack(side=tk.TOP)

        # quit button
        self.quit_button = ttk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack(side=tk.BOTTOM)

    def quit(self):
        print('quitting')
        self.koradctl.disconnect()
        return super().quit()

    def update_date_time(self):
        '''Update the date and time label every second'''

        now = datetime.datetime.now()
        self.date_time.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
        self.after(1000, self.update_date_time) 

    def mainloop(self):
        for chan in self.channel_ids:
            print('update channel:', chan )
            self.channels[chan].update()
        tk.Tk.update(self)
        tk.Tk.mainloop(self)

class KonradChannelWidget(tk.Frame):
    def __init__(self, koradctl, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.koradctl = koradctl
        self.channel = channel

        #self.title("Korad Kontrol")
        #self.geometry("600x300")

        self.create_widgets()
        self['padx'] = 5
        self['pady'] = 5
        self['borderwidth'] = 1
        self['relief'] = 'solid'

    def create_widgets(self):
        '''Create the widgets for the GUI.
            They include voltage set, current set, 
            voltage readback, current readback, and output on/off.
            Also a readback of the output status.
            The readbacks should update once every 15 seconds 
        '''
        # put channel id label at the top
        self.channel_id_label = ttk.Label(self, text="Channel "+self.channel )
        self.channel_id_label.pack(side=tk.TOP,pady=5)


        # voltage and current set should include a label, entry, and button
        # voltage label, entry and button are next to each other, then current label, entry and button below
        self.voltage_frame = tk.Frame(self)
        self.voltage_frame.pack(side=tk.TOP,pady=5)
        self.voltage_label = ttk.Label(self.voltage_frame, text="V Set (V)")
        self.voltage_entry = ttk.Entry(self.voltage_frame, width=10)
        voltage = self.koradctl.get_voltage_set( self.channel )
        print('voltage:',voltage)
        self.voltage_entry.insert(0,str(voltage))
        self.set_voltage_button = ttk.Button(self.voltage_frame, text="Set V", command=self.set_voltage)
        self.voltage_label.pack(side=tk.LEFT, padx=5 )
        self.voltage_entry.pack(side=tk.LEFT, padx=5)
        self.set_voltage_button.pack(side=tk.LEFT, padx=5)

        self.voltage_readback_label = ttk.Label(self.voltage_frame, text="V read: ")
        self.voltage_readback_label.pack(side=tk.LEFT,padx=5)
        self.voltage_readback = ttk.Label(self.voltage_frame, text="- V")
        self.voltage_readback.pack(side=tk.LEFT,padx=5)


        self.current_frame = tk.Frame(self)
        self.current_frame.pack(side=tk.TOP,pady=5)
        self.current_label = ttk.Label(self.current_frame, text="I Set (A):")
        self.current_entry = ttk.Entry(self.current_frame,width=10)
        current = self.koradctl.get_current_set( self.channel )
        print('current:',current)
        self.current_entry.insert(0,str(current))
        self.set_current_button = ttk.Button(self.current_frame, text="Set I", command=self.set_current)
        self.current_label.pack(side=tk.LEFT,padx=5)
        self.current_entry.pack(side=tk.LEFT,padx=5)
        self.set_current_button.pack(side=tk.LEFT,padx=5)

        self.current_readback_label = ttk.Label(self.current_frame, text="I read: ")
        self.current_readback_label.pack(side=tk.LEFT,padx=5)
        self.current_readback = ttk.Label(self.current_frame, text="- A")
        self.current_readback.pack(side=tk.LEFT,padx=5)

        self.onoff_frame = tk.Frame(self,width=self.current_frame.winfo_width())
        self.onoff_frame.pack(side=tk.TOP,pady=5)
        self.output_status_label = ttk.Label(self.onoff_frame, text="On/Off Status")
        self.output_status_label.pack(side=tk.LEFT,padx=5)
        self.output_button = ttk.Button(self.onoff_frame, text="Toggle On/Off", command=self.toggle_output)
        self.output_button.pack(side=tk.LEFT,padx=5)        




    def toggle_output(self):
        if self.koradctl.get_output_onoff( self.channel ):
            self.koradctl.turn_output_off( self.channel )
        else:
            self.koradctl.turn_output_on( self.channel )
        self.get_output()

    def set_voltage(self):
        self.koradctl.set_voltage( float(self.voltage_entry.get()), self.channel )

    def set_current(self):
        self.koradctl.set_current( float(self.current_entry.get()), self.channel )

    def get_voltage(self):
        voltage = self.koradctl.get_voltage( self.channel )
        self.voltage_readback.config(text=str(voltage)+' V')
 
    def get_current(self):
        current = self.koradctl.get_current( self.channel )
        self.current_readback.config(text=str(current)+' A')

    def get_output(self):
        '''
        Check if the output is on or off and update the widgets accordingly.
        If the channel is on but readback and set voltages do not match make Vread red
        otherwise make it green. 
        '''
        voltage_set = float(self.voltage_entry.get())
        voltage_read = self.koradctl.get_voltage( self.channel )
        current_set = float(self.current_entry.get())
        current_read = self.koradctl.get_current( self.channel )
        if self.koradctl.get_output_onoff( self.channel ):
            self.output_button.config(text="Turn OFF")
            self.output_status_label.config(text="Output: ON")
            if abs(voltage_set-voltage_read) > 0.01:
                self.voltage_readback.config(foreground="red")
            else:
                self.voltage_readback.config(foreground="green")
            if current_set - current_read < 0.01:
                self.current_readback.config(foreground="red")
            else:
                self.current_readback.config(foreground="green")
        else:
            self.output_button.config(text="Turn ON")
            self.output_status_label.config(text="Output: OFF")
            self.voltage_readback.config(foreground="black")
            self.current_readback.config(foreground="black")

    def update(self):
        def run_update():
            while True:
                print('updating')
                self.get_voltage()
                self.get_current()
                self.get_output()
                time.sleep(5)
        update_thread = threading.Thread(target=run_update)
        update_thread.daemon = True
        update_thread.start()





if __name__ == '__main__':

    root = tk.Tk()

    root.destroy()

    # use argparse to get the port and channel numbers from the command line
    parser = argparse.ArgumentParser(description='Korad Kontrol')
    parser.add_argument('--port', default='/dev/serial/by-id/usb-Nuvoton_KORAD_USB_Mode_000016E90000-if00',type=str, help='The serial port to use')
    parser.add_argument('--id', default=['1','2','3','4'],nargs='+', help='List of channels')
    args = parser.parse_args()

    app = KonradKontrolWindow( args.port, args.id )
    app.mainloop()

