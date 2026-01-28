from decimal import Decimal
from typing import Dict, Any, Optional
import requests
import logging
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

logger = logging.getLogger(__name__)


class ShippingService:
    """Service for handling shipping calculations and label generation."""
    
    def __init__(self):
        self.api_url = settings.SHIPPING_API_URL
        self.api_key = settings.SHIPPING_API_KEY
        self.timeout = getattr(settings, 'SHIPPING_API_TIMEOUT', 30)
    
    def calculate_shipping_cost(self, order_data: Dict[str, Any]) -> Decimal:
        """Calculate shipping cost for an order."""
        if not self._validate_order_data(order_data):
            raise ValidationError("Invalid order data provided")
        
        shipping_request = self._build_shipping_request(order_data)
        response_data = self._make_shipping_api_call(shipping_request)
        
        if response_data and 'cost' in response_data:
            return Decimal(str(response_data['cost']))
        
        return self._get_fallback_shipping_cost(order_data)
    
    def generate_shipping_label(self, order_id: int, shipping_address: Dict[str, str]) -> Optional[str]:
        """Generate shipping label and return tracking number."""
        label_request = self._build_label_request(order_id, shipping_address)
        response_data = self._make_shipping_api_call(label_request, endpoint='labels')
        
        if response_data and 'tracking_number' in response_data:
            self._save_tracking_info(order_id, response_data['tracking_number'])
            return response_data['tracking_number']
        
        logger.warning(f"Failed to generate shipping label for order {order_id}")
        return None
    
    def _validate_order_data(self, order_data: Dict[str, Any]) -> bool:
        """Validate required fields in order data."""
        required_fields = ['weight', 'dimensions', 'destination_zip', 'origin_zip']
        return all(field in order_data for field in required_fields)
    
    def _build_shipping_request(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build request payload for shipping cost calculation."""
        return {
            'service_type': 'standard',
            'weight': order_data['weight'],
            'dimensions': order_data['dimensions'],
            'origin': {'zip_code': order_data['origin_zip']},
            'destination': {'zip_code': order_data['destination_zip']},
            'package_type': order_data.get('package_type', 'box')
        }
    
    def _build_label_request(self, order_id: int, shipping_address: Dict[str, str]) -> Dict[str, Any]:
        """Build request payload for label generation."""
        return {
            'order_id': order_id,
            'service_type': 'standard',
            'address': shipping_address,
            'label_format': 'PDF'
        }
    
    def _make_shipping_api_call(self, payload: Dict[str, Any], endpoint: str = 'rates') -> Optional[Dict[str, Any]]:
        """Make API call to shipping provider."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_url}/{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Shipping API request failed: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse shipping API response: {e}")
            return None
    
    def _get_fallback_shipping_cost(self, order_data: Dict[str, Any]) -> Decimal:
        """Calculate fallback shipping cost when API is unavailable."""
        weight = Decimal(str(order_data['weight']))
        base_cost = Decimal('5.99')
        weight_multiplier = Decimal('0.50')
        
        return base_cost + (weight * weight_multiplier)
    
    @transaction.atomic
    def _save_tracking_info(self, order_id: int, tracking_number: str) -> None:
        """Save tracking information to database."""
        from .models import Order
        
        try:
            order = Order.objects.get(id=order_id)
            order.tracking_number = tracking_number
            order.shipping_status = 'label_generated'
            order.save(update_fields=['tracking_number', 'shipping_status'])
        except Order.DoesNotExist:
            logger.error(f"Order {order_id} not found when saving tracking info")