#! /usr/bin/env python3
import argparse
import dataclasses
import json
import re
from pathlib import Path

from genieutils.datfile import DatFile
from genieutils.tech import Tech
from genieutils.unit import Unit

RES_FOOD = 0
RES_WOOD = 1
RES_STONE = 2
RES_GOLD = 3
ARM_PIERCE = 3

TYPE_MAPPING = {
    10: "Eye Candy",
    15: "Tree (AoK)",
    20: "Animated",
    25: "Doppelganger",
    30: "Moving",
    40: "Actor",
    50: "Superclass",
    60: "Projectile",
    70: "Combatant",
    80: "Building",
    90: "Tree (AoE)"
}

CLASS_MAPPING = [
    "Archer",
    "Artifact",
    "Trade Boat",
    "Building",
    "Civilian",
    "Ocean Fish",
    "Infantry",
    "Berry Bush",
    "Stone Mine",
    "Prey Animal",
    "Predator Animal",
    "Miscellaneous",
    "Cavalry",
    "Siege Weapon",
    "Terrain",
    "Tree",
    "Tree Stump",
    "Healer",
    "Monk",
    "Trade Cart",
    "Transport Boat",
    "Fishing Boat",
    "Warship",
    "Conquistador",
    "War Elephant",
    "Hero",
    "Elephant Archer",
    "Wall",
    "Phalanx",
    "Domestic Animal",
    "Flag",
    "Deep Sea Fish",
    "Gold Mine",
    "Shore Fish",
    "Cliff",
    "Petard",
    "Cavalry Archer",
    "Doppelganger",
    "Bird",
    "Gate",
    "Salvage Pile",
    "Resource Pile",
    "Relic",
    "Monk with Relic",
    "Hand Cannoneer",
    "Two Handed Swordsman",
    "Pikeman",
    "Scout",
    "Ore Mine",
    "Farm",
    "Spearman",
    "Packed Unit",
    "Tower",
    "Boarding Boat",
    "Unpacked Siege Unit",
    "Ballista",
    "Raider",
    "Cavalry Raider",
    "Livestock",
    "King",
    "Misc Building",
    "Controlled Animal"
]


def cpp_round(value: float) -> int | float:
    rounded_int = round(value)
    if abs(rounded_int - value) < 0.0000001:
        return rounded_int
    return round(value, 6)


def read_strings(path: Path) -> dict[int, str]:
    values = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line and line[0].isnumeric():
            items = line.strip().split(maxsplit=1)
            values[int(items[0])] = items[1][1:-1]
    return values


def read_rms_consts(path: Path) -> dict[int, str]:
    values = {}
    pattern = re.compile(r'#const\s+([A-Z_]+)\s+(\d+)')
    active = False
    for line in path.read_text(encoding='utf-8').splitlines():
        if 'OBJECT TYPES' in line or 'DLC_AUTUMNTREE ' in line or 'DLC_BOULDER_A ' in line:
            active = True
        if 'Effect Constants' in line or 'DLC_BAOBABFOREST ' in line or 'DLC_ROCK ' in line:
            active = False
        if active:
            m = pattern.match(line)
            if m:
                if m.group(2) not in values:
                    values[m.group(2)] = m.group(1)
    return values


def should_include_unit(unit_data: dict) -> bool:
    """Filter out units based on specified conditions"""
    # Exclude units with line_of_sight = -1
    if unit_data.get('line_of_sight') == -1:
        return False
    
    # Exclude units with class = "Miscellaneous"
    if unit_data.get('class') == 'Miscellaneous':
        return False
    
    # Exclude units with class = "Relic"
    if unit_data.get('class') == 'Relic':
        return False
    
    # Exclude units with class = "Tree"
    if unit_data.get('class') == 'Tree':
        return False
    
    # Exclude units with class = "Terrain"
    if unit_data.get('class') == 'Terrain':
        return False
    
    # Exclude units with class = "Civilian"
    if unit_data.get('class') == 'Civilian':
        return False
    
    # Exclude units with type = "Eye Candy"
    if unit_data.get('type') == 'Eye Candy':
        return False
    
    # Exclude units with type = "Animated"
    if unit_data.get('type') == 'Animated':
        return False
    
    return True


