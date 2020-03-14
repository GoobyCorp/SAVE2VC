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

def lowercase(s: str) -> str:
	return s.lower()

def main() -> None:
	parser = ArgumentParser(description="A script to migrate saves from GBA to Wii U VC")

	subparsers = parser.add_subparsers(title="commands", dest="command", help="Command help", required=True)

	extract_parser = subparsers.add_parser("extract", help="Extract a game save from a Wii U VC save")
	extract_parser.add_argument("ifile", type=FileType("rb"), help="The Wii U VC save file")

	inject_parser = subparsers.add_parser("inject", help="Inject a game save into a Wii U VC save")
	inject_parser.add_argument("sfile", type=FileType("rb"), help="The game save to inject")
	inject_parser.add_argument("ifile", type=FileType("rb"), help="The Wii U VC save file")

	parser.add_argument("-o", "--ofile", type=str, help="The file to output to")
	parser.add_argument("-e", "--eeprom", action="store_true", help="EEPROM byte swap")
	parser.add_argument("-r", "--resize", action="store_true", help="Attempt to resize the STATRAM0 block")
	args = parser.parse_args()

	# make a copy of the file in memory so we don't touch the original
	with BytesIO(args.ifile.read()) as bio:
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
			save_data = args.sfile.read()
			# perform EEPROM byte swap if instructed to
			if args.eeprom:
				save_data = bswap64(save_data)
			# allow resizing the save data
			if args.resize:
				print("Attempting resize...")
				bio.seek(-0x80, 1)
				bio.write(gen_statram_desc(len(save_data)))
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