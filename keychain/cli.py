from main import *
import argparse as ap
import os
import os.path


parser = ap.ArgumentParser()

parser.add_argument(
    "file",
)
parser.add_argument(
    "-f","--force",action="store_true"
)

args = parser.parse_args()

f = args.file
force = args.force

if os.path.isfile(f):
    print(f"{f} already exists")
    if force:
        new_seed = generate_seed()
        new_seed.save(f)
        print(f"{f} overwritten")
else:
    new_seed = generate_seed()
    new_seed.save(f)
    print(f"new_seed_phrase saved to {f}")




