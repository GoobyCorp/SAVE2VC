#!/usr/bin/env python3

from io import BytesIO
from os.path import isfile
from struct import pack, unpack
from argparse import ArgumentParser, FileType

BLOCK_SIZE = 0x1000
SAVE_MAGIC = b"STATRAM0"

def read_file(filename: str) -> bytes:
	with open(filename, "rb") as f:
		data = f.read()
	return data

def write_file(filename: str, data: (bytes, bytearray)) -> None:
	with open(filename, "wb") as f:
		f.write(data)

def bswap(b: (bytes, bytearray), bits: int) -> (bytes, bytearray):
	with BytesIO(b) as bio:
		for i in range(0, len(b), bits // 8):
			data = bio.read(bits // 8)
			bio.seek(-(bits // 8), 1)
			bio.write(bytes(reversed(data)))
		return bio.getvalue()

def bswap16(b: (bytes, bytearray)) -> (bytes, bytearray):
	return bswap(b, 16)

def bswap32(b: (bytes, bytearray)) -> (bytes, bytearray):
	return bswap(b, 32)

def bswap64(b: (bytes, bytearray)) -> (bytes, bytearray):
	return bswap(b, 64)

def gen_statram_desc(size: int) -> bytes:
	return pack("<8s30I", SAVE_MAGIC, size, 0, size, 0, 0, 0, 0, 0, size, 0, 0, 0, 0, 0, 0, 0, size, 0, 0, 0, 0, 0, 0, 0, size, 0, 0, 0, 0, 0)

def main() -> None:
	parser = ArgumentParser(description="A script to migrate saves from GBA to Wii U VC")
	parser.add_argument("command", type=str, choices=["extract", "inject"], help="The command you want to use")
	parser.add_argument("ifile", type=FileType("rb"), help="The Wii U VC save file")
	parser.add_argument("-s", "--save", type=FileType("rb"), help="The save file to inject")
	parser.add_argument("-o", "--ofile", type=str, help="The file to output to")
	parser.add_argument("-e", "--eeprom", action="store_true", help="EEPROM byte swap")
	# parser.add_argument("--disable-errors", action="store_true", help="Disable sanity checks")
	parser.add_argument("-r", "--resize", action="store_true", help="Attempt to resize the STATRAM0 block")
	args = parser.parse_args()

	# make command lowercase
	args.command = args.command.lower()

	# make sure the file to inject is specified
	if args.command == "inject":
		assert args.save, "-s or --save is required for the inject command!"

	# make a copy of the file in memory so we don't touch the original
	with BytesIO(args.ifile.read()) as bio:
		# find the file size
		bio.seek(0, 2)
		size = bio.tell()
		bio.seek(0)
		# iterate through the blocks and find the start magic
		statram0_desc_idx = 0
		for i in range(0, size, BLOCK_SIZE):
			bio.seek(i)
			# found the block, set it to the start
			if bio.read(8) == SAVE_MAGIC:
				bio.seek(i)
				statram0_desc_idx = i
				break
		# find the save size
		bio.seek(12, 1)
		# I'm just assuming this is the size, I could be wrong...
		(save_size,) = unpack("<I", bio.read(4))
		# seek back to the beginning of the save descriptor
		bio.seek(-0x10, 1)
		# seek to after the save descriptor
		bio.seek(0x80, 1)
		# perform commands
		if args.command == "extract":
			print(f"Extracting save @ {hex(bio.tell())}, size {hex(save_size)}...")
			# grab the save data
			save_data = bio.read(save_size)
			# perform EEPROM byte swap if instructed to
			if args.eeprom:
				save_data = bswap64(save_data)
			# extract it
			write_file(args.ofile if args.ofile else "output.sav", save_data)
			# we're done
			return
		elif args.command == "inject":
			print(f"Injecting save @ {hex(bio.tell())}, size {hex(save_size)}...")
			# read the new save data
			save_data = args.save.read()
			# perform EEPROM byte swap if instructed to
			if args.eeprom:
				save_data = bswap64(save_data)
			# allow resizing the save data
			if args.resize:
				print("Attempting resize...")
				tmp = bio.tell()
				bio.seek(statram0_desc_idx)
				bio.write(gen_statram_desc(len(save_data)))
				bio.seek(tmp)
			else:
				assert len(save_data) == save_size, "Save size mismatch!"
			# null the old data incase it was resized
			bio.write((b"\x00" * save_size))
			# seek back to the beginning of the save data
			bio.seek(-save_size, 1)
			# write the new save data in
			bio.write(save_data)
		# get the result
		data = bio.getvalue()

	# only save if injecting
	if args.command == "inject":
		# write the data to disk
		write_file(args.ofile if args.ofile else "output.bin", data)

	# we're done here
	print("Done!")

if __name__ == "__main__":
	main()