def should_include_tech(tech_data: dict) -> bool:
    """Filter out technologies based on specified conditions"""
    # Exclude technologies with empty localised_name
    if tech_data.get('localised_name') == '':
        return False
    
    # Exclude technologies with default placeholder names
    name = tech_data.get('name', '')
    if name.startswith('Anarchy +'):
        return False
    
    return True


def get_pierce_armor(unit: Unit) -> int:
    if unit.type_50:
        for a in unit.type_50.armours:
            if a.class_ == ARM_PIERCE:
                return a.amount
    return 0


def unit_data(unit: Unit) -> dict:
    cost = {
        "wood": 0,
        "food": 0,
        "gold": 0,
        "stone": 0,
    }
    if unit.creatable:
        cost = {
            "wood": next((c.amount for c in unit.creatable.resource_costs if c.type == RES_WOOD), 0),
            "food": next((c.amount for c in unit.creatable.resource_costs if c.type == RES_FOOD), 0),
            "gold": next((c.amount for c in unit.creatable.resource_costs if c.type == RES_GOLD), 0),
            "stone": next((c.amount for c in unit.creatable.resource_costs if c.type == RES_STONE), 0),
        }
    return {
        "cost": cost,
        "attack": unit.type_50.displayed_attack if unit.type_50 else 0,
        "melee_armor": unit.type_50.displayed_melee_armour if unit.type_50 else 0,
        "pierce_armor": get_pierce_armor(unit),
        "base_id": unit.base_id,
        "help_converter": unit.language_dll_help - 79000,
        "language_file_name": unit.language_dll_name,
        "language_file_help": unit.language_dll_help,
        "name": unit.name,
        "hit_points": unit.hit_points,
        "line_of_sight": cpp_round(unit.line_of_sight),
        "garrison_capacity": unit.garrison_capacity,
        "type": TYPE_MAPPING.get(unit.type, str(unit.type)),
        "class": CLASS_MAPPING[unit.class_] if unit.class_ < len(CLASS_MAPPING) else str(unit.class_),
        "localised_name": '',
        "rms_const": None,
    }


def civ_data(civ, index: int) -> dict:
    return {
        "id": index,
        "name": civ.name,
        "player_type": civ.player_type,
        "team_bonus_id": civ.team_bonus_id,
        "tech_tree_id": civ.tech_tree_id,
        "localised_name": civ.name,  # Use name as localised_name since no language DLL info
    }


def should_include_civ(civ_data: dict) -> bool:
    """Filter out civilizations based on specified conditions"""
    # Exclude civilizations with empty name
    if civ_data.get('name') == '':
        return False
    
    return True


def tech_data(tech: Tech) -> dict:
    return {
        "cost": {
            "wood": next((c.amount for c in tech.resource_costs if c.type == RES_WOOD), 0),
            "food": next((c.amount for c in tech.resource_costs if c.type == RES_FOOD), 0),
            "gold": next((c.amount for c in tech.resource_costs if c.type == RES_GOLD), 0),
            "stone": next((c.amount for c in tech.resource_costs if c.type == RES_STONE), 0),
        },
        "help_converter": tech.language_dll_help - 79000,
        "language_file_name": tech.language_dll_name,
        "language_file_help": tech.language_dll_help,
        "name": tech.name,
        "localised_name": '',
    }


