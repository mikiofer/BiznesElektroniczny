import json
import csv
import re
import random
from pathlib import Path



# --- USTAWIENIA (na start) ---
TAX_RULE_ID = 1          
ACTIVE = 1
AVAILABLE_FOR_ORDER = 1
SHOW_PRICE = 1
CATEGORY_MAP = {
    "https://www.x-kom.pl/g-2/c/159-laptopy-notebooki-ultrabooki.html":
        "Laptopy i komputery/Laptopy-Notebooki-Ultrabooki",
    "https://www.x-kom.pl/g-2/c/3524-laptopy-biznesowe.html":
        "Laptopy i komputery/Laptopy biznesowe",
}
BASE_IMAGE_URL = "http://localhost/import-images"



def parse_price_to_gross(price_str: str) -> float:
    """
    Przykład wejścia: "2 68900 zł"
    Chcemy: 2689.00
    """
    if not price_str:
        return 0.0
    s = price_str.lower().replace("zł", "").strip()
    # zostaw tylko cyfry i spacje
    s = re.sub(r"[^0-9 ]", "", s)
    s = s.replace(" ", "")
    # jeśli końcówka ma 2 cyfry groszy, a całość > 2 cyfry
    if len(s) >= 3:
        # zakładamy, że ostatnie 2 cyfry to grosze (często x-kom tak zapisuje)
        return float(s[:-2] + "." + s[-2:])
    return float(s)



def shorten(text: str, max_len: int = 600) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def iter_products(tree: list):
    """
    Przechodzi po strukturze kategorii/subkategorii i zwraca produkty.
    """
    for cat in tree:
        # kategorie level 0
        for sub in cat.get("subcategories", []):
            # subkategorie level 1
            for p in sub.get("products", []):
                yield cat, sub, p


def build_category_path(subcategory_url: str) -> str:
    try:
        return CATEGORY_MAP[subcategory_url]
    except KeyError:
        raise ValueError(f"Brak mapowania kategorii dla URL: {subcategory_url}")


def random_qty(p_zero: float = 0.05) -> int:
    # 5% szans na 0, w pozostałych przypadkach 1-10
    if random.random() < p_zero:
        return 0
    return random.randint(1, 10)


def json_to_csv(input_json: Path, output_csv: Path, target_subcategory_url: str, vat_rate: float = 0.23):
    with input_json.open("r", encoding="utf-8") as f:
        data = json.load(f)

    headers = [
        "Aktywny (0 lub 1)",
        "Nazwa*",
        "Kategorie (x,y,z...)",
        "Cena zawiera podatek. (brutto)",
        "ID reguły podatku",
        "Ilość",
        "Dostępne do zamówienia (0 = Nie, 1 = Tak)",
        "Pokaż cenę (0 = Nie, 1 = Tak)",
        "Adresy URL zdjęcia (x,y,z...)",
        #"Podsumowanie",
        #"Opis",
    ]

    rows = []
    for cat, sub, p in iter_products(data):
        if sub.get("url") != target_subcategory_url:
            continue

        title = p.get("title", "").strip()
        if not title:
            continue

        cat_path = build_category_path(sub.get("url"))

        try:
            gross = parse_price_to_gross(p.get("price", ""))
        except Exception:
            continue

        images = p.get("images") or []
        if len(images) == 0:
            continue
        local_urls = []
        for img in images[:2]:
            # filename może być zapisany z backslashami (zależnie od tego, na czym scraper działał)
            # więc normalizujemy na "/"
            rel = (img.get("filename") or "").replace("\\", "/").lstrip("/")
            # rel wygląda np: "hp-probook-.../1298239_1.jpg"
            local_urls.append(f"{BASE_IMAGE_URL}/{rel}")
        images_field = ",".join(local_urls)

        #desc_html = p.get("descriptionHtml", "") or ""
        #desc_text = p.get("descriptionText", "") or ""

        rows.append({
            headers[0]: ACTIVE,
            headers[1]: title,
            headers[2]: cat_path,
            headers[3]: f"{gross:.2f}",
            headers[4]: TAX_RULE_ID,
            headers[5]: random_qty(0.05),
            headers[6]: AVAILABLE_FOR_ORDER,
            headers[7]: SHOW_PRICE,
            headers[8]: images_field,
            #headers[9]: shorten(desc_text, 600),
            #headers[10]: desc_html, #TU BYLO 10!!!
        })

    # zapis CSV – Presta często lepiej znosi ';' w PL (przecinek bywa problematyczny)
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"OK: zapisano {len(rows)} produktów do {output_csv}")



if __name__ == "__main__":
    #---LAPTOPY I KOMPUTERY---
    #json_to_csv(Path("../scraper-output/shorter-products-jsons/pruned_tree.json"), Path("presta_import_products.csv"), "https://www.x-kom.pl/g-2/c/159-laptopy-notebooki-ultrabooki.html")
    json_to_csv(Path("../scraper-output/shorter-products-jsons/pruned_tree.json"), Path("presta_import_products.csv"), "https://www.x-kom.pl/g-2/c/3524-laptopy-biznesowe.html")
    #pass
