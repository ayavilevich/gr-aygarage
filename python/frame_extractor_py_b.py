#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 Arik Yavilevich.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

class frame_extractor_py_b(gr.sync_block):
    """
    docstring for block frame_extractor_py_b
    """
    def __init__(self, prelen, postlen, byteoff):
        gr.sync_block.__init__(self,
            name="frame_extractor_py_b",
            in_sig=[numpy.byte],
            out_sig=None)

        self.prelen=prelen
        self.postlen=postlen
        self.byteoff=byteoff
        self.set_history(prelen+postlen)
        self.globlen=0


    def work(self, input_items, output_items):
        in0 = input_items[0]
        histlen = self.history() # prelen+postlen
        inlen = len(in0)
        # len is hist-1 old data and the rest is new data

        # signal processing here
        #print inlen, histlen
        for i in range(inlen-(histlen-1)): # [0, inlen-histlen]
            if in0[i+self.prelen] & 2:
                #print i, in0[i+self.prelen]
                globpos=self.globlen+i-(histlen-1) # convert i to point in new part of buf
                bits=in0[i:(i+self.prelen+self.postlen)] & 1
                # get byte bound and pack
                aligned_bits=bits[(self.prelen+self.byteoff)%8:]
                hbytes=','.join( hex(n)[2:] for n in numpy.packbits(aligned_bits) )
                
                print globpos, bits, hbytes

        self.globlen += inlen - (histlen-1)
        return len(input_items[0])

