# SR830.py, Stanford Research 830 DSP lock-in driver
# Katja Nowack, Stevan Nadj-Perge, Arjan Beukman, Reinier Heeres
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
import visa
import types
import logging

class SR530(Instrument):
    '''
    This is the python driver for the Lock-In SR830 from Stanford Research Systems.

    Usage:
    Initialize with
    <name> = instruments.create('name', 'SR830', address='<GPIB address>',
        reset=<bool>)
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the SR830.

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            reset (bool)     : resets to default values, default=false

        Output:
            None
        '''
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        """
        self.add_parameter('mode',
           flags=Instrument.FLAG_SET,
           type=types.BooleanType)
        """
        self.add_parameter('frequency', type=types.FloatType,
            flags=Instrument.FLAG_GET | Instrument.FLAG_GET_AFTER_SET,
            minval=1e-3, maxval=102e3,
            units='Hz', format='%.04e')
        """
        self.add_parameter('amplitude', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=0.004, maxval=5.0,
            units='V', format='%.04e')
        """
        self.add_parameter('phase', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=-360, maxval=729, units='deg')
        self.add_parameter('X', flags=Instrument.FLAG_GET, units='V', type=types.FloatType)
        self.add_parameter('Y', flags=Instrument.FLAG_GET, units='V', type=types.FloatType)
        #self.add_parameter('R', flags=Instrument.FLAG_GET, units='V', type=types.FloatType)
        self.add_parameter('P', flags=Instrument.FLAG_GET, units='deg', type=types.FloatType)
        self.add_parameter('taupre', type=types.IntType,
            flags=Instrument.FLAG_GETSET,
            format_map={
            1 : "1ms",
            2 : "3ms",
            3 : "10ms",
            4 : "30ms",
            5 : "100ms",
            6 : "300ms",
            7 : "1s",
            8 : "3s",
            9 : "10s",
            10: "30s",
            11: "100s",
            })
        self.add_parameter('taupost', type=types.IntType,
            flags=Instrument.FLAG_GETSET,
            format_map={
            0 : "none",
            1 : "0.1s",
            2 : "1s",
            })

        self.add_parameter('out', type=types.FloatType, channels=(1,2,3,4),
            flags=Instrument.FLAG_GETSET,
            minval=-10.5, maxval=10.5, units='V', format='%.3f')
        self.add_parameter('in', type=types.FloatType, channels=(1,2,3,4),
            flags=Instrument.FLAG_GET,
            minval=-10.5, maxval=10.5, units='V', format='%.3f')

        self.add_parameter('sensitivity', type=types.IntType,
            flags=Instrument.FLAG_GETSET,
            format_map={
            1 : "10nV",
            2 : "20nV",
            3 : "50 nV",
            4 : "100nV",
            5 : "200nV",
            6 : "500nV",
            7 : "1muV",
            8 : "2muV",
            9 : "5muV",
            10 : "10muV",
            11 : "20muV",
            12 : "50muV",
            13 : "100muV",
            14 : "200muV",
            15 : "500muV",
            16 : "1mV",
            17 : "2mV",
            18 : "5mV",
            19 : "10mV",
            20 : "20mV",
            21 : "50mV",
            22 : "100mV",
            23 : "200mV",
            24 : "500mV",
            })

        self.add_function('reset')
        self.add_function('get_all')
        self.add_function('get_xyp')

        if reset:
            self.reset()
        else:
            self.get_all()

    # Functions
    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Resetting instrument')
        self._visainstrument.write('Z')
        self.get_all()

    def get_all(self):
        '''
        Reads all implemented parameters from the instrument,
        and updates the wrapper.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : reading all settings from instrument')
        self.get_sensitivity()
        self.get_taupre()
        self.get_taupost()
        self.get_frequency()
        #self.get_amplitude()
        self.get_phase()
        self.get_X()
        self.get_Y()
        #self.get_R()
        self.get_P()

    def disable_front_panel(self):
        '''
        disables the front panel of the lock-in
        while being in remote control
        '''
        self._visainstrument.write('I 1')

    def auto_phase(self):
        '''
        The "AP"
        command will execute the auto-phase routine.
        This is done by setting the reference phase shift
        with the present phase difference between the
        signal and the reference input. The  output then
        reads zero and the reference display reads the
        signal phase shift. "AP" maximizes X and
        minimizes Y but R is unaffected. The A
        commands may be issued at any time, regardless
        of the DISPLAY setting
        '''
        self._visainstrument.write('AP')

    def enable_front_panel(self):
        '''
        enables the front panel of the lock-in
        while being in remote control
        '''
        self._visainstrument.write('I 0')

    def direct_output(self):
        '''
        select GPIB as interface, not necessary because switch on the back of the instrument is set to GPIB ??
        '''
        #self._visainstrument.write('OUTX 1')

    def read_output(self,output):
        '''
        Read out R,X,Y or phase (P) of the Lock-In

        Input:
            mode (int) :
            1 : "X",
            2 : "Y",
            3 : "R"
            4 : "P"

        '''
        parameters = {
        1 : "QX",  # X 
        2 : "QY",  # Y
        3 : "R",  #R value cant be read out, calculate it! DEACTIVATED
        4 : "P"  #reference phase shift
        }
        self.direct_output()
        if parameters.__contains__(output):
            logging.info(__name__ + ' : Reading parameter from instrument: %s ' %parameters.get(output))
            readvalue = float(self._visainstrument.ask('%s' %parameters.get(output)))
        else:
            print 'Wrong output requested.'
        return readvalue
    
    def get_xyp(self):
        '''
        
        Read out xyp of the Lock In
        '''
       
        readlist = [self.do_get_X(), self.do_get_Y(), self.do_get_P()]
        return readlist
    
    def do_get_X(self):
        '''
        Read out X of the Lock In
        '''
        return self.read_output(1)

    def do_get_Y(self):
        '''
        Read out Y of the Lock In
        '''
        return self.read_output(2)
    """
    def do_get_R(self):
        '''
        Read out R of the Lock In          #R value cant be read out, calculate it! R = X/cos(phi)
        '''
        return self.read_output(3)
    """
    def do_get_P(self):
        '''
        Read out P of the Lock In
        '''
        return self.read_output(4)
    """
    def do_set_frequency(self, frequency):
        '''
        Set frequency of the local oscillator

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting frequency to %s Hz' % frequency)
        self._visainstrument.write('FREQ %e' % frequency)
    """

    def do_get_frequency(self):
        '''
        Get the frequency of the local oscillator

        Input:
            None

        Output:
            frequency (float) : frequency in Hz
        '''
        self.direct_output()
        logging.debug(__name__ + ' : reading frequency from instrument')
        return float(self._visainstrument.ask('F'))
    """
    def do_get_amplitude(self):
        '''
        Get the frequency of the local oscillator

        Input:
            None

        Output:
            frequency (float) : frequency in Hz
        '''
        self.direct_output()
        logging.debug(__name__ + ' : reading frequency from instrument')
        return float(self._visainstrument.ask('SLVL?'))
    """
    """
    def do_set_mode(self,val):
        logging.debug(__name__ + ' : Setting Reference mode to external' )
        self._visainstrument.write('FMOD %d' %val)
    """
    """
    def do_set_amplitude(self, amplitude):
        '''
        Set frequency of the local oscillator

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting amplitude to %s V' % amplitude)
        self._visainstrument.write('SLVL %e' % amplitude)
    """

    def _set_tau(self,type,timeconstant):
        '''
        Set the time constant of the LockIn

        Input:
            time constant (integer) : integer from 0 to 19

        Output:
            None
        '''
        self.direct_output()
        logging.debug(__name__ + ' : setting time constant on instrument to %s,%s'% (type,timeconstant))
        self._visainstrument.write('T %s,%s' % (type,timeconstant) )
        
    def do_set_taupre(self,timeconstant):
        self._set_tau(1,timeconstant)
        
    def do_set_taupost(self,timeconstant):
        self._set_tau(2,timeconstant)
            
    def do_get_taupre(self):
        '''
        Get the time constant of the LockIn

        Input:
            None
        Output:
            time constant (integer) : integer from 0 to 19
        '''

        self.direct_output()
        logging.debug(__name__ + ' : getting time constant on instrument')
        return float(self._visainstrument.ask('T 1'))
        
    def do_get_taupost(self):
        '''
        Get the time constant of the LockIn

        Input:
            None
        Output:
            time constant (integer) : integer from 0 to 19
        '''

        self.direct_output()
        logging.debug(__name__ + ' : getting time constant on instrument')
        return float(self._visainstrument.ask('T 2'))
        
    def do_set_sensitivity(self, sens):
        '''
        Set the sensitivity of the LockIn

        Input:
            sensitivity (string) : e.g. "2nV"

        Output:
            None
        '''
        
        self.direct_output()
        
        logging.debug(__name__ + ' : setting sensitivity on instrument to %s'%(sens))
        self._visainstrument.write('G %s' % sens)

    def do_get_sensitivity(self):
        '''
        Get the sensitivity
            Output:
            sensitivity (integer) : integer from 0 to 26
        '''
        self.direct_output()
        logging.debug(__name__ + ' : reading sensitivity from instrument')
        return float(self._visainstrument.ask('G'))

    def do_get_phase(self):
        '''
        Get the reference phase shift

        Input:
            None

        Output:
            phase (float) : reference phase shift in degree
        '''
        self.direct_output()
        logging.debug(__name__ + ' : reading frequency from instrument')
        return float(self._visainstrument.ask('P'))


    def do_set_phase(self, phase):
        '''
        Set the reference phase shift

        Input:
            phase (float) : reference phase shit in degree

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting the refernce phase shift to %s degree' %phase)
        self._visainstrument.write('P %e' % phase)

    def set_aux(self, output, value):
        '''
        Set the voltage on the aux output
        Input:
            output - number 5,6 (defining which output you are adressing)
            value  - the voltage in Volts
        Output:
            None
        '''
        logging.debug(__name__ + ' : setting the output %(out)i to value %(val).3f' % {'out':output,'val': value})
        self._visainstrument.write('X %s, %s' % (output,value))

    def read_aux(self, output):
        '''
        Query the voltage on the aux output
        Input:
            output - number 1-4 (defining which output you are adressing)
        Output:
            voltage on the output D/A converter
        '''
        logging.debug(__name__ + ' : reading the output %s' %output)
        return float(self._visainstrument.ask('X %s' %output))

    def get_oaux(self, value):
        '''
        Query the voltage on the aux output
        Input:
            output - number 1-4 (defining which output you are adressing)
        Output:
            voltage on the input A/D converter
        '''
        logging.debug(__name__ + ' : reading the input %i' %value)
        return float(self._visainstrument.ask('X %s' %value))

    def do_set_out(self, value, channel):
        '''
        Set output voltage, rounded to nearest mV.
        '''
        self.set_aux(channel, value)
    
    def do_get_out(self, channel):
        '''
        Read output voltage.
        '''
        return self.read_aux(channel)

    def do_get_in(self, channel):
        '''
        Read input voltage, resolution is 1/3 mV.
        '''
        return self.get_oaux(channel)

    def set_bandpassfilter(self,value):
        """
        Sets status of bandpassfilter to on (1) or off(0)
        """
        self._visainstrument.write('B %s' % value)