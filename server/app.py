from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from models import db, User,Admin, Product, ProductOrder, ProductOrderItem, ShippingAddress,Cart, CartItem
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, get_jwt
from flask_bcrypt import Bcrypt
from functools import wraps
from werkzeug.security import check_password_hash
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

bcrypt = Bcrypt(app)

app.secret_key = 'secret key'
app.config['JWT_SECRET_KEY'] = 'this-is-secret-key'

jwt = JWTManager(app)

revoked_tokens = set()


# Decorator for admin-only access
# def admin_required(fn):
#     @wraps(fn)
#     def wrapper(*args, **kwargs):
#         current_user = get_jwt_identity()
#         if current_user.get('role') != 'admin':
#             return jsonify({'error': 'Unauthorized'}), 403
#         return fn(*args, **kwargs)
#     return wrapper

# User Registration
class UserRegister(Resource):
    @cross_origin()
    def post(self):
        data = request.get_json(force=True)

        # Log received data for debugging
        print('Received data:', data)

        if not data:
            return jsonify({'error': 'Missing JSON in request'}), 400

        username = data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        

        if not all([username, email, phone_number, password, confirm_password]):
            return jsonify({'error': 'Missing fields in request'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'User already exists'}), 409
        
        if password != confirm_password:
            return jsonify({'Error': 'Passwords not matching'}), 400
        
        hashed_pw = bcrypt.generate_password_hash(password.encode('utf-8'))

        new_user = User(
            username=username,
            email=email, 
            phone_number=phone_number, 
            password=hashed_pw,
            role='client'
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            'phone_number': new_user.phone_number,
        }), 201

api.add_resource(UserRegister, '/userRegister')


# User Login
class UserLogin(Resource):
    @cross_origin()
    def post(self):
        data = request.get_json(force=True)

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({'error': 'Unauthorized, incorrect password'}), 401
        
        # Generate access token with role included
        access_token = create_access_token(identity={'username': username, 'role': 'client'})

        return jsonify({
            "id": user.id,
            "username": user.username,
            "access_token": access_token
        }), 201

api.add_resource(UserLogin, '/userLogin')

# Admin Login
# class AdminLogin(Resource):
#     @cross_origin()
#     def post(self):
#         data = request.get_json(force=True)

#         username = data.get('username')
#         password = data.get('password')

#         # Checks if the admin exists in the Admin Table
#         admin = Admin.query.filter_by(username=username).first()

#         if admin is None:
#             return jsonify({'error': 'Unauthorized'}), 401
        
#         if not bcrypt.check_password_hash(admin.password, password):
#             return jsonify({'error': 'Unauthorized, incorrect password'}), 401
        
#         # Generate access token with role included
#         access_token = create_access_token(identity={'username': username, 'role': 'admin'})

#         return jsonify({
#             "id": admin.id,
#             "username": admin.username,
#             "access_token": access_token
#         }), 201

# api.add_resource(AdminLogin, '/adminlogin')


def create_admin_users():
    admin1 = Admin(username='Hen', email='kuku@gmail.com', password=check_password_hash('kuku'), role='admin')
    admin2 = Admin(username='Duck', email='bata@gmail.com', password=check_password_hash('bata'), role='admin')
    db.session.add(admin1)
    db.session.add(admin2)
    db.session.commit()



class AdminLogin(Resource):
    @cross_origin()
    def post(self):
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')

        logging.debug(f"Attempting login for user: {username}")

        # Check if the admin exists in the Admin table
        admin = Admin.query.filter_by(username=username).first()

        if admin is None:
            logging.debug(f"User {username} not found.")
            return jsonify({'error': 'Unauthorized'}), 401

        if admin is None or not check_password_hash(admin.password, password):
            logging.debug(f"Incorrect password for user {username}.")
            return jsonify({'error': 'Unauthorized'}), 401

        # Generate access token with role included
        access_token = create_access_token(identity={'username': username, 'role': 'admin'})
        
        logging.debug(f"User {username} logged in successfully.")


        return jsonify({
            "id": admin.id,
            "username": admin.username,
            "access_token": access_token
        }), 201

api.add_resource(AdminLogin, '/adminLogin')


# User Logout
class UserLogout(Resource):
    @jwt_required()  # Requires a valid access token to access this endpoint
    def post(self):
        try:
            # No need to retrieve raw JWT token, as jwt_required ensures a valid token
            # Revoke the current access token directly
            jti = get_jwt()["jti"]
            revoked_tokens.add(jti)

            return jsonify({'message': 'User Logout successful'}), 200
        except Exception as e:
            print(f"Error occurred during logout: {e}")
            return jsonify({'error': 'An unexpected error occurred'}), 500

api.add_resource(UserLogout, '/userLogout')


