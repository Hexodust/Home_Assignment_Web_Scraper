from project import create_app, db  # Importăm creatorul aplicației și obiectul bazei de date
from project.models.product import Product
from project.services.scraping_service import run_scraper


def main():
    app = create_app()

    print("Se pornește scraperul Playwright...")
    date_extrase = run_scraper()

    with app.app_context():
        print("Se salvează produsele în baza de date...")
        Product.save_products(date_extrase)
        print("Scraping finalizat și datele au fost salvate cu succes!")


if __name__ == "__main__":
    main()
