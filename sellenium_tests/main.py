import os
import time
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random
import string


def random_str(length=8):

    return ''.join(random.choices(string.ascii_lowercase, k=length))


URL_SKLEPU = "http://localhost:8080"
KAT_1_URL = f"{URL_SKLEPU}/11-laptopy-biznesowe"
KAT_2_URL = f"{URL_SKLEPU}/13-smartfony-i-smartwatche"

MAX_PRODUCTS = 10
CHROME_DRIVER_PATH = "./chromedriver.exe"
HASLO = "123456"


# =====================
# DRIVER
# =====================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

download_dir = os.getcwd()

prefs = {
    "download.default_directory": download_dir,       # Gdzie zapisać plik
    "download.prompt_for_download": False,            # Nie pytaj gdzie zapisać
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,       # ⚠️ KLUCZOWE: Nie otwieraj w Chrome, tylko pobierz
    "profile.default_content_settings.popups": 0
}
options.add_experimental_option("prefs", prefs)



service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# =====================
# FUNKCJE
# =====================

def get_product_urls(category_url, limit=5):
    driver.get(category_url)

    # czekamy aż produkty się załadują
    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".thumbnail.product-thumbnail")
        )
    )

    anchors = driver.find_elements(By.CSS_SELECTOR, ".thumbnail.product-thumbnail")

    urls = []
    for a in anchors:
        href = a.get_attribute("href")
        if href and href not in urls:
            urls.append(href)

    print(f"🔎 Znaleziono {len(urls)} produktów w kategorii")
    return urls[:limit]


