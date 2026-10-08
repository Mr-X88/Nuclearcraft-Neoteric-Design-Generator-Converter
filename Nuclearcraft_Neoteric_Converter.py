import json
import os

# Exaktes Block ID Mapping für NuclearCraft Neoteric (1.18.2 / 1.20.1)
BLOCK_MAP = {
    "FuelCell": "nuclearcraft:fission_reactor_solid_fuel_cell",
    "Casing": "nuclearcraft:fission_reactor_casing",
    "Glass": "nuclearcraft:fission_reactor_glass",
    "Water": "nuclearcraft:water_heat_sink",
    "Redstone": "nuclearcraft:redstone_heat_sink",
    "Quartz": "nuclearcraft:quartz_heat_sink",
    "Iron": "nuclearcraft:iron_heat_sink",
    "Glowstone": "nuclearcraft:glowstone_heat_sink",
    "Lapis": "nuclearcraft:lapis_heat_sink",
    "Gold": "nuclearcraft:gold_heat_sink",
    "Diamond": "nuclearcraft:diamond_heat_sink",
    "Helium": "nuclearcraft:liquid_helium_heat_sink",
    "Enderium": "nuclearcraft:enderium_heat_sink",
    "Cryotheum": "nuclearcraft:cryotheum_heat_sink",
    "Tin": "nuclearcraft:tin_heat_sink",
    "Copper": "nuclearcraft:copper_heat_sink",
    "Boron": "nuclearcraft:boron_heat_sink",
    "Lithium": "nuclearcraft:lithium_heat_sink",
    "Obsidian": "nuclearcraft:obsidian_heat_sink",
    "Lead": "nuclearcraft:lead_heat_sink",
    "Emerald": "nuclearcraft:emerald_heat_sink",
    "Netherite": "nuclearcraft:netherite_heat_sink",
    "Graphite": "nuclearcraft:graphite_block"
}

def konvertieren():
    input_file = "reactor.json"
    output_file_json = "nc_reactor_bg2.json"
    output_file_txt = "nc_reactor_bg2_clipboard.txt"

    print("==================================================")
    print(" NuclearCraft zu Building Gadgets 2 Konverter")
    print("==================================================\n")

    if not os.path.exists(input_file):
        print(f"[FEHLER] Die Datei '{input_file}' wurde nicht gefunden!")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            planner_data = json.load(f)
    except Exception as e:
        print(f"[FEHLER] Beim Lesen der JSON-Datei: {e}")
        return

    compressed = planner_data.get("CompressedReactor", {})
    raw_positions = []
    required_items = {}

    for key, coords in compressed.items():
        if key in BLOCK_MAP:
            block_id = BLOCK_MAP[key]
            count = len(coords)
            required_items[block_id] = required_items.get(block_id, 0) + count

            for c in coords:
                x = c.get("X", c.get("x", 0))
                y = c.get("Y", c.get("y", 0))
                z = c.get("Z", c.get("z", 0))
                raw_positions.append((x, y, z, block_id))
        else:
            print(f"[WARNUNG] Unbekannter Blocktyp: '{key}'")

    if not raw_positions:
        print("[FEHLER] Keine gültigen Blöcke in der Reaktor-Datei gefunden.")
        return

    # Normalisierung der Koordinaten auf den Ursprung (0, 0, 0)
    min_x = min(p[0] for p in raw_positions)
    max_x = max(p[0] for p in raw_positions)
    min_y = min(p[1] for p in raw_positions)
    max_y = max(p[1] for p in raw_positions)
    min_z = min(p[2] for p in raw_positions)
    max_z = max(p[2] for p in raw_positions)

    grid = {}
    for x, y, z, block_id in raw_positions:
        grid[(x - min_x, y - min_y, z - min_z)] = block_id

    end_x = max_x - min_x
    end_y = max_y - min_y
    end_z = max_z - min_z

    # Palette aufbauen
    palette = []
    palette_map = {}

    total_positions = (end_x + 1) * (end_y + 1) * (end_z + 1)
    if len(grid) < total_positions:
        palette_map["minecraft:air"] = 0
        palette.append({"Name": "minecraft:air"})

    for block_id in required_items.keys():
        if block_id not in palette_map:
            palette_map[block_id] = len(palette)
            palette.append({"Name": block_id})

    # 3D-Gitter verarbeiten (X -> Y -> Z)
    statelist_indices = []
    for x in range(end_x + 1):
        for y in range(end_y + 1):
            for z in range(end_z + 1):
                block_id = grid.get((x, y, z), "minecraft:air")
                statelist_indices.append(palette_map[block_id])

    blockstatemap_str = json.dumps(palette, separators=(',', ':'))
    statelist_str = f"[I;{','.join(map(str, statelist_indices))}]"

    # WICHTIG: X, Y, Z müssen zwingend GROSSGESCHRIEBEN sein für NBT!
    state_pos_array_list_str = (
        f"{{blockstatemap:{blockstatemap_str},"
        f"endpos:{{X:{end_x},Y:{end_y},Z:{end_z}}},"
        f"startpos:{{X:0,Y:0,Z:0}},"
        f"statelist:{statelist_str}}}"
    )

    bg2_structure = {
        "name": "NC Neoteric Fission Reactor",
        "statePosArrayList": state_pos_array_list_str,
        "requiredItems": required_items
    }

    # 1. Lesbare JSON-Datei speichern
    with open(output_file_json, "w", encoding="utf-8") as f:
        json.dump(bg2_structure, f, indent=2)

    # 2. Einzeilige Clipboard-Datei ohne Umbrüche für das direkte Einfügen im Game
    single_line_json = json.dumps(bg2_structure, separators=(',', ':'))
    with open(output_file_txt, "w", encoding="utf-8") as f:
        f.write(single_line_json)

    print(f" -> Fertig! Es wurden {len(raw_positions)} Blöcke verarbeitet.")
    print(f" -> Dimensionen: {end_x + 1} x {end_y + 1} x {end_z + 1} Blöcke.")
    print(f"\n[IMPORT HINWEIS]:")
    print(f" Kopiere den Inhalt aus '{output_file_txt}' und klicke im BG2 Template Manager auf 'Paste'.")

if __name__ == "__main__":
    try:
        konvertieren()
    except Exception as e:
        print(f"\n[FEHLER]: {e}")
    
    print("\n")
    input("Drücke Enter zum Beenden...")