# Admin Logout
class AdminLogout(Resource):
    @jwt_required()  # Requires a valid access token to access this endpoint
    def post(self):
        try:
            # Get the raw JWT token (access token)
            jti = get_jwt()["jti"]
            revoked_tokens.add(jti)

            return jsonify({'message': 'Admin logout successful'}), 200
        except Exception as e:
            print(f"Error occurred during admin logout: {e}")
            return jsonify({'error': 'An unexpected error occurred'}), 500

api.add_resource(AdminLogout, '/adminLogout')

@app.route('/users/<int:id>', methods=["GET", "PATCH"])
def get_and_update_user_info_by_id(id):
    session = db.session()
    user = session.get(User,id)

    if request.method == 'GET':
        if not user:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify(user.to_dict()), 200
    
    if request.method == 'PATCH':
        data = request.json7

        if not data:
            return jsonify({'error': 'No data provided for update'}), 401
        
        if not user:
            return jsonify({'error': 'Item not found'}), 404
        
        for key, value in data.items():
            setattr(user, key, value)

        try:
            db.session.commit()
            return jsonify(user.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update item: {str(e)}'}), 500
        
@app.route('/admins/<int:id>', methods=["GET", "PATCH"])
def get_and_update_admin_info_by_id(id):
    session = db.session()
    admin = session.get(Admin,id)

    if request.method == 'GET':
        if not admin:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify(admin.to_dict()), 200
    
    if request.method == 'PATCH':
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided for update'}), 401
        
        if not admin:
            return jsonify({'error': 'Item not found'}), 404
        
        for key, value in data.items():
            setattr(admin, key, value)

        try:
            db.session.commit()
            return jsonify(admin.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update item: {str(e)}'}), 500

# Client side
@app.route('/userproducts', methods=['GET'])
def get_user_products():
    if request.method == 'GET':
        name = request.args.get('name')

        if name:
            # Perform search by name
            products = Product.query.filter(Product.name.ilike(f'%{name}%')).all()
        else:
            products = Product.query.all()

        return jsonify([product.to_dict() for product in products]), 200

@app.route('/userproducts/<int:id>', methods=['GET'])
def get_products_by_id(id):
    session = db.session()
    product = session.get(Product, id)

    if request.method == 'GET':
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product.to_dict()), 200
    
class ProductOrders(Resource):
    @jwt_required()
    def get(self):

        current_user_id = get_jwt_identity()
        orders = ProductOrder.query.filter_by(user_id=current_user_id).all()

        aggregated_orders = []

        for order in orders:
            order_details = {
                'order_id': order.id,
                'status': order.status,
                'total_price': float(sum(item.product.price * item.quantity for item in order.product_order_items)),
                'products': [{'name': item.product.name, 'quantity': item.quantity, 'image':item.product.image_url, 'price':item.product.price} for item in order.product_order_items]
            }
            aggregated_orders.append(order_details)
        
        return make_response(aggregated_orders, 200)

    @jwt_required()
    def post(self):

        data = request.json
        current_user_id = get_jwt_identity()

        try:
            new_product_order = ProductOrder(
                user_id=current_user_id,
                total_price=data.get("total"),
                status="pending"
            )
            # incase of a list of items 
            for item in data.get("items", []):
                product_id=item.get("id"),
                quantity=item.get("quantity")
                

                if product_id is None or quantity is None:
                    raise ValueError("Missing product ID or quantity")
                    
                product_order_item = ProductOrderItem(
                        product_id=product_id,
                        quantity=quantity
                )
                new_product_order.order_items.append(product_order_item)

            db.session.add(new_product_order)
            db.session.commit()

            print("This is the new product order", new_product_order)
            return make_response(new_product_order.to_dict(only=("id","status", "total_price")), 201)

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 400) 
        
api.add_resource(ProductOrders,"/userProductOrders")


# class ShoppingCart(Resource):
#     @jwt_required()
#     def get(self):
#         # Retrieve current user's ID
#         current_user_id = get_jwt_identity()

#         # Query database to find the user's cart
#         user_cart = Cart.query.filter_by(user_id=current_user_id).first()

#         if user_cart:
#             # Serialize the user's cart
#             serialized_cart = user_cart.to_dict()

#             # Optionally, include cart items
#             serialized_cart_items = []
#             for cart_item in user_cart.cart_items:
#                 serialized_cart_item = cart_item.to_dict()
#                 serialized_cart_items.append(serialized_cart_item)

#             # Add cart items to the serialized cart
#             serialized_cart['cart_items'] = serialized_cart_items

#             # Return serialized cart as JSON response
#             return jsonify(serialized_cart), 200
#         else:
#             return {'message': 'Cart not found'}, 404
        
#     def post(self):
#         current_user_id = get_jwt_identity()
#         data = request.json

