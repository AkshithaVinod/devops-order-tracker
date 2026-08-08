from flask import Blueprint, jsonify, request
from app.database import db
from app.models import Order
from sqlalchemy.exc import IntegrityError

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "service": "order-tracker",
            "database": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@api_bp.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "Order Tracker API",
        "version": "1.0.0",
        "database": "PostgreSQL",
        "endpoints": {
            "health": "/api/health",
            "orders": "/api/orders",
            "order_detail": "/api/orders/<id>"
        }
    }), 200

@api_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        paginated = db.paginate(
            db.select(Order).order_by(Order.created_at.desc()),
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            "orders": [order.to_dict() for order in paginated.items],
            "total": paginated.total,
            "page": page,
            "per_page": per_page,
            "pages": paginated.pages
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/orders', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        data = request.get_json()
        
        # Validation
        if not data or not all(k in data for k in ['customer_name', 'product', 'quantity']):
            return jsonify({"error": "Missing required fields: customer_name, product, quantity"}), 400
        
        if not isinstance(data['quantity'], int) or data['quantity'] <= 0:
            return jsonify({"error": "Quantity must be a positive integer"}), 400
        
        # Create order
        order = Order(
            customer_name=data['customer_name'],
            product=data['product'],
            quantity=data['quantity'],
            status=data.get('status', 'pending')
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify(order.to_dict()), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order"""
    try:
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        return jsonify(order.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update order"""
    try:
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'customer_name' in data:
            order.customer_name = data['customer_name']
        if 'product' in data:
            order.product = data['product']
        if 'quantity' in data:
            if not isinstance(data['quantity'], int) or data['quantity'] <= 0:
                return jsonify({"error": "Quantity must be a positive integer"}), 400
            order.quantity = data['quantity']
        if 'status' in data:
            order.status = data['status']
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete order"""
    try:
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/orders/stats/summary', methods=['GET'])
def order_stats():
    """Get order statistics"""
    try:
        total_orders = db.session.query(Order).count()
        pending_orders = db.session.query(Order).filter_by(status='pending').count()
        shipped_orders = db.session.query(Order).filter_by(status='shipped').count()
        completed_orders = db.session.query(Order).filter_by(status='completed').count()
        
        return jsonify({
            "total_orders": total_orders,
            "pending": pending_orders,
            "shipped": shipped_orders,
            "completed": completed_orders
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500