#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
import re
import unicodedata
import pandas as pd

def find_column(columns, keyword):
    keyword = keyword.lower()
    for col in columns:
        if keyword in str(col).lower():
            return col
    return None

def safe_val(row, col):
    if not col or col not in row:
        return ''
    v = row[col]
    return '' if pd.isna(v) else str(v).strip()

# --- ÚJ: SZÖVEG TISZTÍTÓ A VÁLTOZÓNEVEKHEZ ---
def sanitize_name(text):
    """
    Ékezetmentesít és eltávolítja a speciális karaktereket, 
    hogy érvényes NML változónevet kapjunk.
    Példa: "Ikarus 280 (csuklós)" -> "IKARUS_280_CSUKLOS"
    """
    if not text: return "EMPTY"
    # Ékezetmentesítés (Á -> A)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Minden nem betű/szám karaktert alulvonásra cserélünk
    text = re.sub(r'[^a-zA-Z0-9]', '_', text)
    # Dupla alulvonások takarítása és nagybetűsítés
    return re.sub(r'_+', '_', text).strip('_').upper()

# --- MÓDOSÍTOTT STRING OPTIMALIZÁLÓ ---
def build_string_maps(rows, cm):
    """
    Kigyűjti az egyedi szövegeket, és a tartalmuk alapján 
    generál nekik fix STR_ID-t.
    """
    def create_map(col_key, prefix):
        unique_vals = sorted(list(set(safe_val(r, cm[col_key]) for r in rows if safe_val(r, cm[col_key]))))
        # Itt történik a varázslat: a tartalom lesz az ID része
        return {val: f"STR_{prefix}_{sanitize_name(val)}" for val in unique_vals}

    m_map  = create_map('TextManufacturer', 'MFR')
    t_map = create_map('TextType', 'T1')
    s1_map = create_map('TextSType1', 'S1')
    s2_map = create_map('TextSType2', 'S2')
    o1_map = create_map('TextOther1', 'O1')
    o2_map = create_map('TextOther2', 'O2')
    l_map  = create_map('LiveryText', 'LIV')

    return m_map, t_map, s1_map, s2_map, o1_map, o2_map, l_map