#         try:
#             # Extract product or service ID and quantity from request data
#             product_id = data.get('product_id')
#             # service_id = data.get('service_id')
#             quantity = data.get('quantity')

#             # Ensure that either product_id or service_id is provided
#             if product_id:
#                 if not Product.query.filter_by(id=product_id).first():
#                     raise ValueError('Product with provided ID not found')
#             # elif service_id:
#             #     if not Service.query.filter_by(id=service_id).first():
#             #         raise ValueError('Service with provided ID not found')
#             else:
#                 raise ValueError('A product_id must be provided')

#             # Create a new cart item object based on the presence of product_id 
#             if product_id:
#                 new_cart_item = CartItem(
#                     cart_id=current_user_id,
#                     product_id=product_id,
#                     quantity=quantity
#                 )

#             # Add the new cart item to the user's cart
#             db.session.add(new_cart_item)

#             # Commit the changes to the database
#             db.session.commit()

#             # Serialize the new cart item
#             serialized_cart_item = new_cart_item.to_dict()

#             # Return the serialized cart item as the response
#             return jsonify(serialized_cart_item), 201

#         except Exception as e:
#             db.session.rollback()
#             return {'error': str(e)}, 400
        
#     def patch(self, item_id):
#         current_user_id = get_jwt_identity()
#         data = request.json

#         try:
#             # Extract updated quantity from request data
#             updated_quantity = data.get('quantity')

#             # Find the cart item with the specified item_id belonging to the current user
#             cart_item = CartItem.query.filter_by(id=item_id, cart_id=current_user_id).first()

#             if cart_item:
#                 # Update the quantity of the cart item
#                 cart_item.quantity = updated_quantity

#                 # Commit the changes to the database
#                 db.session.commit()

#                 # Serialize the updated cart item
#                 serialized_cart_item = cart_item.to_dict()

#                 # Return the serialized cart item as the response
#                 return jsonify(serialized_cart_item), 200
#             else:
#                 return {'error': 'Cart item not found'}, 404

#         except Exception as e:
#             db.session.rollback()
#             return {'error': str(e)}, 400
        
#     def delete(self, item_id):
#         current_user_id = get_jwt_identity()

#         try:
#             # Find the cart item with the specified item_id belonging to the current user
#             cart_item = CartItem.query.filter_by(id=item_id, cart_id=current_user_id).first()

#             if cart_item:
#                 # Delete the cart item from the database
#                 db.session.delete(cart_item)

#                 # Commit the changes to the database
#                 db.session.commit()

#                 return {'message': 'Cart item deleted successfully'}, 200
#             else:
#                 return {'error': 'Cart item not found'}, 404

#         except Exception as e:
#             db.session.rollback()
#             return {'error': str(e)}, 400

# api.add_resource(ShoppingCart,'/userCart')


#shopping NEW

