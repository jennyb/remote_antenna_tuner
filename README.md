# remote_antenna_tuner
Pi Pico W providing a web page controlling stepper motors connected to a remote manual ATU
Remote ATUs ( antenna tunung units ) for amateur radio give the advantage of a minimal loss 50R connection from the radio to the remote antenna tuner
The Antenna tuner will then match the 50R cable to the complex impedance of the antenna
There are many automatic remote ATUs on the market, but in my experience they do not find the best match, will try to auto tune during an SSB transmission and produce RFI being powered on all the time
This, at its simplest, is a pi pico, running from power fed down the centre of the coax, serving a web page allowing the operator to rotate a variable capacitor
At its most complex, a manual ATU with kno
The power is then removed once the antenna has been matched.
