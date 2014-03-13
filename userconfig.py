# This file contains user-specific settings for qtlab.
# It is run as a regular python script.

# Do not change the following line unless you know what you are doing
config.remove([
            'datadir',
            'startdir',
            'scriptdirs',
            'user_ins_dir',
            'startgui',
            'gnuplot_terminal',
            ])

# QTLab instance name and port for networked operation
config['instance_name'] = 'qtlab_dn6'
config['port'] = 12002

# A list of allowed IP ranges for remote connections
config['allowed_ips'] = (
#     '141.52.95.219', #intdanneau4
#    '145.94.*.*',
)

config['servers'] = (
        '141.52.95.219', #intdanneau4             
)

# Start instrument server to share with instruments with remote QTLab?
config['instrument_server'] = False

## This sets a default location for data-storage
#config['datadir'] = 'C:/data'

## This sets a default directory for qtlab to start in
#config['startdir'] = 'C:/scripts'

## A default script (or list of scripts) to run after qtlab started
config['startscript'] = []      #e.g. 'initscript1.py'

## A default script (or list of scripts) to run when qtlab closes
config['exitscript'] = []       #e.g. ['closescript1.py', 'closescript2.py']

# Add directories containing scripts here. All scripts will be added to the
# global namespace as functions.
config['scriptdirs'] = [
		'C:/scripts',
        'examples/scripts',
#        'd:/scripts',
]

# Add subdirectories of scripts folder
for path,dirs,files in os.walk('C:/scripts'):
	if ".git" in dirs:
		dirs.remove(".git")
		
	for d in dirs:
		config['scriptdirs'].append(d)

print "Scriptdirs:"
print config['scriptdirs']

## This sets a user instrument directory
## Any instrument drivers placed here will take
## preference over the general instrument drivers
#config['user_insdir'] = 'd:/instruments'

## For adding additional folders to the 'systm path'
## so python can find your modules
#import sys
#sys.path.append('d:/folder1')
#sys.path.append('d:/folder2')

# Whether to start the GUI automatically
config['startgui'] = True

# Default gnuplot terminal
#config['gnuplot_terminal'] = 'x11'
#config['gnuplot_terminal'] = 'wxt'
#config['gnuplot_terminal'] = 'windows'

# Enter a filename here to log all IPython commands
config['ipython_logfile'] = ''      #e.g. 'command.log'
