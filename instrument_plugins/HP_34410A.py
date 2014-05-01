# x_HP_34401A.py driver for HP 34401A Digital Multimeter
# Thomas Watson <tfwatson15@gmail.com>
# Based on the Keithley_2001.py driver.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from instrument import Instrument
import visa
import types
import logging
import numpy
import re

import qt

def bool_to_str(val):
    '''
Function to convert boolean to 'ON' or 'OFF'
'''
    if val == True:
        return "ON"
    else:
        return "OFF"

class x_HP_34401A(Instrument):
    '''
This is the driver for the HP 34401A Multimeter
#still needs a bit of debugging

Usage:
Initialize with
<name> = instruments.create('<name>', 'x_HP_34401A',
address='<GBIP address>',
reset=<bool>,
change_display=<bool>,
change_autozero=<bool>)
'''

    def __init__(self, name, address, reset=False,
        change_display=False, change_autozero=False):
        '''
Initializes the HP_34401A, and communicates with the wrapper.

Input:
name (string) : name of the instrument
address (string) : GPIB address
reset (bool) : resets to default values
change_display (bool) : If True (default), automatically turn off
display during measurements.
change_autozero (bool) : If True (default), automatically turn off
autozero during measurements.
Output:
None
'''
        # Initialize wrapper functions
        logging.info('Initializing instrument HP_34401A')
        Instrument.__init__(self, name, tags=['physical', 'measure'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self._modes = ['VOLT:AC', 'VOLT', 'CURR:AC', 'CURR', 'RES',
            'FRES', 'TEMP', 'FREQ']
        self._change_display = change_display
        self._change_autozero = change_autozero
        self._trigger_sent = False

        # Add parameters to wrapper
        self.add_parameter('range',
            flags=Instrument.FLAG_GETSET,
            units='', minval=0.01, maxval=100, type=types.FloatType)
        self.add_parameter('trigger_count',
            flags=Instrument.FLAG_GETSET,
            units='#', type=types.IntType)
        self.add_parameter('trigger_delay',
            flags=Instrument.FLAG_GETSET,
            units='s', minval=0, maxval=3600, type=types.FloatType)
        self.add_parameter('trigger_source',
            flags=Instrument.FLAG_GETSET,
            units='')
        self.add_parameter('mode',
            flags=Instrument.FLAG_GETSET,
            type=types.StringType, units='')
        self.add_parameter('resolution',
            flags=Instrument.FLAG_GETSET,
            units='', minval = 3e-7, maxval=1e-4, type=types.FloatType)
        self.add_parameter('readval', flags=Instrument.FLAG_GET,
            units='AU',
            type=types.FloatType,
            tags=['measure'])
        self.add_parameter('nplc',
            flags=Instrument.FLAG_GETSET,
            units='#', type=types.FloatType, minval=0.02, maxval=100)
        self.add_parameter('display', flags=Instrument.FLAG_GETSET,
            type=types.BooleanType)
        self.add_parameter('autozero', flags=Instrument.FLAG_GETSET,
            type=types.BooleanType)
        self.add_parameter('autorange',
            flags=Instrument.FLAG_GETSET,
            units='',
            type=types.BooleanType)

        # Add functions to wrapper
        self.add_function('set_mode_volt_ac')
        self.add_function('set_mode_volt_dc')
        self.add_function('set_mode_curr_ac')
        self.add_function('set_mode_curr_dc')
        self.add_function('set_mode_res')
        self.add_function('set_mode_fres')
        self.add_function('set_mode_freq')
        self.add_function('set_range_auto')
        self.add_function('reset')
        self.add_function('get_all')

        self.add_function('read')

        self.add_function('send_trigger')
        self.add_function('fetch')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        if reset:
            self.reset()
        else:
            self.get_all()
            self.set_defaults()

# --------------------------------------
# functions
# --------------------------------------

    def reset(self):
        '''
Resets instrument to default values

Input:
None

Output:
None
'''
        logging.debug('Resetting instrument')
        self._visainstrument.write('*RST')
        self.get_all()

    def set_defaults(self):
        '''
Set to driver defaults:
Output=data only
Mode=Volt:DC
Range=10 V
Resolution 1e-5

'''

        self.set_mode_volt_dc()
        self.set_range(10)
        self.set_resolution(1e-5)

    def get_all(self):
        '''
Reads all relevant parameters from instrument

Input:
None

Output:
None
'''
        logging.info('Get all relevant data from device')
        self.get_mode()
        self.get_range()
        self.get_trigger_count()
        self.get_trigger_delay()
        self.get_trigger_source()
        self.get_nplc()
        self.get_display()
        self.get_autozero()
        self.get_autorange()

# Link old read and readlast to new routines:
    # Parameters are for states of the machnine and functions
    # for non-states. In principle the reading of the Keithley is not
    # a state (it's just a value at a point in time) so it should be a
    # function, technically. The GUI, however, requires an parameter to
    # read it out properly, so the reading is now done as if it is a
    # parameter, and the old functions are redirected.

    def read(self):
        '''
Old function for read-out, links to get_readval()
'''
        logging.debug('Link to get_readval()')
        return self.get_readval()


    def send_trigger(self): #needs debugging
        '''
Send trigger to HP, use when triggering is not continous.
'''
        self._visainstrument.write('INIT')
        self._trigger_sent = True


    def fetch(self): #needs debugging
        '''
Get data at this instance, not recommended, use get_readlastval.
Use send_trigger() to trigger the device.
Note that Readval is not updated since this triggers itself.
'''
        trigger_status = False
        if self._trigger_sent and (not trigger_status):
            logging.debug('Fetching data')
            reply = self._visainstrument.ask('FETCH?')
            self._trigger_sent = False
            return float(reply[0:15])
        elif (not self._trigger_sent) and (not trigger_status):
            logging.warning('No trigger sent, use send_trigger')
        else:
            logging.error('Triggering is on continous!')

    def set_mode_volt_ac(self):
        '''
Set mode to AC Voltage

Input:
None

Output:
None
'''
        logging.debug('Set mode to AC Voltage')
        self.set_mode('VOLT:AC')

    def set_mode_volt_dc(self):
        '''
Set mode to DC Voltage

Input:
None

Output:
None
'''
        logging.debug('Set mode to DC Voltage')
        self.set_mode('VOLT')

    def set_mode_curr_ac(self):
        '''
Set mode to AC Current

Input:
None

Output:
None
'''
        logging.debug('Set mode to AC Current')
        self.set_mode('CURR:AC')

    def set_mode_curr_dc(self):
        '''
Set mode to DC Current

Input:
None

Output:
None
'''
        logging.debug('Set mode to DC Current')
        self.set_mode('CURR')

    def set_mode_res(self):
        '''
Set mode to Resistance

Input:
None

Output:
None
'''
        logging.debug('Set mode to Resistance')
        self.set_mode('RES')

    def set_mode_fres(self):
        '''
Set mode to 'four wire Resistance'

Input:
None

Output:
None
'''
        logging.debug('Set mode to "four wire resistance"')
        self.set_mode('FRES')


    def set_mode_freq(self):
        '''
Set mode to Frequency

Input:
None

Output:
None
'''
        logging.debug('Set mode to Frequency')
        self.set_mode('FREQ')

    def set_range_auto(self, mode=None):
        '''
Old function to set autorange, links to set_autorange()
'''
        logging.debug('Redirect to set_autorange')
        self.set_autorange(True)


# --------------------------------------
# parameters
# --------------------------------------

    def do_get_readval(self, ignore_error=False):
        '''
Aborts current trigger and sends a new trigger
to the device and reads float value.
Do not use when trigger mode is 'CONT'
Instead use readlastval

Input:
ignore_error (boolean): Ignore trigger errors, default is 'False'

Output:
value(float) : currrent value on input
'''

        logging.debug('Read current value')
        text = self._visainstrument.ask('READ?')
        self._trigger_sent = False
        text = re.sub('N.*','',text)
            
        return float(text)


    def do_set_range(self, val, mode=None):
        '''
Set range to the specified value for the
designated mode. If mode=None, the current mode is assumed

Input:
val (float) : Range in specified units
mode (string) : mode to set property for. Choose from self._modes

Output:
None
'''
        
        logging.debug('Set range to %s' % val)
        self._set_func_par_value(mode, 'RANG', val)

    def do_get_range(self, mode=None):
        '''
Get range for the specified mode.
If mode=None, the current mode is assumed.

Input:
mode (string) : mode to set property for. Choose from self._modes

Output:
range (float) : Range in the specified units
'''
        logging.debug('Get range')
        return float(self._get_func_par(mode, 'RANG'))

    def do_set_nplc(self, val, mode=None, unit='APER'):
        '''
Set integration time to the specified value in Number of Powerline Cycles.
To set the integrationtime in seconds, use set_integrationtime().
Note that this will automatically update integrationtime as well.
If mode=None the current mode is assumed

Input:
val (float) : Integration time in nplc.
mode (string) : mode to set property for. Choose from self._modes.

Output:
None
'''
        mode = self.get_mode(query=False)
        if mode in ('VOLT', 'CURR', 'RES', 'FRES'):
            logging.debug('Set integration time to %s PLC' % val)
            self._set_func_par_value(mode, 'NPLC', val)
        else:
            logging.info('Cant set NPLC in this mode')
        
    def do_get_nplc(self, mode=None, unit='APER'):
        '''
Get integration time in Number of PowerLine Cycles.
To get the integrationtime in seconds, use get_integrationtime().
If mode=None the current mode is assumed

Input:
mode (string) : mode to get property of. Choose from self._modes.

Output:
time (float) : Integration time in PLCs
'''
        mode = self.get_mode(query=False)
        if mode in ('VOLT', 'CURR', 'RES', 'FRES'):
            logging.debug('Read integration time in PLCs')
            return float(self._get_func_par(mode, 'NPLC'))
        else:
            return float(0)

    def do_set_resolution(self, val, mode = None):
        '''
Set resolution.
If mode=None the current mode is assumed

Input:
val (float) : Resolution.
mode (string) : mode to set property for. Choose from self._modes.

Output:
None
'''
        mode = self.get_mode(query=False)
        if mode in ('VOLT' ,'VOLT:AC','CURR:AC', 'CURR', 'RES', 'FRES'):
            logging.debug('Set resolution to %s' % val)
            self._set_func_par_value(mode, 'RES', val)
        else:
            logging.info('Cant set resolution in this mode')
        

    def do_get_resolution(self, mode = None):
        '''
Get resolution
Input:
mode (string) : mode to get property of. Choose from self._modes.

Output:
resolution (float) :
'''

        mode = self.get_mode(query=False)
        if mode in ('VOLT' ,'VOLT:AC','CURR:AC', 'CURR', 'RES', 'FRES'):
            logging.debug('Get resolution')
            return float(self._get_func_par(mode, 'RES'))
        else:
            return float(0)
        

    def do_set_trigger_count(self, val):
        '''
Set trigger count
if val>9999 count is set to INF

Input:
val (int) : trigger count

Output:
None
'''
        logging.debug('Set trigger count to %s' % val)
        if val > 9999:
            val = 'INF'
        self._set_func_par_value('TRIG', 'COUN', val)

    def do_get_trigger_count(self):
        '''
Get trigger count

Input:
None

Output:
count (int) : Trigger count
'''
        logging.debug('Read trigger count from instrument')
        ans = self._get_func_par('TRIG', 'COUN')
        try:
            ret = int(float(ans))
        except:
            ret = 0

        return ret

    def do_set_trigger_delay(self, val):
        '''
Set trigger delay to the specified value

Input:
val (float) : Trigger delay in seconds

Output:
None
'''
        logging.debug('Set trigger delay to %s' % val)
        self._set_func_par_value('TRIG', 'DEL', val)

    def do_get_trigger_delay(self):
        '''
Read trigger delay from instrument

Input:
None

Output:
delay (float) : Delay in seconds
'''
        logging.debug('Get trigger delay')
        return float(self._get_func_par('TRIG', 'DEL'))

    def do_set_trigger_source(self, val):
        '''
Set trigger source

Input:
val (string) : Trigger source

Output:
None
'''
        logging.debug('Set Trigger source to %s' % val)
        self._set_func_par_value('TRIG', 'SOUR', val)

    def do_get_trigger_source(self):
        '''
Read trigger source from instrument

Input:
None

Output:
source (string) : The trigger source
'''
        logging.debug('Getting trigger source')
        return self._get_func_par('TRIG', 'SOUR')

    def do_set_mode(self, mode):
        '''
Set the mode to the specified value

Input:
mode (string) : mode to be set. Choose from self._modes

Output:
None
'''
        logging.debug('Set mode to %s', mode)
        if mode in self._modes:
            string = 'SENS:FUNC "%s"' % mode
            self._visainstrument.write(string)

            if mode.startswith('VOLT'):
                self._change_units('V')
            elif mode.startswith('CURR'):
                self._change_units('A')
            elif mode.startswith('RES'):
                self._change_units('Ohm')
            elif mode.startswith('FREQ'):
                self._change_units('Hz')

        else:
            logging.error('invalid mode %s' % mode)

        # Get all values again because some paramaters depend on mode
        self.get_all()

    def do_get_mode(self):

        '''
Read the mode from the device

Input:
None

Output:
mode (string) : Current mode
'''
        string = 'SENS:FUNC?'
        logging.debug('Getting mode')
        ans = self._visainstrument.ask(string)
        return ans.strip('"')

    def do_get_display(self):
        '''
Read the staturs of diplay

Input:
None

Output:
True = On
False= Off
'''
        logging.debug('Reading display from instrument')
        reply = self._visainstrument.ask('DISP?')
        return bool(int(reply))

    def do_set_display(self, val):
        '''
Switch the diplay on or off.

Input:
val (boolean) : True for display on and False for display off

Output

'''
        logging.debug('Set display to %s' % val)
        val = bool_to_str(val)
        self._visainstrument.write('DISP %s' % val)
        #return self._set_func_par_value('DISP',val)

    def do_get_autozero(self):
        '''
Read the staturs of the autozero function

Input:
None

Output:
reply (boolean) : Autozero status.
'''
        logging.debug('Reading autozero status from instrument')
        reply = self._visainstrument.ask(':ZERO:AUTO?')
        return bool(int(reply))

    def do_set_autozero(self, val):
        '''
Switch the diplay on or off.

Input:
val (boolean) : True for display on and False for display off

Output

'''
        logging.debug('Set autozero to %s' % val)
        val = bool_to_str(val)
        return self._visainstrument.write('SENS:ZERO:AUTO %s' % val)

    def do_set_autorange(self, val, mode=None):
        '''
Switch autorange on or off.
If mode=None the current mode is assumed

Input:
val (boolean)
mode (string) : mode to set property for. Choose from self._modes.

Output:
None
'''
        logging.debug('Set autorange to %s ' % val)
        val = bool_to_str(val)
        self._set_func_par_value(mode, 'RANG:AUTO', val)

    def do_get_autorange(self, mode=None):
        '''
Get status of averaging.
If mode=None the current mode is assumed

Input:
mode (string) : mode to set property for. Choose from self._modes.

Output:
result (boolean)
'''
        logging.debug('Get autorange')
        reply = self._get_func_par(mode, 'RANG:AUTO')
        return bool(int(reply))


# --------------------------------------
# Internal Routines
# --------------------------------------

    def _change_units(self, unit):
        self.set_parameter_options('readval', units=unit)
    
        
    def _determine_mode(self, mode):
        '''
Return the mode string to use.
If mode is None it will return the currently selected mode.
'''
        logging.debug('Determine mode with mode=%s' % mode)
        if mode is None:
            mode = self.get_mode(query=False)
        if mode not in self._modes and mode not in ('INIT', 'TRIG', 'SYST', 'DISP'):
            logging.warning('Invalid mode %s, assuming current' % mode)
            mode = self.get_mode(query=False)
        return mode

    def _set_func_par_value(self, mode, par, val):
        '''
For internal use only!!
Changes the value of the parameter for the function specified

Input:
mode (string) : The mode to use
par (string) : Parameter
val (depends) : Value

Output:
None
'''
        mode = self._determine_mode(mode)
        string = ':%s:%s %s' % (mode, par, val)
        logging.debug('Set instrument to %s' % string)
        self._visainstrument.write(string)

    def _get_func_par(self, mode, par):
        '''
For internal use only!!
Reads the value of the parameter for the function specified
from the instrument

Input:
func (string) : The mode to use
par (string) : Parameter
:
Output:
val (string) :
'''
        mode = self._determine_mode(mode)
        string = ':%s:%s?' % (mode, par)
        ans = self._visainstrument.ask(string)
        logging.debug('ask instrument for %s (result %s)' % \
            (string, ans))
        return ans

    def _measurement_start_cb(self, sender):
        '''
Things to do at starting of measurement
'''
        if self._change_display:
            self.set_display(False)
            #Switch off display to get stable timing
        if self._change_autozero:
            self.set_autozero(False)
            #Switch off autozero to speed up measurement

    def _measurement_end_cb(self, sender):
        '''
Things to do after the measurement
'''
        if self._change_display:
            self.set_display(True)
        if self._change_autozero:
            self.set_autozero(True)