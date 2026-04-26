#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import os

def process_sprites(image_path):
    # Fájlnév kinyerése kiterjesztés nélkül
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Kép betöltése
    img = cv2.imread(image_path)
    if img is None:
        print(f"Hiba: Nem sikerült betölteni a képet: {image_path}")
        return

    # Képfeldolgozás (szürkeárnyalat + küszöbölés)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

    # Kontúrok keresése
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 5 and h > 5: # Zajszűrés
            rects.append([x, y, w, h])

    if len(rects) < 16:
        print(f"Figyelem! Csak {len(rects)} alakzatot találtam a várt 16 helyett.")
    elif len(rects) > 16:
        print(f"Figyelem! Több alakzatot ({len(rects)}) találtam, csak az első 16-ot használom.")

    # Rendezés: Először Y szerint (sorok), majd X szerint (oszlopok)
    # Egy kis toleranciát (10 pixel) használunk az Y-nál, hogy a nem tökéletesen egy vonalban lévők is egy sorba kerüljenek
    rects.sort(key=lambda r: (r[1] // 10, r[0]))
    
    # Csak az első 16 kell, ha több lenne
    rects = rects[:16]
    
    # Szétbontás két 8-as csoportra
    group_1 = rects[:8]
    group_2 = rects[8:16]

    def generate_nml_block1(name, sprite_list):
        block = f"spriteset(ss_{name}, \"grf/{name}.png\") {{\n"
        for r in sprite_list:
            x, y, w, h = r
            # NML: [x, y, width, height, offset_x, offset_y]
            block += f"    [ {x:4}, {y:4}, {w:3}, {h:3}, {-w//2:3}, {-h//2:3}, ANIM ]\n"
        block += "}\n\n"
        return block
    def generate_nml_block2(name, sprite_list):
        block = f"spriteset(ss_{name}_loading, \"grf/{name}.png\") {{\n"
        for r in sprite_list:
            x, y, w, h = r
            # NML: [x, y, width, height, offset_x, offset_y]
            block += f"    [ {x:4}, {y:4}, {w:3}, {h:3}, {-w//2:3}, {-h//2:3}, ANIM ]\n"
        block += "}\n\n"
        return block

    # NML tartalom összeállítása
    nml_content = f"// NML Sprite Layout for {base_name}.png\n\n"
    nml_content += generate_nml_block1(f"{base_name}", group_1)
    nml_content += generate_nml_block2(f"{base_name}", group_2)

    # Mentés a kép neve alapján .nml kiterjesztéssel
    output_filename = f"{base_name}_spriteset.nml"
    with open(output_filename, "w") as f:
        f.write(nml_content)

    print(f"Siker! Generált fájl: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_sprites(sys.argv[1])
    else:
        print("Használat: Húzz egy PNG-t a .bat fájlra!")