def set_quantity(qty):
    qty_input = driver.find_element(By.ID, "quantity_wanted")

    # 1️⃣ wyczyść poprawnie
    qty_input.click()
    qty_input.send_keys(Keys.CONTROL + "a")  # zaznacz wszystko
    qty_input.send_keys(Keys.DELETE)  # usuń

    # 2️⃣ ustaw nową wartość
    qty_input.send_keys(str(qty))

    # 3️⃣ wyzwól change event przez JS
    driver.execute_script("""
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, qty_input)

    # 4️⃣ poczekaj aż input faktycznie ma poprawną wartość
    WebDriverWait(driver, 3).until(lambda d: qty_input.get_attribute("value") == str(qty))


def add_single_product(url):
    driver.get(url)

    try:
        qty_input = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "quantity_wanted"))
        )
        add_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "add-to-cart"))
        )
    except TimeoutException:
        print("⚠️ To nie jest strona produktu – pomijam")
        return False

    # pobranie stocku
    try:
        stock_el = driver.find_element(By.CSS_SELECTOR, ".product-quantities")
        stock_text = stock_el.text
        stock = int(''.join(filter(str.isdigit, stock_text)))
    except:
        stock = 10

    qty = random.randint(1, 3)
    qty = min(qty, stock)
    if qty == 0:
        print("⚠️ Produkt niedostępny – pomijam")
        return False

    set_quantity(qty)

    wait.until(lambda d: qty_input.get_attribute("value") == str(qty))

    # 🔹 scroll + JS click
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", add_btn)

    # czekaj na modal
    wait.until(EC.visibility_of_element_located((By.ID, "blockcart-modal")))

    # zamknij modal
    close_btn = driver.find_element(By.CSS_SELECTOR, "#blockcart-modal .close")
    driver.execute_script("arguments[0].click();", close_btn)
    time.sleep(0.5)

    print(f"✅ Dodano produkt ({qty} szt.)")
    return True



def add_products_to_cart():
    categories = [KAT_1_URL, KAT_2_URL]
    added = 0

    for category in categories:
        if added >= MAX_PRODUCTS:
            break

        product_urls = get_product_urls(category, limit=5)

        for url in product_urls:
            if added >= MAX_PRODUCTS:
                break

            if add_single_product(url):
                added += 1

    print(f"\n🛒 Łącznie dodano {added} produktów")


def search_and_add_random_product(search_query="hunter"):
    # 1️⃣ Wchodzimy na stronę sklepu
    driver.get(URL_SKLEPU)

    # 2️⃣ Znajdź pole wyszukiwania
    try:
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "s"))
        )
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.ENTER)
    except:
        print("❌ Nie udało się znaleźć pola wyszukiwania")
        return False

    # 3️⃣ Czekamy na wyniki
    try:
        results = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-miniature"))
        )
    except:
        print("❌ Brak wyników wyszukiwania")
        return False

    # 4️⃣ Wybierz losowy produkt
    random_product = random.choice(results)

    try:
        # Pobranie linku do produktu
        link = random_product.find_element(By.CSS_SELECTOR, ".thumbnail.product-thumbnail").get_attribute("href")
    except:
        print("❌ Nie udało się pobrać linku do produktu")
        return False

    # 5️⃣ Dodaj do koszyka
    print(f"🔎 Losowy produkt do dodania: {link}")
    return add_single_product(link)

def remove_products_from_cart(n=3):
    driver.get(f"{URL_SKLEPU}/koszyk")  # lub link do koszyka w Twoim sklepie
    time.sleep(2)  # poczekaj aż strona koszyka się załaduje

    removed = 0

    for _ in range(n):
        try:
            # znajdź wszystkie przyciski "usuń"
            delete_buttons = driver.find_elements(By.CLASS_NAME, "remove-from-cart")

            if not delete_buttons:
                print("⚠️ Brak produktów do usunięcia")
                break

            # użyj JS do kliknięcia, bo czasem zwykły click nie działa
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_buttons[0])
            driver.execute_script("arguments[0].click();", delete_buttons[0])

            # poczekaj aż Prestashop przeliczy koszyk
            time.sleep(2)

            removed += 1
            print(f"🗑️ Usunięto produkt ({removed}/{n})")

        except Exception as e:
            print(f"❌ Błąd przy usuwaniu produktu: {e}")
            break

    print(f"✅ Usunięto {removed} produkty z koszyka")
    return removed


def go_to_register_form():
    driver.get(f"{URL_SKLEPU}/moje-konto")

    try:
        register_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Załóż"))
        )
        register_link.click()
        print("➡️ Przejście do formularza rejestracji")
    except TimeoutException:
        print("❌ Nie udało się znaleźć linku do rejestracji")
        return False

    # czekamy aż formularz rejestracji się pojawi
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "customer-form"))
    )
    return True


def register_new_account():
    driver.get(f"{URL_SKLEPU}/moje-konto")

    # 1️⃣ Klikamy link "Nie masz konta? Załóż je tutaj"
    try:
        register_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Załóż"))
        )
        register_link.click()
        print("➡️ Przejście do formularza rejestracji")
    except TimeoutException:
        print("❌ Nie udało się znaleźć linku do rejestracji")
        return None

    # 2️⃣ Czekamy aż formularz będzie widoczny
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "customer-form"))
    )

    # 3️⃣ Wypełniamy inputy tekstowe
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "field-firstname"))
    ).send_keys("Jan")
    driver.find_element(By.ID, "field-lastname").send_keys("Testowy")

    email = f"test_{random_str()}@test.com"
    driver.find_element(By.ID, "field-email").send_keys(email)

    driver.find_element(By.ID, "field-password").send_keys(HASLO)
    driver.find_element(By.ID, "field-birthday").send_keys("1990-01-01")  # opcjonalne

    # 4️⃣ Klikamy checkboxy JS-em
    driver.execute_script("arguments[0].click();", driver.find_element(By.NAME, "customer_privacy"))
    driver.execute_script("arguments[0].click();", driver.find_element(By.NAME, "psgdpr"))

    # 5️⃣ Klikamy przycisk "Zapisz" JS-em
    continue_btn = driver.find_element(By.CSS_SELECTOR, "button[data-link-action='save-customer']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
    driver.execute_script("arguments[0].click();", continue_btn)



    print(f"✅ Zarejestrowano konto: {email}")
    return email


def checkout_order():
    print("➡️ Przechodzę do koszyka...")

    # Bezpośrednie wejście na URL koszyka (action=show)
    cart_url = f"{URL_SKLEPU}/koszyk?action=show"
    driver.get(cart_url)

    try:
        # Sprawdź, czy jesteśmy w koszyku (przycisk 'Przejdź do realizacji zamówienia')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cart-summary"))
        )
        print("✅ Jesteśmy w podsumowaniu koszyka")
        return True

    except TimeoutException:
        print("❌ Nie udało się załadować widoku koszyka")
        return False

def go_to_checkout_from_cart():
    try:
        wait = WebDriverWait(driver, 10)

        # Czekamy, aż przycisk będzie widoczny
        checkout_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary[href*='/zamówienie']"))
        )

        # Klikamy JS-em, żeby ominąć ewentualne problemy z zakrytym elementem
        driver.execute_script("arguments[0].click();", checkout_btn)
        print("✅ Przeszliśmy do realizacji zamówienia")
        return True

    except Exception as e:
        print(f"❌ Błąd przy przechodzeniu do checkoutu: {type(e).__name__} - {e}")
        driver.save_screenshot("checkout_from_cart_error.png")
        return False

def finalize_order():
    """
    Finalizuje zamówienie w Prestashop po wejściu w checkout:
    1️⃣ Adres
    2️⃣ Przewoźnik
    3️⃣ Płatność przy odbiorze
    4️⃣ Regulamin (poprawny checkbox)
    5️⃣ Zatwierdzenie zamówienia
    """
    go_to_checkout_from_cart()
    try:
        wait = WebDriverWait(driver, 10)

        # 1️⃣ Adres
        print("➡️ Potwierdzam adres...")
        address_field = wait.until(EC.presence_of_element_located((By.ID, "field-address1")))
        address_field.clear()
        address_field.send_keys("Ulica Sezamkowa 1")
        driver.find_element(By.ID, "field-postcode").send_keys("00-001")
        driver.find_element(By.ID, "field-city").send_keys("Warszawa")
        driver.find_element(By.NAME, "confirm-addresses").click()
        time.sleep(1)

        # 2️⃣ Przewoźnik
        print("➡️ Wybieram przewoźnika...")
        delivery_options = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[name^='delivery_option']"))
        )
        driver.execute_script("arguments[0].click();", delivery_options[0])
        driver.find_element(By.NAME, "confirmDeliveryOption").click()
        time.sleep(1)

        # 3️⃣ Płatność przy odbiorze
        print("➡️ Wybieram płatność przy odbiorze...")
        payment_radio = driver.find_element(By.ID, "payment-option-2")
        driver.execute_script("arguments[0].click();", payment_radio)
        WebDriverWait(driver, 5).until(lambda d: payment_radio.is_selected())
        print("✅ Płatność przy odbiorze zaznaczona")

        # 4️⃣ Akceptacja regulaminu
        print("➡️ Akceptuję regulamin...")
        terms_checkbox = driver.find_element(By.ID, "conditions_to_approve[terms-and-conditions]")
        driver.execute_script("arguments[0].click();", terms_checkbox)

        # 5️⃣ Zatwierdzenie zamówienia
        print("➡️ Zatwierdzam zamówienie...")
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#payment-confirmation button"))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)

        # 6️⃣ Status zamówienia
        confirmation_msg = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#content-hook_order_confirmation h3"))
        ).text
        print(f"🎉 Zamówienie złożone. Status: {confirmation_msg}")

        return True

    except Exception as e:
        print(f"❌ Błąd podczas finalizacji zamówienia: {type(e).__name__} - {e}")
        driver.save_screenshot("checkout_error.png")
        return False


def logout():

    try:
        # Sprawdź, czy istnieje link do wylogowania
        logout_link = driver.find_elements(By.CSS_SELECTOR, "a.logout")
        if logout_link:
            logout_link[0].click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.login"))
            )
            print("✅ Wylogowano użytkownika")
            return True
        else:
            print("ℹ️ Brak zalogowanego użytkownika")
            return True
    except Exception as e:
        print(f"❌ Błąd przy wylogowywaniu: {type(e).__name__} - {e}")
        driver.save_screenshot("logout_error.png")
        return False


def login_and_download_invoice(email="biznes@gmail.com", password="biznes"):
    wait = WebDriverWait(driver, 15)

    try:
        print(f"➡️ Logowanie na konto: {email}...")
        driver.get(f"{URL_SKLEPU}/moje-konto")

        # 1. LOGOWANIE
        wait.until(EC.visibility_of_element_located((By.ID, "field-email"))).send_keys(email)
        driver.find_element(By.ID, "field-password").send_keys(password)

        login_btn = driver.find_element(By.ID, "submit-login")
        driver.execute_script("arguments[0].click();", login_btn)
        time.sleep(2)

        # 2. WEJŚCIE W HISTORIĘ
        print("➡️ Przechodzę do historii zamówień...")
        driver.get(f"{URL_SKLEPU}/historia-zamowien")

        # 3. SZUKANIE FAKTURY I STATUSU
        print("🔎 Analizuję zamówienia...")

        # Czekamy na wiersze tabeli
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr")))
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

        invoice_found = False

        for row in rows:
            # Sprawdzamy, czy w tym wierszu jest link do faktury
            pdf_links = row.find_elements(By.CSS_SELECTOR, "a[href*='controller=pdf-invoice']")

            if pdf_links:
                # --- TUTAJ POBIERAMY STATUS ---
                # W PrestaShop status jest zazwyczaj w elemencie z klasą 'label' lub po prostu w jednej z kolumn
                try:
                    # Próbujemy znaleźć "label" (kolorowy prostokąt ze statusem)
                    status_element = row.find_element(By.CSS_SELECTOR, ".label")
                    status_text = status_element.text.strip()
                except:
                    # Jeśli nie ma labela, bierzemy tekst z całego wiersza i czyścimy go
                    # (To zadziała nawet jak zmieni się motyw)
                    full_text = row.text.replace("\n", " ")
                    status_text = f"[Status w wierszu]: {full_text}"

                print(f"✅ Znaleziono fakturę dla zamówienia.")
                print(f"📊 STATUS ZAMÓWIENIA: {status_text}")  # <--- TU WYPISUJEMY STATUS

                # Pobieramy fakturę
                target_link = pdf_links[0]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_link)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", target_link)

                print("⬇️ Rozpoczęto pobieranie...")
                invoice_found = True
                break  # Przerywamy pętlę po znalezieniu pierwszej faktury

        if not invoice_found:
            print("ℹ️ Przeszukano zamówienia, ale nie znaleziono żadnej faktury PDF.")
            return False

        # 4. WERYFIKACJA PLIKU
        print("⏳ Czekam 5 sekund na zapisanie pliku...")
        time.sleep(5)

        files = os.listdir(os.getcwd())
        pdfs = [f for f in files if f.endswith(".pdf")]

        if pdfs:
            print(f"🎉 SUKCES! Pobrane pliki PDF w folderze: {pdfs}")
            return True
        else:
            print("⚠️ Kliknięto, ale plik nie pojawił się w folderze.")
            return False

    except Exception as e:
        print(f"❌ Błąd podczas pobierania faktury: {e}")
        return False
# =====================
# START TESTU
# =====================


try:
    print("🚀 START TESTU")

    driver.get(URL_SKLEPU)

    # 1️⃣ Dodaj produkty z kategorii
    add_products_to_cart()
    print("✅ ETAP DODAWANIA ZAKOŃCZONY")

    # 2️⃣ Wyszukaj i dodaj losowy produkt
    while True:
        if search_and_add_random_product("hunter"):
            print("✅ Losowy produkt wyszukany i dodany do koszyka")
            break  #
        else:
            print("❌ Nie udało się dodać produktu. Ponawiam próbę za 2 sekundy...")
            time.sleep(2)
    removed_count = remove_products_from_cart(3)
    print(f"Usunięto {removed_count} produkty z koszyka")

    user_email = register_new_account()
    print(f"Konto utworzone dla: {user_email}")

    checkout_order()
    finalize_order()

    logout()
    login_and_download_invoice(email="biznes@gmail.com", password="biznes")
except Exception as e:
    print("❌ BŁĄD:")
    print(type(e).__name__, e)
    driver.save_screenshot("error.png")

finally:
    # 3️⃣ Zamknij przeglądarkę dopiero na końcu
    time.sleep(3)
    driver.quit()
