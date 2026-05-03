#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import os

def process_sprites(image_path):
    # Abszolút út és mappa név kinyerése
    abs_path = os.path.abspath(image_path)
    parent_folder = os.path.basename(os.path.dirname(abs_path))
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"Hiba: Nem sikerült betölteni a képet: {image_path}")
        return

    # Képfeldolgozás: szürkeárnyalat és küszöbölés
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 5 and h > 5:
            rects.append([x, y, w, h])

    # Rendezés: Sorok (Y), majd oszlopok (X) szerint
    rects.sort(key=lambda r: (r[1] // 10, r[0]))
    
    # Csoportok meghatározása[cite: 3]
    group_1 = rects[:8]
    group_2 = rects[8:16] if len(rects) > 8 else []
    
    # Módosított group_3 logika:
    # Ha van legalább 9 kép, a 9. (index 8) legyen a kiválasztott, különben a 3. (index 2)[cite: 3]
    if len(rects) >= 9:
        group_3 = [rects[8]]
    else:
        group_3 = [rects[2]] if len(rects) > 2 else []

    def generate_nml_block1(name, sprite_list, folder):
        block = f"spriteset(ss_{name}, \"gfx/{folder}/{name}.png\") {{\n"
        for r in sprite_list:
            x, y, w, h = r
            block += f"    [ {x:4}, {y:4}, {w:3}, {h:3}, {-w//2:3}, {-h//2:3}, ANIM ]\n"
        block += "}\n\n"
        return block

    def generate_nml_block2(name, sprite_list, folder):
        block = f"spriteset(ss_{name}_loading, \"gfx/{folder}/{name}.png\") {{\n"
        for r in sprite_list:
            x, y, w, h = r
            block += f"    [ {x:4}, {y:4}, {w:3}, {h:3}, {-w//2:3}, {-h//2:3}, ANIM ]\n"
        block += "}\n\n"
        return block

    def generate_nml_block3(name, sprite_list, folder):
        block = f"spriteset(ss_{name}_purchase, \"gfx/{folder}/{name}.png\") {{\n"
        for r in sprite_list:
            x, y, w, h = r
            block += f"    [ {x:4}, {y:4}, {w:3}, {h:3}, {-w//2:3}, {-h//2:3}, ANIM ]\n"
        block += "}\n\n"
        return block

    # NML tartalom összeállítása[cite: 3]
    nml_content = f"// NML Sprite Layout for {base_name}.png\n\n"
    nml_content += generate_nml_block1(base_name, group_1, parent_folder)
    if group_2:
        nml_content += generate_nml_block2(base_name, group_2, parent_folder)
    if group_3:
        nml_content += generate_nml_block3(base_name, group_3, parent_folder)

    output_filename = f"{base_name}_spriteset.nml"
    with open(output_filename, "w") as f:
        f.write(nml_content)

    print(f"Siker! Generált fájl: {output_filename} (Mappa: {parent_folder})")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_sprites(sys.argv[1])