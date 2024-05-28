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

        product1 = Product(name='Grooming', pet='Any', price=4000, description='Pet grooming', image_url='https://i.pinimg.com/736x/a4/bc/5e/a4bc5e366224d3fde5681e0cab947a45.jpg', quantity_available=100, type= 'service',seller_id=seller_id)
        product2 = Product(name='Transport', pet='Any',price=799, description='Pet transport', image_url='https://i.pinimg.com/236x/2c/00/fb/2c00fb92b4982b47b47cabec56592d86.jpg', quantity_available=80, type= 'service',seller_id=seller_id)
        product3 = Product(name='Training', pet='Any',price=699, description='Pet training', image_url='https://i.pinimg.com/236x/3e/7a/eb/3e7aeb3850255d9ffb70f499bc92c40f.jpg', quantity_available=120, type= 'service',seller_id=seller_id)
        product4 = Product(name='Vetcare',pet='Any', price=899, description='Vetcare', image_url='https://i.pinimg.com/236x/d9/b7/bf/d9b7bf0a4b4c91c697295904a93627e3.jpg', quantity_available=90,type= 'service', seller_id=seller_id)
        product5 = Product(name='Photoshoot', pet='Any', price=999, description='Pet photoshoot', image_url='https://i.pinimg.com/236x/f0/ff/22/f0ff22e2e95aa01728d697b7061e3c61.jpg', quantity_available=100, type= 'service',seller_id=seller_id)
        product6 = Product(name='Cat food', pet='Cat',price=799, description='Cat food', image_url='https://i.pinimg.com/236x/19/26/92/192692fcff982a4784ab39789c14399b.jpg', quantity_available=80, type= 'product',seller_id=seller_id)
        product7 = Product(name='Dog food', pet='Dog',price=699, description='Dog food', image_url='https://i.pinimg.com/236x/0e/5d/2c/0e5d2c628a102eba97411deca54079e3.jpg', quantity_available=120, type= 'product',seller_id=seller_id)
        product8 = Product(name='Cat feeder',pet='Cat', price=899, description='Cat feeder', image_url='https://i.pinimg.com/236x/8a/b1/b4/8ab1b48cdbafc4f03e4f5d410cd533ca.jpg', quantity_available=90,type= 'product', seller_id=seller_id)
        product9 = Product(name='Dog feeder', pet='Dog', price=999, description='Dog feeder', image_url='https://i.pinimg.com/236x/db/94/63/db9463c35e59b46e6d38963076bbce5b.jpg', quantity_available=100, type= 'product',seller_id=seller_id)
        product10 = Product(name='Cat collar', pet='Cat',price=799, description='Cat collar', image_url='https://i.pinimg.com/236x/a5/19/3d/a5193d0a7102356f87e822d73513c538.jpg', quantity_available=80, type= 'product',seller_id=seller_id)
        product11 = Product(name='Dog collar', pet='Dog',price=699, description='Dog collar', image_url='https://i.pinimg.com/236x/1a/f4/70/1af4708b6348f85ceb3f8d5a04c444ce.jpg', quantity_available=120, type= 'product',seller_id=seller_id)
        product12 = Product(name='Cat leash',pet='Cat', price=899, description='Cat leash', image_url='https://i.pinimg.com/236x/c4/67/7d/c4677d6c8f81838d7e0aae9af76a4eb7.jpg', quantity_available=90,type= 'product', seller_id=seller_id)
        product13 = Product(name='Dog leash', pet='Dog', price=999, description='Dog leash', image_url='https://i.pinimg.com/236x/98/0a/d5/980ad5d21bac19b9b0367e682687d38f.jpg', quantity_available=100, type= 'product',seller_id=seller_id)
        product14 = Product(name='Cat cage', pet='Cat',price=799, description='Cat cage', image_url='https://i.pinimg.com/236x/8f/f0/0c/8ff00cf0812583684d78b405288c3a0d.jpg', quantity_available=80, type= 'product',seller_id=seller_id)
        product15 = Product(name='Dog cage', pet='Dog',price=699, description='Dog cage', image_url='https://i.pinimg.com/236x/55/8c/e9/558ce91bce9eec4cf6cc8c9146b83eef.jpg', quantity_available=120, type= 'product',seller_id=seller_id)
        product16 = Product(name='Cat bed',pet='Cat', price=899, description='Cat bed', image_url='https://i.pinimg.com/236x/4e/cf/f8/4ecff8e77909362a0e711e5eff5f219b.jpg', quantity_available=90,type= 'product', seller_id=seller_id)
        product17 = Product(name='Dog bed',pet='Dog', price=899, description='Dog bed', image_url='https://i.pinimg.com/236x/2c/b6/32/2cb632750c3d4df70c8be82fdfd6bfd6.jpg', quantity_available=90,type= 'product', seller_id=seller_id)
        
        admin1 = Admin(username='Hen', email='kuku@gmail.com', password=bcrypt.generate_password_hash('kuku').decode('utf-8'), role='admin')
        admin2 = Admin(username='Duck', email='bata@gmail.com', password=bcrypt.generate_password_hash('bata').decode('utf-8'), role='admin')


        
        admins = [admin1, admin2]
        products = [product1, product2, product3, product4, product5, product6, product7, product8, product9, product10, product11, product12, product13, product14, product15, product16, product17]

        # Combine all the objects into a single iterable
        objects_to_add = admins + products

        # Add all objects to the session
        db.session.add_all(objects_to_add)

        # Commit the changes
        db.session.commit()


        print('Successfully created products')

if __name__ == '__main__':
    seed_data()
