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

class rapoo_parser_py_b(gr.sync_block):
	"""
	docstring for block rapoo_parser_py_b
	"""
	def __init__(self, req_pre, filename=None):
		gr.sync_block.__init__(self,
			name="rapoo_parser_py_b",
			in_sig=[numpy.byte],
			out_sig=None)
		
		#const 
		bytes_to_keep=18
		self.set_history(bytes_to_keep*8)
		self.req_pre=req_pre


	# based on http://stackoverflow.com/questions/25239423/crc-ccitt-16-bit-python-manual-calculation/38655469
	def calcCRC(self, message):
		#CRC-16-CITT poly, the CRC sheme used by x/ymodem protocol
		##poly = 0x11021
		poly = 0x1021
		#16bit operation register, initialized to zeros
		##reg = 0xffff
		reg = 0
		#pad the end of the message with the size of the poly
		##message += '\x00\x00' 
		#message+=[0,0] # for lists
		message=numpy.append(message, [0,0]) # for numpy array
		#for each bit in the message
		for byte in message:
			mask = 0x80
			while(mask > 0):
				#left shift by one
				reg<<=1
				#input the next bit from the message into the right hand side of the op reg
				##if ord(byte) & mask:   
				if (byte) & mask:   
					reg += 1
				mask>>=1
				#if a one popped out the left of the reg, xor reg w/poly
				if reg > 0xffff:            
					#eliminate any one that popped out the left
					reg &= 0xffff           
					#xor with the poly, this is the remainder
					reg ^= poly
		return reg
	
	def get_key(self, keyId):
		return {
			14: 'Ctrl',
			23: '1',
			31: '2',
			39: '3',
			47: '4',
			46: '5',
			54: '6',
			55: '7',
			63: '8',
			71: '9',
			79: '0',
			16: 'Q',
			24: 'W',
			32: 'E',
			40: 'R',
			41: 'T',
			49: 'Y',
			48: 'U',
			56: 'I',
			64: 'O',
			72: 'P',
			18: 'A',
			26: 'S',
			34: 'D',
			42: 'F',
			43: 'G',
			51: 'H',
			50: 'J',
			58: 'K',
			66: 'L',
			74: ';',
			20: 'Z',
			28: 'X',
			36: 'C',
			44: 'V',
			45: 'B',
			53: 'N',
			52: 'M',
			60: '<',
			68: '>',
			9: 'Space',
			83: 'AltL',
			85: 'AltR',
			97: 'ShiftL',
			98: 'ShiftR',
			17: 'Tab',
			19: 'Esc',
			92: 'Enter',
			102: 'Delete',
			89: 'Backspace',
			82: 'Fn',
			67: 'Win',
			69: 'Context',
			78: '-',
			62: '=',
			90: '\\',
			30: 'F1',
			38: 'F2',
			33: 'F3',
			35: 'F4',
			15: 'F5',
			59: 'F6',
			65: 'F7',
			70: 'F8',
			94: 'F9',
			95: 'F10',
			91: 'F11',
			93: 'F12',
			99: 'Up',
			108: 'Left',
			101: 'Right',
			109: 'Down',
			73: '[',
			57: ']',
			75: '\''
		}.get(keyId, '?');
	
	def _print_ar(self, ar):
		print ','.join( hex(n)[2:] for n in ar)
		
	def _get_byte(self, i):
		return numpy.packbits( self.stream[self.byte_sync+i*8:self.byte_sync+i*8+8] )[0]
		
	def work(self, input_items, output_items):
		in0 = input_items[0]
		inlen=len(input_items[0])
		#print inlen
		histlen = self.history()
		# len is hist-1 old data and the rest is new data
		
		self.stream=in0;
		
		for i in range(inlen-(histlen-1)): # [0, inlen-histlen]
			self.byte_sync=i
			j=0
			# see if we have preamble end on cur pos
			# take 5 bytes from start
			preamble=False
			if self._get_byte(2)==0xaa and self._get_byte(3)==0xaa and self._get_byte(4)!=0xaa:
				preamble='Short'
				if self._get_byte(0)==0xaa and self._get_byte(1)==0xaa:
					preamble='Long'
			if preamble==False and self.req_pre: # require preamble
				continue
					
			j+=4 # 4 pre candidates and one look ahead
			
			# work with data
			k=0
			# detect ee
			repeat=False # is repeat frame
			if self._get_byte(j+k)==0xee: # also saw 0xce. is error in bit or diff message?
				k+=1
				repeat=True
			# see if we have address 
			if self._get_byte(j+k)==0xd4 and self._get_byte(j+k+1)==0xd9 and self._get_byte(j+k+2)==0x44:
				k+=3
				j+=k;
				k=0
				# debug
				#self._print_ar(hdr_bytes)
				#self._print_ar(data_bytes)
				# check if fixed frame
				if self._get_byte(j+k)==0x4b and self._get_byte(j+k+1)==0x78:
					if preamble: # only relate to "fixed" frames if preamble was ok (otherwise will detect duplicates due to 0xee position)
						#print 'fixed', 'pre', preamble, 'repeat', repeat, hex( self._get_byte(j+k+2) ) # also print byte after 4b78, to see if it is 2a.
						if preamble=='Long':
							print 'a',
						if repeat:
							print '*',
						block=0 # place holder for empty block (to silence ident error)
				else:
					# work with data
					data_bits=in0[(i+j*8+0):(i+j*8+histlen-j*8)] # get rest of bytes
					data_bytes=numpy.packbits(data_bits)
					# data packets
					wh=0x5a # whitening mask
					wh_bytes=data_bytes^wh
					h=wh_bytes[k]
					print 'data', 'pre', preamble, 'repeat', repeat, 'type', hex(h>>4), 'seq', h&0xf
					# handle different data packets
					if h>>4 == 0xf:
						# kb
						#self._print_ar(wh_bytes[k:(k+1+2+2)])
						crcR=self.calcCRC(wh_bytes[k:(k+1+2)])
						crcT=wh_bytes[k+3]+(wh_bytes[k+4]<<8) # first byte is the least significant
						print 'key', self.get_key(wh_bytes[k+2]), wh_bytes[k+2], 'flags', hex(wh_bytes[k+1]), 'crc', crcR==crcT #, hex(crcR),hex(crcT)
					elif h>>4 == 0xc:
						# mouse
						self._print_ar(wh_bytes[k:(k+1+8+2)])
						crcR=self.calcCRC(wh_bytes[k:(k+1+8)])
						crcT=wh_bytes[k+9]+(wh_bytes[k+10]<<8) # first byte is the least significant
						print 'flags', 0, 'key', 0, 'crc', crcR==crcT
			#else: # not adress
				#print 'no address', 'pre', preamble, 'repeat', repeat, hex(data_bytes[k])
		return inlen

