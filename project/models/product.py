from project import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_url = db.Column(db.String(500), nullable=True)

    title = db.Column(db.String(255), nullable=False, unique=True)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, title, price, image_url=None, description=None):
        self.title = title
        self.price = price
        self.image_url = image_url
        self.description = description


    @staticmethod
    def get_all_products():
        return Product.query.all()

    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def save_products(products_list):
        """
        Primește lista de dicționare de la scraper și o salvează în baza de date.
        Dacă produsul există deja după denumire (title), îi actualizează restul datelor (Upsert).
        """
        for prod_data in products_list:
            # Verificăm dacă există deja un produs cu aceeași denumire
            existing_product = Product.query.filter_by(title=prod_data['title']).first()

            if existing_product:
                existing_product.price = prod_data['price']
                existing_product.image_url = prod_data['image_url']
                existing_product.description = prod_data['description']
            else:
                new_product = Product(
                    title=prod_data['title'],
                    price=prod_data['price'],
                    image_url=prod_data['image_url'],
                    description=prod_data['description']
                )
                db.session.add(new_product)

        db.session.commit()

    @staticmethod
    def update_product(product_id, title, price, description, image_url):
        product = Product.query.get(product_id)
        if product:
            product.title = title
            product.price = price
            product.description = description
            product.image_url = image_url
            db.session.commit()

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
