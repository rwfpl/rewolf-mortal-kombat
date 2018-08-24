'''
 Mortal Kombat GRA files parser
 
 Copyright (c) 2018 ReWolf
 http://blog.rewolf.pl/
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from bitreader import BitReader

class LzwState:
	def __init__(self, c):
		self.c = c
		self.M_CLR = 1 << c
		self.M_NEW = self.M_CLR + 2
		self.M_EOD = self.M_CLR + 1
		self.default_req_bits = c + 1

	def clear(self):
		self.next_code = self.M_NEW
		self.req_bits = self.default_req_bits
		self.next_shift = 1 << self.default_req_bits
		self.finchar = -1
		self.oldcode = -1

def decompress(compressed_data, c):
	br = BitReader(compressed_data)
	state = LzwState(c)
	state.clear()

	d = {}
	htab = {}
	output = []
	output2 = []

	while True:
		if br.isEnd():
			return []
		cur_code = br.getBits(state.req_bits)
		incode = cur_code
		if cur_code == state.M_EOD:
			break
		if cur_code == state.M_CLR:
			state.clear()
		else:
			if cur_code == state.next_code:
				cur_code = state.oldcode
				output.append(state.finchar)
			while cur_code >= state.M_CLR:
				if cur_code not in htab:
					return []
				output.append(htab[cur_code])
				cur_code = d[cur_code + 1]
			state.finchar = cur_code
			while True:
				output2.append(cur_code)
				if not output:
					break
				cur_code = output.pop()
			if state.next_code < 4096 and state.oldcode != -1:
				d[state.next_code + 1] = state.oldcode
				htab[state.next_code] = state.finchar
				state.next_code += 1
				if state.next_code >= state.next_shift:
					if state.req_bits < 12:
						state.req_bits += 1
						state.next_shift = 1 << state.req_bits
			state.oldcode = incode
	return bytes(output2)
