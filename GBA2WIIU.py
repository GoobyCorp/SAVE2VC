#!/usr/bin/env python3

from io import BytesIO
from struct import unpack
from os.path import isfile
from argparse import ArgumentParser

BLOCK_SIZE = 0x1000
SAVE_MAGIC = b"STATRAM0"

def read_file(filename: str) -> bytes:
	with open(filename, "rb") as f:
		data = f.read()
	return data

def write_file(filename: str, data: (bytes, bytearray)) -> None:
	with open(filename, "wb") as f:
		f.write(data)

def main() -> None:
	parser = ArgumentParser(description="A script to migrate saves from GBA to Wii U VC")
	parser.add_argument("fw", type=str, help="The Wii U save file")
	parser.add_argument("fg", type=str, help="The GBA save file")
	parser.add_argument("-o", "--ofile", type=str, help="The file to output to")
	args = parser.parse_args()

	assert isfile(args.fw), "The input Wii U save file doesn't exist!"
	assert isfile(args.fg), "The input GBA save file doesn't exist!"

	# make a copy of the file in memory so we don't touch the original
	with BytesIO(read_file(args.fw)) as bio:
		# find the file size
		bio.seek(0, 2)
		size = bio.tell()
		bio.seek(0)

		# iterate through the blocks and find the start magic
		for i in range(0, size, BLOCK_SIZE):
			bio.seek(i)
			# found the block, set it to the start
			if bio.read(8) == SAVE_MAGIC:
				bio.seek(i)
				break

		# find the save size
		bio.seek(12, 1)
		# I'm just assuming this is the size, I could be wrong
		(save_size,) = unpack("<I", bio.read(4))
		# seek back to the beginning of the save magic
		bio.seek(-0x10, 1)
		# seek to after the save descriptor
		bio.seek(0x80, 1)
		# grab the save data
		save_data = bio.read(save_size)
		# back it up
		write_file("gba.bin", save_data)
		# seek to the beginning of the save data
		bio.seek(-save_size, 1)
		# read the new save data
		save_data = read_file(args.fg)
		assert len(save_data) == save_size, "Save size mismatch!"
		# write the new save data in
		bio.write(save_data)
		# get the result
		data = bio.getvalue()

	# write the data to disk
	write_file(args.ofile if args.ofile else "output.sav", data)

if __name__ == "__main__":
	main()