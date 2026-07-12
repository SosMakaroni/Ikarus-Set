import os
from PIL import Image

# --- BEÁLLÍTÁSOK ---
MAX_SOR_KEPENKENT = 11  # Egy képen legfeljebb 11 sor van
Y_START = 80            # Első sor Y koordinátája
Y_LEPESKOZ = 90         # Sorok közötti távolság (90 pixel)

X_NEZET_2 = 22
X_NEZET_8 = 250
X_NEZET_10 = 302
X_NEZET_16 = 530

W, H = 37, 28
DXA, DYA = -2, 1  # Balra 2, Lefelé 1
DXB, DYB = 2, 1  # Jobbra 2, Lefelé 1

# Mivel az eredeti palettával dolgozunk, a szín helyett 
# közvetlenül a kívánt színindexet (0) adjuk meg.
KIPOTLO_SZIN_INDEX = 0 
# -------------------

def kepek_csoportos_javitasa():
    # Megkeressük az összes PNG fájlt a mappa gyökerében
    aktualis_mappa = os.getcwd()
    png_fajlok = [f for f in os.listdir(aktualis_mappa) if f.lower().endswith('.png') and not f.endswith('_javitott.png')]

    if not png_fajlok:
        print("Nem találtam feldolgozható .png fájlt ebben a mappában!")
        return

    print(f"Találtam {len(png_fajlok)} db képet. Indul a feldolgozás...\n")

    for fajl_nev in png_fajlok:
        print(f"-> {fajl_nev} feldolgozása...")
        
        # Megnyitjuk a képet, és MEGTARTJUK az eredeti formátumot (Palettát)
        img = Image.open(fajl_nev)
        pixels = img.load()
        
        # Megnézzük, a kép magassága alapján ténylegesen hány sor fér rá (max 11)
        sorok_szama = 0
        for s in range(MAX_SOR_KEPENKENT):
            if Y_START + (s * Y_LEPESKOZ) + H <= img.height:
                sorok_szama += 1
            else:
                break

        # Végigmegyünk a kép sorain
        for sor in range(sorok_szama):
            jelenlegi_y = Y_START + (sor * Y_LEPESKOZ)
            
            for x_start in [X_NEZET_2, X_NEZET_10]:
                # 1. Kivágás (az eredeti indexelt sprite-ot vágja ki)
                box = (x_start, jelenlegi_y, x_start + W, jelenlegi_y + H)
                sprite = img.crop(box)
                
                # 2. Kitöltés a 0-s színindexszel
                for y in range(jelenlegi_y, jelenlegi_y + H):
                    for x in range(x_start, x_start + W):
                        if 0 <= x < img.width and 0 <= y < img.height:
                            pixels[x, y] = KIPOTLO_SZIN_INDEX
                
                # 3. Beillesztés az új helyre
                uj_x = x_start + DXA
                uj_y = jelenlegi_y + DYA
                img.paste(sprite, (uj_x, uj_y))

            for x_start in [X_NEZET_8, X_NEZET_16]:
                # 1. Kivágás
                box = (x_start, jelenlegi_y, x_start + W, jelenlegi_y + H)
                sprite = img.crop(box)
                
                # 2. Kitöltés a 0-s színindexszel
                for y in range(jelenlegi_y, jelenlegi_y + H):
                    for x in range(x_start, x_start + W):
                        if 0 <= x < img.width and 0 <= y < img.height:
                            pixels[x, y] = KIPOTLO_SZIN_INDEX
                
                # 3. Beillesztés az új helyre
                uj_x = x_start + DXB
                uj_y = jelenlegi_y + DYB
                img.paste(sprite, (uj_x, uj_y))

        # Új fájlnév generálása
        nev, kiterjesztes = os.path.splitext(fajl_nev)
        uj_fajl_nev = f"{nev}{kiterjesztes}"
        
        # Mentés - mivel nem változtattunk módot, az eredeti paletta érintetlen maradt
        img.save(uj_fajl_nev)
        print(f"   Kész! Elmentve: {uj_fajl_nev} ({sorok_szama} sor módosítva, mód: {img.mode})")

    print("\nMinden fájl feldolgozása sikeresen befejeződött!")

if __name__ == "__main__":
    kepek_csoportos_javitasa()