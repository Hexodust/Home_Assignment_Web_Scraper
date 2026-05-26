from flask import Blueprint, render_template, request, redirect, url_for
from project.models.product import Product
from project.services.scraping_service import run_scraper

products_blueprint = Blueprint('products', __name__)


@products_blueprint.route('/products')
def index():
    # Apelăm metoda prin intermediul clasei Product
    products = Product.get_all_products()
    return render_template('products/index.html', products=products)


@products_blueprint.route('/products/run-scraper')
def trigger_scraper():
    print("Se pornește scraperul Playwright...")
    date_extrase = run_scraper()
    Product.save_products(date_extrase)
    print("Scraping finalizat și datele au fost salvate!")
    return redirect(url_for('products.index'))


@products_blueprint.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    product = Product.get_product_by_id(product_id)

    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        image_url = request.form['image_url']

        Product.update_product(product_id, title, price, description, image_url)
        return redirect(url_for('products.index'))

    return render_template('products/edit.html', product=product)


@products_blueprint.route('/products/delete/<int:product_id>', methods=['POST'])
def delete(product_id):
    Product.delete_product(product_id)
    return redirect(url_for('products.index'))
