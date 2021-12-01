from flask.templating import render_template
from werkzeug.utils import redirect
from .import bp as shop
from .models import Product, Cart
from flask import redirect, url_for, flash, current_app as app
import stripe
from flask_login import current_user
from app import db


@shop.route('/')
def index():
    print(current_user.get_id())
    stripe.api_key = app.config.get('STRIPE_TEST_SK')
    context = {
        'products': stripe.Product.list()
    }
    return render_template('shop/index.html', **context)

@shop.route('/product/add/<id>')
def add_product(id):
    cart_item = Cart.query.filter_by(product_key=str(id)).filter_by(user_id=current_user.get_id()).first()
    # if cart item already exists, increment its quantity by 1 and UPDATE the database
    if cart_item:
        cart_item.quantity += 1
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('shop.cart'))
    # otherwise, create the new item and add it to the database
    cart_item = Cart(product_key=id, user_id=current_user.get_id(), quantity=1)
    db.session.add(cart_item)
    db.session.commit()
    flash('Product added successfully', 'success')
    return redirect(url_for('shop.index'))


@shop.route('/cart/remove/<id>')
def remove_product(id):
    Cart.query.filter_by(product_key=str(id)).filter_by(user_id=current_user.get_id()).delete()
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('shop.cart'))
    
@shop.route('/cart')
def cart():
    stripe.api_key = app.config.get('STRIPE_TEST_SK')
    cart_items = []
    for i in Cart.query.filter_by(user_id=current_user.get_id()).all():
        stripe_product = stripe.Product.retrieve(i.product_key)
        product_dict = {
            'product': stripe_product,
            'price': float(stripe.Price.retrieve(stripe_product['metadata']['price_id'])['unit_amount']) / 100,
            'quantity': i.quantity
        }
        cart_items.append(product_dict)
    context = {
        'cart': cart_items
    }
    return render_template('shop/cart.html', **context)

@shop.route('/checkout', methods=['POST'])
def create_checkout_session():
    stripe.api_key = app.config.get('STRIPE_TEST_SK')
    items = []
    for i in Cart.query.filter_by(user_id=current_user.get_id()).all():
        stripe_product = stripe.Product.retrieve(i.product_key)
        product_dict = {
            'price': stripe.Price.retrieve(stripe_product['metadata']['price_id']),
            'quantity': i.quantity
        }
        items.append(product_dict)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=items,
            mode='payment',
            success_url='http://localhost:5000/shop/success',
            cancel_url='http://localhost:5000/shop/cancel',
        )
    except Exception as error:
        return str(error)
    return redirect(checkout_session.url, code=303)

@shop.route('/success/')
def clear_cart():
    Cart.query.filter_by(product_key=str(id)).filter_by(user_id=current_user.get_id()).delete()
    db.session.commit()
    context = {
    }
    return render_template('shop/success.html', **context)

#     @shop.route('/cart/remove/<id>')
# def remove_product(id):
#     Cart.query.filter_by(product_key=str(id)).filter_by(
#         user_id=current_user.get_id()).delete()
#     db.session.commit()
#     flash('Product deleted successfully', 'success')
#     return redirect(url_for('shop.cart'))