def process(dat_file: Path, strings_file: Path, rms_file: Path | None, target: Path) -> None:
    units_data = []
    buildings_data = []
    techs_data = []
    civs_data = []
    
    strings = read_strings(strings_file)
    rms = read_rms_consts(rms_file) if rms_file else {}
    dat = DatFile.parse(dat_file)
    
    for unit in dat.civs[0].units:
        if unit:
            unit_info = unit_data(unit)
            if should_include_unit(unit_info):
                # Separate units and buildings based on type
                if unit_info.get('type') == 'Building':
                    buildings_data.append(unit_info)
                else:
                    units_data.append(unit_info)
    
    for tid, tech in enumerate(dat.techs):
        tech_info = tech_data(tech)
        techs_data.append(tech_info)
    
    # Extract civilization data
    for index, civ in enumerate(dat.civs):
        civ_info = civ_data(civ, index)
        if should_include_civ(civ_info):
            civs_data.append(civ_info)

    # Apply localization to all data
    all_data = {'units': units_data, 'buildings': buildings_data, 'techs': techs_data, 'civs': civs_data}
    for objtype in ('units', 'buildings', 'techs'):
        for obj in all_data[objtype]:
            strings_key = obj['language_file_name']
            obj['localised_name'] = strings.get(strings_key, '')
            if objtype in ('units', 'buildings'):
                obj['rms_const'] = rms.get(str(obj['base_id']), None)
    
    # Civs already have their names, no localization needed
    
    # Remove objects with empty localised_name after localization
    filtered_units = [obj for obj in all_data['units'] if obj.get('localised_name') != '']
    filtered_buildings = [obj for obj in all_data['buildings'] if obj.get('localised_name') != '']
    filtered_techs = [obj for obj in all_data['techs'] if obj.get('localised_name') != '' and 'Placeholder' not in obj.get('name', '')]
    filtered_civs = [obj for obj in all_data['civs'] if obj.get('localised_name') != '']
    
    # Write to separate files
    base_dir = target.parent
    units_file = base_dir / 'units.json'
    buildings_file = base_dir / 'buildings.json'
    techs_file = base_dir / 'techs.json'
    civs_file = base_dir / 'civs.json'
    
    units_file.write_text(json.dumps(filtered_units, indent='\t', ensure_ascii=False, sort_keys=False))
    buildings_file.write_text(json.dumps(filtered_buildings, indent='\t', ensure_ascii=False, sort_keys=False))
    techs_file.write_text(json.dumps(filtered_techs, indent='\t', ensure_ascii=False, sort_keys=False))
    civs_file.write_text(json.dumps(filtered_civs, indent='\t', ensure_ascii=False, sort_keys=False))


def main():
    parser = argparse.ArgumentParser(
        prog='update-de-data.py',
        description='Update data files for DE and RoR',
    )
    parser.add_argument('aoe2_dir', type=Path)
    args = parser.parse_args()

    de_dat = args.aoe2_dir / 'resources' / '_common' / 'dat' / 'empires2_x2_p1.dat'
    de_strings = args.aoe2_dir / 'resources' / 'en' / 'strings' / 'key-value' / 'key-value-strings-utf8.txt'
    de_rms = args.aoe2_dir / 'resources' / '_common' / 'drs' / 'gamedata_x2' / 'random_map.def'
    de_target = Path(__file__).parent.resolve().parent / 'data' / 'units_buildings_techs.de.json'

    ror_dat = args.aoe2_dir / 'modes' / 'Pompeii' / 'resources' / '_common' / 'dat' / 'empires2_x2_p1.dat'
    ror_strings = args.aoe2_dir / 'modes' / 'Pompeii' / 'resources' / 'en' / 'strings' / 'key-value' / 'key-value-pompeii-strings-utf8.txt'
    ror_target = Path(__file__).parent.resolve().parent / 'data' / 'units_buildings_techs.ror.json'

    process(de_dat, de_strings, de_rms, de_target)
    
    # Only process Pompeii DLC if files exist
    if ror_dat.exists() and ror_strings.exists():
        process(ror_dat, ror_strings, None, ror_target)


if __name__ == '__main__':
    main()
