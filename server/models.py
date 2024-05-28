from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates, relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from sqlalchemy.orm import relationship

class Admin(db.Model, SerializerMixin):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String, nullable=False, default='admin')  

    @validates('password')
    def validate_password(self, key, password):
        if len(password) < 8:
            raise ValueError('Password must be more than 8 characters.')
        return password

    def __repr__(self):
        return f"<Admin(id={self.id}, username='{self.username}')>"

class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    
    role = db.Column(db.String, nullable=False, default='client')
    confirm_password = db.Column(db.String(80), nullable=True)

    productorders = relationship("ProductOrder", back_populates="user")
    cart = relationship("Cart", uselist=False, back_populates="user")

    serialize_rules = ('-productorders.user', '-cart.user')

    @validates('password')
    def validate_password(self, key, password):
        if len(password) < 8:
            raise ValueError('Password must be more than 8 characters.')
        return password
    
    @validates('email')
    def validate_email(self, key, email):
        if not email.endswith("@gmail.com"):
            raise ValueError("Email is not valid. It should end with @gmail.com")
        return email

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Product(db.Model, SerializerMixin):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    pet=db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String, nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)

    # Added seller_id to the Product model to establish a relationship with the Admin model, representing the seller of the product.
    seller_id = db.Column(db.Integer, db.ForeignKey('admins.id')) 

    product_order_items = relationship("ProductOrderItem", back_populates="product")

    serialize_rules = ('-product_order_items.product', '-seller.products.product_order_items')

    def __repr__(self):
        return f'<Product {self.name} from seller {self.seller_id}>'

class ProductOrder(db.Model, SerializerMixin):
    __tablename__ = "productorders"

    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)

    # Added user_id to the ProductOrder model to establish a relationship with the User model, representing the user who placed the order.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Added a relationship attribute user to the ProductOrder model to access the user who placed the order.
    user = relationship("User", back_populates="productorders")

    #Added order_items relationship to the ProductOrder model to represent the items in the order.
    product_order_items = relationship("ProductOrderItem", back_populates="product_order")
    shipping_address = relationship("ShippingAddress", back_populates="product_order")

    serialize_rules = ('-product_order_items.product_order', '-user.productorders.product_order_items')

    def __repr__(self):
        return f'<ProductOrder {self.id}>'

class ProductOrderItem(db.Model, SerializerMixin):
    __tablename__ = "productorderitems"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    product_order_id = db.Column(db.Integer, db.ForeignKey('productorders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    approval_status = db.Column(db.String, nullable=False, default="Pending")

    #Added product_order and product relationships to the ProductOrderItem model to represent the order and product associated with each item, respectively.
    product_order = relationship("ProductOrder", back_populates="product_order_items")
    product = relationship("Product", back_populates="product_order_items")

    serialize_rules = ('-product_order.product_order_items.product', '-product.product_order_items', '-shipping_address')


    def __repr__(self):
        return f'<OrderItem {self.id}>'

    
class Cart(db.Model, SerializerMixin):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="cart")
    cart_items = relationship("CartItem", back_populates="cart")

    serialize_rules = ('-user.cart', '-cart_items.cart')

    def __repr__(self):
        return f'<Cart {self.id}>'

class CartItem(db.Model, SerializerMixin):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)

    product = relationship("Product")
    cart = relationship("Cart", back_populates="cart_items")

    serialize_rules = ('-cart.cart_items', '-product')

    def __repr__(self):
        return f'<CartItem {self.id}>'

class ShippingAddress(db.Model, SerializerMixin):
    __tablename__ = "shipping_addresses"

    id = db.Column(db.Integer, primary_key=True)
    address_line1 = db.Column(db.String, nullable=False)
    address_line2 = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)

    product_order_id = db.Column(db.Integer, db.ForeignKey('productorders.id'))
    

    product_order = relationship("ProductOrder", back_populates="shipping_address")


    serialize_rules = ('-product_order.shipping_address',)

    def __repr__(self):
        return f'<ShippingAddress {self.id}>'
