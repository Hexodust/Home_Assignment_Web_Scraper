import time
from playwright.sync_api import sync_playwright


def run_scraper():
    products_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Navigare catre pagina de login...")
        page.goto("https://www.web-scraping.dev/login")

        # Autentificare
        page.fill("input[name='username']", "user123")
        page.fill("input[name='password']", "password")

        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        print("Autentificare reusita!")

        # Navigare catre pagina 'consumables'
        print("Navigare catre produse...")
        page.goto("https://www.web-scraping.dev/products?category=consumables")
        page.wait_for_load_state("networkidle")

        pagina_curenta = 1
        url_anterior = ""

        while True:
            url_curent = page.url
            print(f"Scraping pagina {pagina_curenta}... (URL: {url_curent})")

            # --- SIGURANȚĂ 1: Dacă URL-ul nu s-a schimbat față de tura trecută, am terminat ---
            if url_curent == url_anterior:
                print("URL-ul nu s-a schimbat după click. S-a ajuns la capăt!")
                break
            url_anterior = url_curent

            # Extragere produse de pe pagina curentă
            product_elements = page.query_selector_all(".product")

            # --- SIGURANȚER 2: Dacă pagina e goală și nu are produse, oprim bucla ---
            if not product_elements:
                print("Nu s-au mai găsit produse pe această pagină. Scraping complet!")
                break

            for product in product_elements:
                try:
                    img_product = product.query_selector("img")
                    img_url = img_product.get_attribute("src") if img_product else None

                    title_product = product.query_selector(".product-title, h3, h5")
                    title = title_product.inner_text().strip() if title_product else "N/A"

                    price_product = product.query_selector(".price")
                    price = price_product.inner_text().strip() if price_product else "0.00"

                    desc_product = product.query_selector(".short-description")
                    description = desc_product.inner_text().strip() if desc_product else ""

                    products_data.append({
                        "image_url": img_url,
                        "title": title,
                        "price": price,
                        "description": description,
                    })
                except Exception as e:
                    print(f"Eroare la extragerea unui produs: {e}")
                    continue

            # --- LOGICA DE PAGINARE DINAMICĂ ---
            next_button = page.locator(".paging a:has-text('>')")

            if next_button.count() > 0 and next_button.is_visible():
                print("Se apasă pe butonul '>' pentru pagina următoare...")
                next_button.click()
                page.wait_for_load_state("networkidle")
                time.sleep(1)  # Pauză de siguranță pentru randare conținut nou
                pagina_curenta += 1
            else:
                print("Butonul '>' nu mai este vizibil. S-a ajuns la ultima pagină!")
                break

        browser.close()

    print(f"Scraping finalizat! S-au extras în total {len(products_data)} produse.")
    return products_data
