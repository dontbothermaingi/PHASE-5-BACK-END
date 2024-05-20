import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from test_config import TestConfig

# Import the models
from models import db, Product, ProductOrder, ProductOrderItem, Cart, CartItem, ShippingAddress

@pytest.fixture(scope='module')
def test_app():
    """Setup Flask test application"""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    db.init_app(app)

    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def init_db(test_app):
    """Setup the database for testing"""
    db.create_all()

    # Create some sample data
    product = Product(name="Sample Product", description="This is a sample product.", price=9.99, image_url="http://example.com/image.jpg", quantity_available=10, type=1)
    db.session.add(product)
    db.session.commit()

    yield db

    db.session.remove()
    db.drop_all()

@pytest.fixture
def new_product(init_db):
    """Fixture to create a new product"""
    return Product(name="New Product", description="This is a new product.", price=19.99, image_url="http://example.com/newimage.jpg", quantity_available=5, type=2)

def test_product_creation(init_db, new_product):
    """Test product creation"""
    db.session.add(new_product)
    db.session.commit()
    product = Product.query.get(new_product.id)
    assert product is not None
    assert product.name == "New Product"

def test_product_order_creation(init_db):
    """Test product order creation"""
    order = ProductOrder(total_price=19.98, status="Pending")
    db.session.add(order)
    db.session.commit()
    assert order.id is not None

def test_product_order_item_creation(init_db):
    """Test product order item creation"""
    order = ProductOrder(total_price=19.98, status="Pending")
    db.session.add(order)
    db.session.commit()

    product = Product.query.first()
    order_item = ProductOrderItem(quantity=2, product_order_id=order.id, product_id=product.id)
    db.session.add(order_item)
    db.session.commit()
    assert order_item.id is not None

def test_cart_creation(init_db):
    """Test cart creation"""
    cart = Cart()
    db.session.add(cart)
    db.session.commit()
    assert cart.id is not None

def test_cart_item_creation(init_db):
    """Test cart item creation"""
    cart = Cart()
    db.session.add(cart)
    db.session.commit()

    product = Product.query.first()
    cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=1)
    db.session.add(cart_item)
    db.session.commit()
    assert cart_item.id is not None

def test_shipping_address_creation(init_db):
    """Test shipping address creation"""
    address = ShippingAddress(address_line1="123 Main St", city="Anytown", postal_code="12345", country="USA")
    db.session.add(address)
    db.session.commit()
    assert address.id is not None