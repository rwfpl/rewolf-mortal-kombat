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

MULT = 255.0/31
def convert15to24bitRGB(r, g, b):
	return int(round(r*MULT)), int(round(g*MULT)), int(round(b*MULT))


def getCompressedData(br):
	# HACK: skip unknown number of padding 0 bytes
	b = 0
	while b == 0:
		b = br.getBits(8)
	width = b | (br.getBits(8) << 8)
	height = br.getWord()

	c = br.getBits(8)

	blocks = []
	while not br.isEnd():
		block_size = br.getBits(8)	
		if block_size == 0:
			break
		block = br.getBytes(block_size)
		blocks.append(block)
	return width, height, c, b''.join(blocks)


def getPalette(br):
	palette = []
	record_num = br.getWord()
	for _ in range(0, record_num):
		record_size = br.getWord()
		for _ in range(0, record_size):
			c = br.getWord()
			palette.append(convert15to24bitRGB((c >> 10) & 0x1F, (c >> 5) & 0x1F, c & 0x1F))
	return palette
