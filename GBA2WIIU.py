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
	parser.add_argument("command", type=str, choices=["extract", "inject"], help="The command you want to use")
	parser.add_argument("ifile", type=str, help="The Wii U VC save file")
	# inject only command
	parser.add_argument("-s", "--save", type=str, help="The save file to inject")
	parser.add_argument("-o", "--ofile", type=str, help="The file to output to")
	args = parser.parse_args()

	args.command = args.command.lower()
	assert isfile(args.ifile), "The input Wii U save file doesn't exist!"
	if args.command == "inject":
		assert args.save, "-s or --save is required for the inject command!"
		assert isfile(args.save), "The save to be injected doesn't exist!"

	# make a copy of the file in memory so we don't touch the original
	with BytesIO(read_file(args.ifile)) as bio:
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
		# I'm just assuming this is the size, I could be wrong...
		(save_size,) = unpack("<I", bio.read(4))
		# seek back to the beginning of the save descriptor
		bio.seek(-0x10, 1)
		# seek to after the save descriptor
		bio.seek(0x80, 1)
		if args.command == "extract":
			print(f"Extracting save @ {hex(bio.tell())}, size {hex(save_size)}...")
			# grab the save data
			save_data = bio.read(save_size)
			# extract it
			write_file(args.ofile if args.ofile else "output.bin", save_data)
		elif args.command == "inject":
			print(f"Injecting save @ {hex(bio.tell())}, size {hex(save_size)}...")
			# read the new save data
			save_data = read_file(args.save)
			assert len(save_data) == save_size, "Save size mismatch!"
			# write the new save data in
			bio.write(save_data)
		# get the result
		data = bio.getvalue()

	# write the data to disk
	write_file(args.ofile if args.ofile else "output.sav", data)

if __name__ == "__main__":
	main()