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


def replace_mc_hgd(
    world: BaseLevel,
    dimension: Dimension,
    selection: SelectionGroup,
    options: dict,
):
    """
    Iterates every chunk in the current dimension and replaces all mc_hgd
    namespace blocks with the appropriate filler block:
      overworld -> stone, nether -> netherrack, end -> end_stone.
    """

    replacement_name = DIMENSION_REPLACEMENTS.get(dimension, DEFAULT_REPLACEMENT)
    replacement_block = Block("minecraft", replacement_name)

    # Get all chunk coordinates in the world
    all_chunks = list(world.all_chunk_coords(dimension))
    total = len(all_chunks)
    replaced_count = 0
    chunk_count = 0

    print(f"[mc_hgd Replacer] Found {total} chunks to scan. Starting...")

    for cx, cz in all_chunks:
        chunk_count += 1

        try:
            chunk = world.get_chunk(cx, cz, dimension)
        except (ChunkLoadError, ChunkDoesNotExist):
            continue

        chunk_modified = False

        # Get the block palette for this chunk
        palette = chunk.block_palette

        # Find all palette entries that belong to mc_hgd namespace
        mc_hgd_ids = set()
        for block_id, block in enumerate(palette):
            if block.namespace == TARGET_NAMESPACE:
                mc_hgd_ids.add(block_id)

        # If no mc_hgd blocks found in this chunk's palette, skip it
        if not mc_hgd_ids:
            continue

        # Get the replacement block ID in this chunk's palette
        replacement_id = palette.get_add_block(replacement_block)

        # Iterate through all sub-chunks and replace matching block IDs
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

        # Progress update every 100 chunks
        if chunk_count % 100 == 0:
            print(f"[mc_hgd Replacer] Progress: {chunk_count}/{total} chunks scanned, {replaced_count} blocks replaced so far...")

    print(f"[mc_hgd Replacer] Done! Scanned {total} chunks, replaced {replaced_count} mc_hgd blocks with minecraft:{replacement_name}.")
    print("[mc_hgd Replacer] Don't forget to save the world in Amulet (Ctrl+S) before closing!")


export = {
    "name": "Replace mc_hgd Blocks (Whole World)",
    "operation": replace_mc_hgd,
}
