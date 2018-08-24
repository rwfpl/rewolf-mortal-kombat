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

import os
import argparse
import png
from apng import APNG
from bitreader import BitReader
import mklzw
import mkutils

class ArgFormatter(
	argparse.ArgumentDefaultsHelpFormatter, 
	argparse.RawTextHelpFormatter, 
	argparse.MetavarTypeHelpFormatter):
	pass

def AddBooleanArg(args, arg_name, def_value, help_str):
	args.add_argument(
		arg_name, 
		default=def_value, 
		type=lambda x: (str(x).lower() == 'true'), 
		metavar='true/false', 
		help=help_str)

args = argparse.ArgumentParser(
	description='Mortal Kombat GRA files parser.\nCopyright (c) 2018 ReWolf\nAll rights reserved.\nhttp://blog.rewolf.pl', 
	formatter_class=ArgFormatter)

args.add_argument('input_file', metavar='input_file', type=str)
AddBooleanArg(args, '--apng', def_value=True, help_str='enable/disable APNG generation')
AddBooleanArg(args, '--png', def_value=True, help_str='enable/disable PNG generation')
AddBooleanArg(args, '--raw', def_value=False, help_str='enable/disable RAW pixel dumps')
args.add_argument('--apng_delay', type=int, default=100, help='APNG frame delay in miliseconds')
args.add_argument('--outdir', type=str, default=os.getcwd(), help='output directory')
args = args.parse_args()

filename_no_ext = os.path.splitext(os.path.basename(args.input_file))[0]
out_path = args.outdir
if not os.path.exists(out_path):
	os.makedirs(out_path)

data = open(args.input_file, 'rb').read()
br = BitReader(data)

palette = mkutils.getPalette(br)
print('Number of palette colors:', len(palette), '\n')

file_idx = 0
files = []
while not br.isEnd():
	print('Processing frame nr   :', file_idx)
	cp = br.data_pos
	print('Compressed data offset:', hex(cp))
	width, height, c, compressed_block = mkutils.getCompressedData(br)
	output = mklzw.decompress(compressed_block, c)
	if len(output) == 0:
		print('Decompression error, exiting.')
		break
	print('Compressed data size  :', br.data_pos - cp)
	print('Decompressed data size:', len(output))
	print('Frame width           :', width)
	print('Frame height          :', height)
	print('LZW parameter         :', c)
	
	if args.raw:
		raw_path = os.path.join(out_path, '%s_%002d.data' % (filename_no_ext, file_idx))
		print('Writing RAW pixels    :', raw_path)
		open(raw_path, 'wb').write(bytes(output))
		raw_path = os.path.join(out_path, '%s_%002d.rgb_data' % (filename_no_ext, file_idx))
		print('Writing RAW RGB pixels:', raw_path)
		f = open(raw_path, 'wb')
		for b in bytes(output):
			f.write(bytes(palette[b]))
		f.close()

	if not args.png:
		file_idx += 1
		print()
		continue
	
	file_name = os.path.join(out_path, '%s_%002d.png' % (filename_no_ext, file_idx))
	print('Writing PNG           :', file_name)
	png_array = []
	for y in range(0, height):
		png_array.append([])
		for x in range(0, width):
			png_array[y].append(palette[output[y*width + x]])
	png.from_array(png_array, 'RGB').save(file_name)
	files.append(file_name)
	file_idx += 1
	print()

if len(files) > 1 and args.apng:
	print('Writing APNG animation...')
	print('Number of frames      :', len(files))
	apng_path = os.path.join(out_path, '%s_ani.apng' % filename_no_ext)
	print('File                  : %s' % apng_path)
	APNG.from_files(files, delay=args.apng_delay).save(apng_path)