def generate_nml(row, cm, maps):
    m_map, t_map, s1_map, s2_map, o1_map, o2_map, l_map = maps

    # Értékek lekérése (pontosan úgy, ahogy az eredeti kódodban volt)
    Fuel          = safe_val(row, cm['Fuel'])
    ItemID        = safe_val(row, cm['ItemID'])
    Color         = safe_val(row, cm['Color'])
    MDate         = safe_val(row, cm['MDate'])
    MPeroid       = safe_val(row, cm['MPeroid'])
    VLife         = safe_val(row, cm['VLife'])
    Reli          = safe_val(row, cm['Reli'])
    LoadingSpeed  = safe_val(row, cm['LoadingSpeed'])
    PurchaseRow   = safe_val(row, cm['PurchasePrice'])
    MaintenanceRow = safe_val(row, cm['Maintenance'])
    Speed         = safe_val(row, cm['Speed'])
    Power         = safe_val(row, cm['Power'])
    Weight        = safe_val(row, cm['Weight'])
    Capacity      = safe_val(row, cm['Capacity'])
    Comfort       = safe_val(row, cm['Comfort'])
    Hossz1        = safe_val(row, cm['Hossz1'])
    Hossz2        = safe_val(row, cm['Hossz2'])
    Hossz3        = safe_val(row, cm['Hossz3'])
    Hossz4        = safe_val(row, cm['Hossz4'])
    Hossz5        = safe_val(row, cm['Hossz5'])
    Hossz6        = safe_val(row, cm['Hossz6'])
    Pos1          = safe_val(row, cm['Pos1'])
    Pos2          = safe_val(row, cm['Pos2'])
    Pos3          = safe_val(row, cm['Pos3'])
    PFolder       = safe_val(row, cm['PFolder'])
    Usage         = safe_val(row, cm['Usage'])
    Flag          = safe_val(row, cm['Flag'])

    # String ID-k kikeresése az optimalizált térképből
    m_id  = m_map.get(safe_val(row, cm['TextManufacturer']), "STR_EMPTY")
    t_id = t_map.get(safe_val(row, cm['TextType']), "STR_EMPTY")
    s1_id = s1_map.get(safe_val(row, cm['TextSType1']), "STR_EMPTY")
    s2_id = s2_map.get(safe_val(row, cm['TextSType2']), "STR_EMPTY")
    o1_id = o1_map.get(safe_val(row, cm['TextOther1']), "STR_EMPTY")
    o2_id = o2_map.get(safe_val(row, cm['TextOther2']), "STR_EMPTY")
    l_id  = l_map.get(safe_val(row, cm['LiveryText']), "STR_EMPTY")

    # kerekített számok
    try: PurchasePrice = str(round(float(PurchaseRow or 0)))
    except: PurchasePrice = PurchaseRow
    try: Maintenance = str(round(float(MaintenanceRow or 0)))
    except: Maintenance = MaintenanceRow

    # szín és zászló logika
    Alapszin = '// ' if Color == 'CC1' else ''
    if 'CC' in Color:
        FlagCC = 'ROADVEH_FLAG_2CC, '
        Recolor = ''
    else:
        FlagCC = ''
        Recolor = 'colour_mapping:\tPALETTE_IDENTITY;'

    # badges mappelés
    badge_fuel = {
        'diesel':       ', "power/diesel"',
        'hybrid':       ', "power/steam"',
        'cng':          ', "power/naturgas"',
        'electric':     ', "power/battery"',
        'petrol':       ', "power/diesel"',
        'hydrogen':     ', "power/hydrogen"',
    }
    BadgeFuel = badge_fuel.get(Fuel, '')

    badge_flag = {
        'CC':           ', "flag/flag_CC"',
        'Europe':       ', "flag/europe"',
        'Austria':      ', "flag/AT"',
        'Australia':    ', "flag/AU"',
        'Canada':       ', "flag/CA"',
        'Czech':        ', "flag/CZ"',
        'France':       ', "flag/FR"',
        'Germany':      ', "flag/DE"',
        'United Kingdom':', "flag/GB"',
        'Hungary':      ', "flag/HU"',
        'Romania':      ', "flag/RO"',
        'Russia':       ', "flag/RU"',
        'Slovenia':     ', "flag/SI"',
        'Slovakia':     ', "flag/SK"',
        'Switzerland':  ', "flag/CH"',
        'USA':          ', "flag/US"',
    }
    BadgeFlag = badge_flag.get(Flag, '')

    badge_usage = {
        'City':      ', "usage/city"',
        'Suburb':    ', "usage/suburb"',
        'Regional':  ', "usage/regional"',
        'Intercity': ', "usage/intercity"',
        'Tourist':   ', "usage/tourist"',
    }
    BadgeUsage = badge_usage.get(Usage, '')

    # --- GRAFIKA ÉS CSUKLÓ LOGIKA (EREDETI MÁSOLATA) ---
    cs_graph2, cs_graph3, cs_graph4, cs_graph5, cs_graph6 = [], [], [], [], []
    
    pspr1 = [f"\t\tpurchase:            ss_{ItemID}_{Color}_purchase;"]
    spr1 = [f"spritegroup sg_{ItemID}_{Color} {{	loaded:  [ss_{ItemID}_{Color}];	loading: [ss_{ItemID}_{Color}_loading];}}"]
    spr2, spr3 = [], []
    cs_graph1 = [f"\tsg_{ItemID}_{Color};"] # grafika switch

    if float(Hossz3 or 0) > 0:
        pspr1 = [f"\t\tpurchase:            ss_{ItemID}_{Color}_a_purchase;"]
        spr1 = [f"spritegroup sg_{ItemID}_{Color}_a {{	loaded:  [ss_{ItemID}_{Color}_a];	loading: [ss_{ItemID}_{Color}_a_loading];}}"]
        spr2 = [f"spritegroup sg_{ItemID}_{Color}_b {{	loaded:  [ss_{ItemID}_{Color}_b];	loading: [ss_{ItemID}_{Color}_b_loading];}}"]

    if float(Hossz5 or 0) > 0:
        spr3 = [f"spritegroup sg_{ItemID}_{Color}_c {{	loaded:  [ss_{ItemID}_{Color}_c];	loading: [ss_{ItemID}_{Color}_c_loading];}}"]


    if float(Hossz2 or 0) > 0:
        cs_graph1 = ["\tss_toldat;"] # grafika switch
        cs_graph2 = [f"\t1: sg_{ItemID}_{Color};"] # grafika switch
        if float(Hossz3 or 0) > 0:
            cs_graph2 = [f"\t1: sg_{ItemID}_{Color}_a;"] # grafika switch
            cs_graph3 = [f"\t2: sg_{ItemID}_{Color}_b;"] # grafika switch
            if float(Hossz4 or 0) > 0:
                cs_graph3 = ["\t2: ss_toldat;"] # grafika switch
                cs_graph4 = [f"\t3: sg_{ItemID}_{Color}_b;"] # grafika switch
                if float(Hossz5 or 0) > 0:
                    cs_graph5 = [f"\t4: sg_{ItemID}_{Color}_c;"] # grafika switch
                    if float(Hossz6 or 0) > 0:
                        cs_graph5 = ["\t4: ss_toldat;"] # grafika switch
                        cs_graph6 = [f"\t5: sg_{ItemID}_{Color}_c;"] # grafika switch
            else:
                if float(Hossz5 or 0) > 0:
                    cs_graph4 = [f"\t3: sg_{ItemID}_{Color}_c;"] # grafika switch
                    if float(Hossz6 or 0) > 0:
                        cs_graph4 = ["\t3: ss_toldat;"] # grafika switch
                        cs_graph5 = [f"\t4: sg_{ItemID}_{Color}_c;"] # grafika switch
            
    else:
        if float(Hossz3 or 0) > 0:
            cs_graph1 = [f"\tsg_{ItemID}_{Color}_a;"] # grafika switch
            cs_graph2 = [f"\t1: sg_{ItemID}_{Color}_b;"] # grafika switch
            if float(Hossz4 or 0) > 0:
                cs_graph2 = ["\t1: ss_toldat;"] # grafika switch
                cs_graph3 = [f"\t2: sg_{ItemID}_{Color}_b;"] # grafika switch
                if float(Hossz5 or 0) > 0:
                    cs_graph4 = [f"\t3: sg_{ItemID}_{Color}_c;"] # grafika switch
                    if float(Hossz6 or 0) > 0:
                        cs_graph4 = ["\t3: ss_toldat;"] # grafika switch
                        cs_graph5 = [f"\t4: sg_{ItemID}_{Color}_c;"] # grafika switch
            else:
                if float(Hossz5 or 0) > 0:
                    cs_graph3 = [f"\t2: sg_{ItemID}_{Color}_c;"] # grafika switch
                    if float(Hossz6 or 0) > 0:
                        cs_graph3 = ["\t2: ss_toldat;"] # grafika switch
                        cs_graph4 = [f"\t3: sg_{ItemID}_{Color}_c;"] # grafika switch
                

    csuk1 = []
    if float(Hossz2 or Hossz3 or 0) > 0:
        csuk1 = [
            "// Csukló item",
            f"item(FEAT_ROADVEHS, item_{ItemID}_{Color}_t) {{",
            f"\tproperty {{",
            "\t\tname:							string(STR_BUG);",
            "\t\tclimates_available:			bitmask(NO_CLIMATE);",
            "\t\tintroduction_date:				date(4999999,01,01);",
            "\t\tcargo_allow_refit:				[PASS,TOUR];",
            "\t\tloading_speed:					0;",
            "\t\tcost_factor:					0;",
            "\t\trunning_cost_factor:			0;",
            "\t\tsprite_id:						SPRITE_ID_NEW_ROADVEH;",
            f"\t\tmisc_flags:					bitmask({FlagCC}ROADVEH_FLAG_SPRITE_STACK);",
            "\t\trefit_cost:					0;",
            "\t\trunning_cost_base:				RUNNING_COST_NONE;",
            "\t\tpower:							0 kW;",
            "\t\tweight:						0 ton;",
            "\t\tcargo_capacity:				0;",
            "\t\tcargo_age_period:				0;",
            "\t}",
            "\tgraphics {",
            f"\t\tdefault:						sw_{ItemID}_{Color};",
            f"\t\t{Recolor} // Cégszín deaktiválás, ha valós színű jármű",
            f"\t\tlength:						sw_{ItemID}_{Color}_length;",
            "\t}",
            "}",
        ]

    length_cases = []
    if float(Hossz2 or 0) > 0:
        length_cases.append(f"\t1: return {Hossz2};")
        if float(Hossz3 or 0) > 0: length_cases.append(f"\t2: return {Hossz3};")
        if float(Hossz4 or 0) > 0:
            length_cases.append(f"\t3: return {Hossz4};")
            if float(Hossz5 or 0) > 0: length_cases.append(f"\t4: return {Hossz5};")
            if float(Hossz6 or 0) > 0: length_cases.append(f"\t5: return {Hossz6};")
        else:
            if float(Hossz5 or 0) > 0: length_cases.append(f"\t3: return {Hossz5};")
            if float(Hossz6 or 0) > 0: length_cases.append(f"\t4: return {Hossz6};")
            
    else:
        if float(Hossz3 or 0) > 0: length_cases.append(f"\t1: return {Hossz3};")
        if float(Hossz4 or 0) > 0:
            length_cases.append(f"\t2: return {Hossz4};")
            if float(Hossz5 or 0) > 0: length_cases.append(f"\t3: return {Hossz5};")
            if float(Hossz6 or 0) > 0: length_cases.append(f"\t4: return {Hossz6};")
        else:
            if float(Hossz5 or 0) > 0: length_cases.append(f"\t2: return {Hossz5};")
            if float(Hossz6 or 0) > 0: length_cases.append(f"\t3: return {Hossz6};")

    articu_parts = []
    if float(Hossz2 or 0) > 0:
        articu_parts.append(f"\t1: item_{ItemID}_{Color}_t;")
        if float(Hossz3 or 0) > 0: articu_parts.append(f"\t2: item_{ItemID}_{Color}_t;")
        if float(Hossz4 or 0) > 0:
            articu_parts.append(f"\t3: item_{ItemID}_{Color}_t;")
            if float(Hossz5 or 0) > 0: articu_parts.append(f"\t4: item_{ItemID}_{Color}_t;")
            if float(Hossz6 or 0) > 0: articu_parts.append(f"\t5: item_{ItemID}_{Color}_t;")
        else:
            if float(Hossz5 or 0) > 0: articu_parts.append(f"\t3: item_{ItemID}_{Color}_t;")
            if float(Hossz6 or 0) > 0: articu_parts.append(f"\t4: item_{ItemID}_{Color}_t;")
    else:
        if float(Hossz3 or 0) > 0: articu_parts.append(f"\t1: item_{ItemID}_{Color}_t;")
        if float(Hossz4 or 0) > 0:
            articu_parts.append(f"\t2: item_{ItemID}_{Color}_t;")
            if float(Hossz5 or 0) > 0: articu_parts.append(f"\t3: item_{ItemID}_{Color}_t;")
            if float(Hossz6 or 0) > 0: articu_parts.append(f"\t4: item_{ItemID}_{Color}_t;")
        else:
            if float(Hossz5 or 0) > 0: articu_parts.append(f"\t2: item_{ItemID}_{Color}_t;")
            if float(Hossz6 or 0) > 0: articu_parts.append(f"\t3: item_{ItemID}_{Color}_t;")
            

    # --- NML ÖSSZEÁLLÍTÁSA ---
    lines = [f"// ---------- {ItemID}_{Color}", ""]
    lines.append("/*még kellhet")
    lines.extend(pspr1)
    lines.append("*/")
    lines.append("")
    lines.extend(spr1)
    if spr2:
        lines.append("")
        lines.extend(spr2)
    if spr3:
        lines.append("")
        lines.extend(spr3)
    lines.append("")
    lines.append("// Játékban grafika")    
    lines.append(f"switch (FEAT_ROADVEHS, SELF, sw_{ItemID}_{Color}, position_in_consist ) {{")
    lines.extend(cs_graph2)
    lines.extend(cs_graph3)
    lines.extend(cs_graph4)
    lines.extend(cs_graph5)
    lines.extend(cs_graph6)
    lines.extend(cs_graph1)
    lines.append("}")
    lines.append("")
    lines.append("// Csuklosítás")
    lines.append(f"switch (FEAT_ROADVEHS, SELF, sw_{ItemID}_{Color}_articulated, extra_callback_info1) {{")
    lines.append(f"\t0: item_{ItemID}_{Color};")
    lines.extend(articu_parts)
    lines.append("\tCB_RESULT_NO_MORE_ARTICULATED_PARTS;")
    lines.append("}")
    lines.append("")
    lines.append("// Modelhossz")
    lines.append(f"switch (FEAT_ROADVEHS, SELF, sw_{ItemID}_{Color}_length, position_in_consist) {{")
    lines.extend(length_cases)
    lines.append(f"    return {Hossz1};")
    lines.append("}")
    lines.append("")
    
    # --- ÚJ: OPTIMALIZÁLÓ SZÖVEG SWITCH ---
    lines.append("// Szövegek")
    lines.append(f"switch(FEAT_ROADVEHS, SELF, sw_{ItemID}_{Color}_names, (extra_callback_info1 >> 8) & 0xFFFF) {{")
    lines.append(f"\t1: return string(STR_GEN_LIVERY, string({l_id})); // Almenü 1 név")
    lines.append(f"\treturn CB_RESULT_NO_TEXT;")
    lines.append("}")
    lines.append("")
    lines.append(f"switch(FEAT_ROADVEHS, SELF, sw_{ItemID}_{Color}_texts, extra_callback_info1 & 0xFF) {{")
    lines.append(f"\t0x11: return string(STR_GEN_INFO, string({m_id}), string({t_id}), string({o1_id})); // Jármű infóban név (Gyártó-Típus-Ajtó)")
    lines.append(f"\t0x20: sw_{ItemID}_{Color}_names; // Vásárlási lista név")
    lines.append(f"\t0x21: return string(STR_GEN_NAME, string({m_id}), string({t_id}), string({s1_id}), string({s2_id})); // Elővásárlási név")
    lines.append(f"\treturn CB_RESULT_NO_TEXT;")
    lines.append("}")
    lines.append("")

    lines.append("// Item")
    lines.append(f"item(FEAT_ROADVEHS, item_{ItemID}_{Color}) {{")
    lines.append("\tproperty {")
    lines.append(f"\t\tname:                string(STR_GEN_NAME, string({m_id}), string({t_id}), string({s1_id}), string({s2_id}));")
    lines.append("\t\tclimates_available:  bitmask(CLIMATE_TEMPERATE, CLIMATE_ARCTIC, CLIMATE_TROPICAL);")
    lines.append(f"\t\tintroduction_date:   date({MDate},01,01);")
    lines.append(f"\t\tmodel_life:          {MPeroid};")
    lines.append(f"\t\tvehicle_life:        {VLife};")
    lines.append(f"\t\treliability_decay:   {Reli};")
    lines.append("\t\tcargo_allow_refit:   [PASS,TOUR];")
    lines.append(f"\t\tloading_speed:       {LoadingSpeed or 0};")
    lines.append("\t\tsprite_id:           SPRITE_ID_NEW_ROADVEH;")
    lines.append(f"\t\tspeed:               {Speed} km/h;")
    lines.append(f"\t\tmisc_flags:          bitmask({FlagCC}ROADVEH_FLAG_SPRITE_STACK);")
    lines.append(f"\t\trefit_cost:          0;")
    lines.append("\t\trunning_cost_base:   RUNNING_COST_ROADVEH;")
    lines.append(f"\t\tpower:               {Power} kW;")
    lines.append(f"\t\tweight:              {Weight} ton;")
    lines.append(f"\t\tcargo_capacity:      {Capacity};")
    lines.append(f"\t\tcargo_age_period:    {Comfort};")
    lines.append("\t\tsound_effect:        SOUND_DEPARTURE_MODERN_BUS;")
    lines.append(f"\t\tbadges:              [\"type/bus\"{BadgeFuel}{BadgeFlag}{BadgeUsage}];")
    lines.append(f"\t\t{Alapszin}variant_group:             item_{ItemID}_CC1;")
    lines.append("\t}")
    lines.append("\tgraphics {")
    lines.append(f"\t\tdefault:             sw_{ItemID}_{Color};")
    lines.append(f"\t\t{Recolor}    // Cégszín deaktiválás, ha valós színű jármű")
    lines.extend(pspr1)
    lines.append(f"\t\tarticulated_part:    sw_{ItemID}_{Color}_articulated;")
    lines.append(f"\t\tlength:              sw_{ItemID}_{Color}_length;")
    lines.append(f"\t\tcost_factor:         {PurchasePrice} * parapuco;")
    lines.append(f"\t\trunning_cost_factor: {Maintenance} * pararuco;")
    lines.append(f"\t\tadditional_text:     string(STR_GEN_DATA, {LoadingSpeed or 0}, string({s2_id}), string({o2_id}), string({o1_id}));")
    lines.append(f"\t\tname:                sw_{ItemID}_{Color}_texts; // Vásárlási almenü switch")
    lines.append("\t}")
    lines.append("}")
    if csuk1: lines.extend(csuk1)
    lines.append(f"// ---------- {ItemID}_{Color} --- End")
    lines.append("")
    lines.append("")
    return "\n".join(lines)