class ShoppingCart(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user_cart = Cart.query.filter_by(user_id=current_user_id).first()

        if user_cart:
            serialized_cart = user_cart.to_dict()
            serialized_cart_items = [item.to_dict() for item in user_cart.cart_items]
            serialized_cart['cart_items'] = serialized_cart_items
            return jsonify(serialized_cart), 200
        else:
            return {'message': 'Cart not found'}, 404

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.json
        try:
            product_id = data.get('product_id')
            quantity = data.get('quantity')
            if product_id and quantity:
                new_cart_item = CartItem(cart_id=current_user_id, product_id=product_id, quantity=quantity)
                db.session.add(new_cart_item)
                db.session.commit()
                return jsonify(new_cart_item.to_dict()), 201
            else:
                raise ValueError('Invalid product_id or quantity')
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    @jwt_required()
    def patch(self, item_id):
        current_user_id = get_jwt_identity()
        data = request.json
        try:
            updated_quantity = data.get('quantity')
            cart_item = CartItem.query.filter_by(id=item_id, cart_id=current_user_id).first()
            if cart_item:
                cart_item.quantity = updated_quantity
                db.session.commit()
                return jsonify(cart_item.to_dict()), 200
            else:
                return {'error': 'Cart item not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    @jwt_required()
    def delete(self, item_id):
        current_user_id = get_jwt_identity()
        try:
            cart_item = CartItem.query.filter_by(id=item_id, cart_id=current_user_id).first()
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                return {'message': 'Cart item deleted successfully'}, 200
            else:
                return {'error': 'Cart item not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

api.add_resource(ShoppingCart, '/userCart', '/userCart/<int:item_id>')


class UserShippingDetails(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        details = ShippingAddress.query.filter_by(user_id=current_user_id).all()

        aggregated_details = []

        for detail in details:
            shipping_details = {
                'details_id': detail.id,
                'address_line1': detail.address_line1,
                'address_line2': detail.address_line2,
                'city': detail.city,
                'postal_code': detail.postal_code,
                'country': detail.country
            }
            aggregated_details.append(shipping_details)

        return make_response(aggregated_details, 200)
    

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.json

        new_shipping_details = ShippingAddress(
            address_line1=data.get('address_line1'),
            address_line2=data.get('address_line2'),
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            user_id=current_user_id
        )

        db.session.add(new_shipping_details)
        db.session.commit()

        return make_response(new_shipping_details.to_dict(), 201)
    
    @jwt_required()
    def patch(self):
        current_user_id = get_jwt_identity()
        data = request.json

        try:
            updated_address_line1 = data.get('address_line1')
            updated_address_line2 = data.get('address_line2')
            updated_city = data.get('city')
            updated_postal_code = data.get('postal_code')
            updated_country = data.get('country')

            # Query the shipping address for the current user
            user_shipping_address = ShippingAddress.query.filter_by(user_id=current_user_id).first()

            if user_shipping_address:
                # Update the address details
                user_shipping_address.address_line1 = updated_address_line1
                user_shipping_address.address_line2 = updated_address_line2
                user_shipping_address.city = updated_city
                user_shipping_address.postal_code = updated_postal_code
                user_shipping_address.country = updated_country

                # Commit the changes
                db.session.commit()

                return make_response(user_shipping_address.to_dict(), 200)
            else:
                return make_response({'error': 'Shipping address not found'}, 404)

        except Exception as e:
            db.session.rollback()
            return make_response({'error': str(e)}, 400)

api.add_resource(UserShippingDetails, '/userShippingAddress')


# Admin Side
@app.route('/adminproducts', methods=['GET','POST'])
def get_post_update_and_delete_products():
    products = Product.query.all()

    if request.method == 'GET':
        return jsonify([product.to_dict() for product in products]), 200
    
    if request.method == 'POST':
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided for create'}), 400
        
        # Input validation
        required_fields = ['pet' ,'name', 'description', 'price', 'image_url', 'type','quantity_available']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        name = data.get('name')
        pet = data.get('pet')
        description = data.get('description')
        price = data.get('price')
        image_url = data.get('image_url')
        quantity_available = data.get('quantity_available')
        type = data.get('type')

        new_product = Product(
            name=name,
            pet=pet,
            description=description,
            price=price,
            image_url=image_url,
            quantity_available=quantity_available,
            type=type
        )

        try:
            db.session.add(new_product)
            db.session.commit()
            return jsonify(new_product.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to create product: {str(e)}'}), 500




        
@app.route('/adminproducts/<int:id>', methods=['GET','PATCH','DELETE'])
def get_update_and_delete_products(id):
    session = db.session()
    product = session.get(Product, id)

    if request.method == 'GET':
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product.to_dict()), 200
    
    elif request.method == 'PATCH':
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided for update'}), 401

        if not product:
            return jsonify({'error': 'Item not found'}), 404
        
    
        for key, value in data.items():
            setattr(product, key, value)

        try:
            db.session.commit()
            return jsonify(product.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update product: {str(e)}'}), 500
        
    elif request.method == 'DELETE':
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        try:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'message': 'Product deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to delete product: {str(e)}'}), 500

class AdminProductOrders(Resource):
    def get(self):
        try:
            orders = ProductOrder.query.all()

            orders_data = []
            for order in orders:
                order_info = {
                    'order_id': order.id,
                    'total_price': order.total_price,
                    'user_id': order.user_id,
                    'status': order.status,
                    'items': []
                }

                # Eager loading to retrieve order items
                order_items = ProductOrderItem.query.filter_by(product_order_id=order.id).all()
                for item in order_items:
                    order_info['items'].append({
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'product_price': item.product.price,
                        'product_id': item.product.id,
                        'approval_status': item.approval_status  # Include approval status
                    })

                orders_data.append(order_info)

            return jsonify(orders_data), 200
        except Exception as e:
            return {'message': 'Failed to fetch product orders', 'error': str(e)}, 500

api.add_resource(AdminProductOrders, '/adminProductOrders')

@app.route('/approve_item/<int:item_id>', methods=['POST'])
def approve_item(item_id):
    try:
        item = ProductOrderItem.query.get_or_404(item_id)
        item.approval_status = 'Approved'
        db.session.commit()
        return jsonify({"message": f"Item {item_id} approved."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to approve item", "error": str(e)}), 500

@app.route('/disapprove_item/<int:item_id>', methods=['POST'])
def disapprove_item(item_id):
    try:
        item = ProductOrderItem.query.get_or_404(item_id)
        item.approval_status = 'Disapproved'
        db.session.commit()
        return jsonify({"message": f"Item {item_id} disapproved."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to disapprove item", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)
