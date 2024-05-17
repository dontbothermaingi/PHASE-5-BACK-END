from app import db, app
from models import Product,Admin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def seed_data():
    with app.app_context():

        print('Deleting existing products...')
        Product.query.delete()
        Admin.query.delete()


        print('Creating products...')

        seller_id = 1  # Set the seller_id to 1 for all products

        phone1 = Product(name='iPhone 14 Prp', pet='Dog', price=999, description='Apple iPhone 14 Pro, 128GB, Purple', image_url='https://i.pinimg.com/564x/46/4a/3c/464a3c2e8af440f769de8456976ffbc7.jpg', quantity_available=100, type= 'service',seller_id=seller_id)
        phone2 = Product(name='Samsung Galaxy S20', pet='Cat',price=799, description='Samsung Galaxy S20, 128GB, Cosmic Gray', image_url='https://i.pinimg.com/564x/e8/b2/7d/e8b27df6b3f8f76c569c1715297672d2.jpg', quantity_available=80, type= 'product',seller_id=seller_id)
        phone3 = Product(name='Google Pixel 5', pet='Cat',price=699, description='Google Pixel 7a, 128GB, Just Black', image_url='https://i.pinimg.com/564x/df/c7/24/dfc72427002660c11845df1c3e6cf43b.jpg', quantity_available=120, type= 'service',seller_id=seller_id)
        phone4 = Product(name='OnePlus 9 Pro',pet='Dog', price=899, description='OnePlus 9 Pro, 256GB, Morning Mist', image_url='https://i.pinimg.com/564x/a2/c9/61/a2c9612d875b39b0d899598b67dc415d.jpg', quantity_available=90,type= 'product', seller_id=seller_id)

        
        admin1 = Admin(username='MacBook Pro', email="jondoe@gmail.com", password=bcrypt.generate_password_hash('Applecider'), role='admin')
        admin2 = Admin(username='Mac Bouy', email="markdoe@gmail.com", password=bcrypt.generate_password_hash('Applecider'), role='admin')

        
        admins = [admin1, admin2]
        products = [phone1, phone2, phone3, phone4]

        # Combine all the objects into a single iterable
        objects_to_add = admins + products

        # Add all objects to the session
        db.session.add_all(objects_to_add)

        # Commit the changes
        db.session.commit()


        print('Successfully created products')

if __name__ == '__main__':
    seed_data()
