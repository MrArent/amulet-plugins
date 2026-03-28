"""
FrameSort - mc_hgd Block Replacer
Replaces all blocks with the 'mc_hgd' namespace (Mounts of Mayhem: Dungeon Descent)
with minecraft:stone across the ENTIRE world, no selection required.

Install: Place this file in your Amulet plugins/operations folder.
Usage: Open your world in Amulet, go to Operation tab, select "Replace mc_hgd Blocks", click Run.
"""

from amulet.api.block import Block
from amulet.api.level import BaseLevel
from amulet.api.data_types import Dimension
from amulet.api.selection import SelectionGroup
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
import numpy as np

# The namespace we want to remove
TARGET_NAMESPACE = "mc_hgd"

# Replacement block per dimension
DIMENSION_REPLACEMENTS = {
    "minecraft:the_nether": "netherrack",
    "minecraft:the_end":    "end_stone",
}
DEFAULT_REPLACEMENT = "stone"


DIMENSIONS = [
    "minecraft:overworld",
    "minecraft:the_nether",
    "minecraft:the_end",
]


def replace_mc_hgd(
    world: BaseLevel,
    dimension: Dimension,
    selection: SelectionGroup,
    options: dict,
):
    """
    Iterates every chunk in all three dimensions and replaces all mc_hgd
    namespace blocks with the appropriate filler block:
      overworld -> stone, nether -> netherrack, end -> end_stone.
    """

    total_replaced = 0

    for dim in DIMENSIONS:
        if dim not in world.dimensions:
            print(f"[mc_hgd Replacer] Skipping {dim} (not present in this world).")
            continue

        replacement_name = DIMENSION_REPLACEMENTS.get(dim, DEFAULT_REPLACEMENT)
        replacement_block = Block("minecraft", replacement_name)

        all_chunks = list(world.all_chunk_coords(dim))
        total = len(all_chunks)
        replaced_count = 0
        chunk_count = 0

        print(f"[mc_hgd Replacer] [{dim}] Found {total} chunks to scan. Starting...")

        for cx, cz in all_chunks:
            chunk_count += 1

            try:
                chunk = world.get_chunk(cx, cz, dim)
            except (ChunkLoadError, ChunkDoesNotExist):
                continue

            chunk_modified = False
            palette = chunk.block_palette

            mc_hgd_ids = set()
            for block_id, block in enumerate(palette):
                if block.namespace == TARGET_NAMESPACE:
                    mc_hgd_ids.add(block_id)

            if not mc_hgd_ids:
                continue

            replacement_id = palette.get_add_block(replacement_block)

            blocks = chunk.blocks
            for sy in blocks.sub_chunks:
                sub_chunk = blocks.get_sub_chunk(sy)
                mask = np.isin(sub_chunk, list(mc_hgd_ids))
                if np.any(mask):
                    count = int(np.sum(mask))
                    sub_chunk[mask] = replacement_id
                    blocks.add_sub_chunk(sy, sub_chunk)
                    replaced_count += count
                    chunk_modified = True

            if chunk_modified:
                chunk.changed = True

            if chunk_count % 100 == 0:
                print(f"[mc_hgd Replacer] [{dim}] Progress: {chunk_count}/{total} chunks scanned, {replaced_count} blocks replaced so far...")

        print(f"[mc_hgd Replacer] [{dim}] Done! Replaced {replaced_count} blocks with minecraft:{replacement_name}.")
        total_replaced += replaced_count

    print(f"[mc_hgd Replacer] All dimensions complete. Total blocks replaced: {total_replaced}.")
    print("[mc_hgd Replacer] Don't forget to save the world in Amulet (Ctrl+S) before closing!")


export = {
    "name": "Replace mc_hgd Blocks (Whole World)",
    "operation": replace_mc_hgd,
}
