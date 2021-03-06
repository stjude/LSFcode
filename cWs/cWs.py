#!/usr/bin/env python
##########################################################################
#    cWs: Convolved waiters for load balancing of Spectrum Scale systems
#    Copyright (C) 2016 J. Robert Michael, PhD
##########################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import time
import math

def bashexec( cmd ):
    import subprocess
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    outlines = out.splitlines()
    errlines = err.splitlines()
    return outlines, errlines

def get_tot_wait_time():
    cmd = '/usr/lpp/mmfs/bin/mmdiag --waiters'
    (outlines, errlines) = bashexec(cmd)
    tot_wait_time = 0 
    for line in outlines:
        if( 'waiting' in line ):
            tline = line.split('waiting')[1]
            if( 'seconds' in line ):
                t = float(tline.split('seconds')[0])
            elif( 'minutes' in line):
                t = 60.0*float(tline.split('minutes')[0])
            elif( 'hours' in line):
                t = 60.0*60.0*float(tline.split('hours')[0])

            tot_wait_time += t

    return tot_wait_time

if __name__=="__main__":
    import socket
    import sys

    if( 'hpc' in socket.gethostname() ):
        while( True ):
            print "1 cWs 0.0"
            time.sleep(10)
    else:
        ### define variables
        sleep_time = 15 ### time in seconds to sleep. Should be the same as in lsf.shared
        nmins_keep = 10 ### how long back to look for convolution

        nitems = int(math.ceil(nmins_keep*60/sleep_time)) ### how many items to keep in record

        ws = [ 1.0/float(abs(nitems-i)) for i in reversed(range(nitems)) ] ### weight vector for convolution
        Ws = []
        while( True ):
            if( len(Ws) > nitems ):
                del Ws[-1]
            Ws.insert(0, get_tot_wait_time())
            den = sum(ws[:len(Ws)])
            cWs = float( sum( [w*W for (w,W) in zip(ws, Ws)] ))/den
            print "1 cWs %.2f"%(cWs)
            sys.stdout.flush()
            time.sleep(10)
