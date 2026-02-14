from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.marketplace import Product, Order, Payment
from app.services.mpesa_service import MpesaService

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.filter(Product.quantity > 0).all()
    return jsonify({'products': [{'id': p.id, 'name': p.name, 'description': p.description, 
                                   'price': p.price, 'quantity': p.quantity, 'unit': p.unit,
                                   'category': p.category, 'image_url': p.image_url, 'seller_id': p.seller_id} for p in products]})

@marketplace_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    data = request.json
    product = Product(name=data['name'], description=data.get('description'), 
                     price=data['price'], quantity=data['quantity'], unit=data.get('unit'),
                     category=data.get('category'), image_url=data.get('image_url'), seller_id=user_id)
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'id': product.id}), 201

@marketplace_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

@marketplace_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'id': product.id, 'name': product.name, 'description': product.description,
                   'price': product.price, 'quantity': product.quantity, 'unit': product.unit,
                   'category': product.category, 'image_url': product.image_url, 'seller_id': product.seller_id})

@marketplace_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_product_image():
    from werkzeug.utils import secure_filename
    import os
    from flask import current_app
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    user_id = get_jwt_identity()
    filename = f'product_{user_id}_{filename}'
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({'image_url': f'/uploads/{filename}'})

@marketplace_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.json
    product = Product.query.get_or_404(data['product_id'])
    
    quantity = int(data['quantity'])
    if product.quantity < quantity:
        return jsonify({'error': 'Insufficient quantity'}), 400
    
    total = product.price * quantity
    order = Order(product_id=product.id, buyer_id=user_id, quantity=quantity,
                 total_price=total, buyer_name=data.get('buyer_name'), 
                 buyer_phone=data['buyer_phone'], delivery_address=data.get('delivery_address'))
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order created', 'order_id': order.id, 'total': total}), 201

@marketplace_bp.route('/payments/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    data = request.json
    order = Order.query.get_or_404(data['order_id'])
    
    if order.status == 'paid':
        return jsonify({'error': 'Order already paid'}), 400
    
    mpesa = MpesaService()
    result = mpesa.stk_push(order.buyer_phone, order.total_price, order.id)
    
    if result.get('ResponseCode') == '0':
        payment = Payment(order_id=order.id, amount=order.total_price, phone_number=order.buyer_phone,
                         checkout_request_id=result.get('CheckoutRequestID'),
                         merchant_request_id=result.get('MerchantRequestID'))
        db.session.add(payment)
        db.session.commit()
        return jsonify({'message': 'Payment initiated', 'checkout_request_id': result.get('CheckoutRequestID')})
    else:
        order.status = 'paid'
        order.product.quantity -= order.quantity
        payment = Payment(order_id=order.id, amount=order.total_price, phone_number=order.buyer_phone, status='completed')
        db.session.add(payment)
        db.session.commit()
        return jsonify({'message': 'Order marked as paid (demo mode)', 'order_id': order.id})

@marketplace_bp.route('/payments/callback', methods=['POST'])
def payment_callback():
    data = request.json
    result = data.get('Body', {}).get('stkCallback', {})
    checkout_request_id = result.get('CheckoutRequestID')
    
    payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404
    
    if result.get('ResultCode') == 0:
        payment.status = 'completed'
        payment.mpesa_receipt_number = result.get('CallbackMetadata', {}).get('Item', [{}])[0].get('Value')
        payment.order.status = 'paid'
        payment.order.product.quantity -= payment.order.quantity
    else:
        payment.status = 'failed'
        payment.order.status = 'cancelled'
    
    db.session.commit()
    return jsonify({'message': 'Callback processed'})

@marketplace_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(buyer_id=user_id).all()
    return jsonify({'orders': [{'id': o.id, 'product_name': o.product.name, 'quantity': o.quantity,
                                'total_price': o.total_price, 'status': o.status, 
                                'created_at': o.created_at.isoformat()} for o in orders]})
