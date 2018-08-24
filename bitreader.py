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

class BitReader:
	def __init__(self, data):
		self.data = data
		self.data_pos = 0
		self.fillCache()

	def bitMask(self, n):
		return (1 << n) - 1

	def isEnd(self):
		return self.data_pos == len(self.data) and self.bits_len == 0
		
	def fillCache(self):
		self.bits = 0
		self.bits_len = 0
		cur = 0		
		while cur < 8 and self.data_pos < len(self.data):
			self.bits |= (self.data[self.data_pos] << self.bits_len)
			self.bits_len += 8
			self.data_pos += 1
			cur += 1
		if self.isEnd():
			return -1
		return self.bits_len

	def getBits(self, n):
		r = 0
		if n <= self.bits_len:
			self.bits_len -= n
			r = self.bits & self.bitMask(n)
			self.bits >>= n
		else:
			r = self.bits
			blen = self.bits_len
			if self.fillCache() == -1:
				return -1
			r |= (self.getBits(n - blen) << blen)
		return r
	
	def getWord(self):
		return self.getBits(16)
		
	def getBytes(self, n):
		return bytes([self.getBits(8) for _ in range(0, n)])