import pytest
from app.models import Order
from app.database import db

class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_check(self, client):
        """Test health check returns healthy status"""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
        assert response.json['database'] == 'connected'
    
    def test_index(self, client):
        """Test index endpoint"""
        response = client.get('/api/')
        assert response.status_code == 200
        assert response.json['service'] == 'Order Tracker API'

class TestOrderCRUD:
    """Order CRUD operations"""
    
    def test_create_order(self, client):
        """Test creating an order"""
        order_data = {
            "customer_name": "John Doe",
            "product": "Laptop",
            "quantity": 1
        }
        response = client.post('/api/orders', json=order_data)
        assert response.status_code == 201
        assert response.json['customer_name'] == 'John Doe'
        assert response.json['status'] == 'pending'
    
    def test_create_order_missing_fields(self, client):
        """Test creating order with missing fields"""
        order_data = {"customer_name": "Jane Doe"}
        response = client.post('/api/orders', json=order_data)
        assert response.status_code == 400
        assert 'Missing required fields' in response.json['error']
    
    def test_create_order_invalid_quantity(self, client):
        """Test creating order with invalid quantity"""
        order_data = {
            "customer_name": "Jane Smith",
            "product": "Mouse",
            "quantity": -1
        }
        response = client.post('/api/orders', json=order_data)
        assert response.status_code == 400
        assert 'Quantity must be a positive integer' in response.json['error']
    
    def test_get_orders_empty(self, client):
        """Test getting orders when none exist"""
        response = client.get('/api/orders')
        assert response.status_code == 200
        assert response.json['total'] == 0
        assert response.json['orders'] == []
    
    def test_get_orders_with_data(self, client):
        """Test getting orders with data"""
        # Create orders
        order_data = {"customer_name": "Alice", "product": "Keyboard", "quantity": 2}
        client.post('/api/orders', json=order_data)
        client.post('/api/orders', json=order_data)
        
        response = client.get('/api/orders')
        assert response.status_code == 200
        assert response.json['total'] == 2
        assert len(response.json['orders']) == 2
    
    def test_get_order_by_id(self, client):
        """Test getting a specific order"""
        # Create order
        order_data = {"customer_name": "Bob", "product": "Monitor", "quantity": 1}
        create_response = client.post('/api/orders', json=order_data)
        order_id = create_response.json['id']
        
        # Get the order
        response = client.get(f'/api/orders/{order_id}')
        assert response.status_code == 200
        assert response.json['product'] == 'Monitor'
    
    def test_get_order_not_found(self, client):
        """Test getting non-existent order"""
        response = client.get('/api/orders/999')
        assert response.status_code == 404
        assert 'Order not found' in response.json['error']
    
    def test_update_order_status(self, client):
        """Test updating order status"""
        # Create order
        order_data = {"customer_name": "Charlie", "product": "Headphones", "quantity": 1}
        create_response = client.post('/api/orders', json=order_data)
        order_id = create_response.json['id']
        
        # Update status
        update_data = {"status": "shipped"}
        response = client.put(f'/api/orders/{order_id}', json=update_data)
        assert response.status_code == 200
        assert response.json['status'] == 'shipped'
    
    def test_update_order_all_fields(self, client):
        """Test updating all order fields"""
        # Create order
        order_data = {"customer_name": "Diana", "product": "Tablet", "quantity": 1}
        create_response = client.post('/api/orders', json=order_data)
        order_id = create_response.json['id']
        
        # Update all fields
        update_data = {
            "customer_name": "Diana Updated",
            "product": "Laptop",
            "quantity": 2,
            "status": "completed"
        }
        response = client.put(f'/api/orders/{order_id}', json=update_data)
        assert response.status_code == 200
        assert response.json['customer_name'] == 'Diana Updated'
        assert response.json['quantity'] == 2
    
    def test_delete_order(self, client):
        """Test deleting an order"""
        # Create order
        order_data = {"customer_name": "Eve", "product": "Webcam", "quantity": 1}
        create_response = client.post('/api/orders', json=order_data)
        order_id = create_response.json['id']
        
        # Delete the order
        response = client.delete(f'/api/orders/{order_id}')
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f'/api/orders/{order_id}')
        assert get_response.status_code == 404

class TestOrderStats:
    """Order statistics"""
    
    def test_order_stats(self, client):
        """Test order statistics endpoint"""
        # Create orders with different statuses
        client.post('/api/orders', json={"customer_name": "F1", "product": "P1", "quantity": 1})
        
        create_response = client.post('/api/orders', json={"customer_name": "F2", "product": "P2", "quantity": 1})
        order_id = create_response.json['id']
        client.put(f'/api/orders/{order_id}', json={"status": "shipped"})
        
        response = client.get('/api/orders/stats/summary')
        assert response.status_code == 200
        assert response.json['total_orders'] == 2
        assert response.json['pending'] == 1
        assert response.json['shipped'] == 1