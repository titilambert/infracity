# https://gorillasun.de/blog/Rectangle-Packing-An-incredibly-difficult-problem
# pip install rectpack
# Using algo: MaxRectsBlsf

from rectpack import newPacker, PackingMode
import rectpack.maxrects as maxrects


def arrange_town(town):
    """Arrange districts in a town.

    Using MaxRectsBlsf, the town tries to seem like a square.
    """
    packer = newPacker(mode=PackingMode.Offline, pack_algo=maxrects.MaxRectsBlsf, rotation=1)

    for district in town.districts.values():
        packer.add_rect(district.dimensions["x"], district.dimensions["y"], district.name)

    packer.add_bin(1000, 1000)
    packer.pack()
    return packer.rect_list()


def arrange_island(island):
    """Arrange towns on a island.

    Using MaxRectsBlsf, the island tries to seem like a square.
    """
    packer = newPacker(mode=PackingMode.Offline, pack_algo=maxrects.MaxRectsBlsf, rotation=0)

    for town in island.towns.values():
        if not town.dimensions["x"]:
            continue
        packer.add_rect(town.dimensions["x"], town.dimensions["y"], town.name)

    packer.add_bin(10000, 10000)
    packer.pack()
    return packer.rect_list()