def generate_lng(rows, cm, maps):
    m_map, t_map, s1_map, s2_map, o1_map, o2_map, l_map = maps
    lines = [""]
    # A közös sablonok (színekkel és formázással az eredeti kérésed szerint)
    lines.append("STR_GEN_DATA :Loading speed: {GOLD}{COMMA}{BLACK}{}{GOLD}----------{}{BLACK}Type: {GOLD}{STRING}, {STRING}, {STRING}{BLACK}")
    lines.append("STR_GEN_NAME :{STRING} {STRING} {STRING} {STRING}")
    lines.append("STR_GEN_LIVERY :{STRING} livery")
    lines.append("STR_GEN_INFO :{STRING} {LTBLUE}- {STRING}{BLACK}")
    
    def add_section(name, d):
        if d:
            lines.append(f"\n# --- {name} ---")
            for k, v in d.items(): lines.append(f"{v:<30} :{k}")
    
    add_section("Manufacturers", m_map)
    add_section("Type", t_map)
    add_section("Sub1", s1_map)
    add_section("Sub2", s2_map)
    add_section("Other1", o1_map)
    add_section("Other2", o2_map)
    add_section("Liveries", l_map)
    return "\n".join(lines)

def generate_sort(rows, cm):
    return "\n".join([f"\titem_{safe_val(r, cm['ItemID'])}_{safe_val(r, cm['Color'])}," for r in rows])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("excel")
    args = parser.parse_args()
    excel_path = os.path.abspath(args.excel)
    gen_dir = os.path.join(os.path.dirname(excel_path), "Generated")
    os.makedirs(gen_dir, exist_ok=True)
    
    df = pd.read_excel(excel_path, header=0, dtype=str).fillna('')
    cols = df.columns.tolist()
    col_map = {k: find_column(cols, v) for k, v in {
        'Fuel':'fuel',
        'ItemID':'itemid',
        'Color':'color',
        'LiveryText':'liverytext',
        'MDate':'mdate',
        'MPeroid':'mperoid',
        'VLife':'vlife',
        'Reli':'reli',
        'LoadingSpeed':'tlspeed',
        'PurchasePrice':'purchaseprice',
        'Maintenance':'maintenance',
        'Speed':'maxspeed',
        'Power':'powerkw',
        'Weight':'weight',
        'Capacity':'tcapacity',
        'Comfort':'comfort',
        'Hossz1':'h1',
        'Hossz2':'h2',
        'Hossz3':'h3',
        'Hossz4':'h4',
        'Hossz5':'h5',
        'Hossz6':'h6',
        'Pos1':'pos1',
        'Pos2':'pos2',
        'Pos3':'pos3',
        'PFolder':'pfolder',
        'Usage':'usage',
        'Flag':'flag',
        'TextManufacturer':'manufacturer',
        'TextType':'type',
        'TextSType1':'Subtype1',
        'TextSType2':'Subtype2',
        'TextOther1':'Other1',
        'TextOther2':'Other2'
    }.items()}

    rows = df[df[col_map['ItemID']].str.strip().astype(bool)].to_dict(orient='records')
    maps = build_string_maps(rows, col_map)

    for r in rows:
        with open(os.path.join(gen_dir, f"{safe_val(r, col_map['ItemID'])}_{safe_val(r, col_map['Color'])}.nml"), 'w', encoding='utf-8') as f:
            f.write(generate_nml(r, col_map, maps))
    
    with open(os.path.join(gen_dir, '00_jarmuszovegek.lng'), 'w', encoding='utf-8') as f: f.write(generate_lng(rows, col_map, maps))
    with open(os.path.join(gen_dir, '00_sort.nml'), 'w', encoding='utf-8') as f: f.write(generate_sort(rows, col_map))
    print(f"Kész! {len(rows)} jármű nml generálva.")

if __name__ == "__main__": main()