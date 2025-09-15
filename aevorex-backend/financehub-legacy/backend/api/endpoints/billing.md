# Billing Endpoints

**Category:** Billing  
**Total Endpoints:** 1  
**Authentication:** Not required (webhook)  
**Caching:** No caching

This category handles payment processing webhooks and subscription management.

---

## 1. POST /api/v1/billing/lemonsqueezy

**Description:** LemonSqueezy webhook handler for processing payment events and subscription updates.

**Parameters:**
- **Body:**
  - Webhook payload (object, required): LemonSqueezy webhook data

**Request Body:**
```json
{
  "meta": {
    "event_name": "order_created",
    "custom_data": {
      "user_id": "user123"
    }
  },
  "data": {
    "type": "order",
    "id": "12345",
    "attributes": {
      "store_id": 12345,
      "customer_id": 67890,
      "identifier": "order_abc123",
      "order_number": 1,
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "currency": "USD",
      "currency_rate": "1.00",
      "subtotal": 1000,
      "discount_total": 0,
      "tax": 0,
      "total": 1000,
      "subtotal_usd": 1000,
      "discount_total_usd": 0,
      "tax_usd": 0,
      "total_usd": 1000,
      "tax_name": null,
      "tax_rate": "0.00",
      "status": "paid",
      "status_formatted": "Paid",
      "refunded": false,
      "refunded_at": null,
      "subtotal_formatted": "$10.00",
      "discount_total_formatted": "$0.00",
      "tax_formatted": "$0.00",
      "total_formatted": "$10.00",
      "first_order_item": {
        "id": 11111,
        "order_id": 12345,
        "product_id": 22222,
        "variant_id": 33333,
        "product_name": "Pro Plan",
        "variant_name": "Monthly",
        "price": 1000,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      },
      "urls": {
        "receipt": "https://lemonsqueezy.com/receipt/abc123"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Webhook processed successfully",
  "event_type": "order_created",
  "order_id": "12345",
  "user_id": "user123",
  "subscription_tier": "pro",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response Fields:**
- `status` (string): Processing status ("success", "error")
- `message` (string): Processing message
- `event_type` (string): Webhook event type
- `order_id` (string): Order identifier
- `user_id` (string): User identifier
- `subscription_tier` (string): Updated subscription tier
- `timestamp` (string): Processing timestamp

**Behavior:**
- No authentication required (webhook endpoint)
- No caching
- Processes payment events asynchronously
- Updates user subscription status
- Sends confirmation emails

**Usage:**
```bash
curl -X POST https://api.aevorex.com/api/v1/billing/lemonsqueezy \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "event_name": "order_created",
      "custom_data": {
        "user_id": "user123"
      }
    },
    "data": {
      "type": "order",
      "id": "12345",
      "attributes": {
        "store_id": 12345,
        "customer_id": 67890,
        "identifier": "order_abc123",
        "order_number": 1,
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "currency": "USD",
        "total": 1000,
        "status": "paid",
        "first_order_item": {
          "id": 11111,
          "order_id": 12345,
          "product_id": 22222,
          "variant_id": 33333,
          "product_name": "Pro Plan",
          "variant_name": "Monthly",
          "price": 1000
        }
      }
    }
  }'
```

---

## Webhook Events

### **Order Events**
- **order_created**: New order placed
- **order_updated**: Order status updated
- **order_refunded**: Order refunded

### **Subscription Events**
- **subscription_created**: New subscription created
- **subscription_updated**: Subscription updated
- **subscription_cancelled**: Subscription cancelled
- **subscription_resumed**: Subscription resumed
- **subscription_expired**: Subscription expired

### **Payment Events**
- **payment_success**: Payment successful
- **payment_failed**: Payment failed
- **payment_refunded**: Payment refunded

---

## Event Processing

### **Order Created**
1. Validate webhook signature
2. Extract user information
3. Create or update user subscription
4. Send welcome email
5. Update user permissions
6. Log transaction

### **Subscription Updated**
1. Validate webhook signature
2. Update subscription status
3. Modify user permissions
4. Send notification email
5. Log changes

### **Payment Failed**
1. Validate webhook signature
2. Update subscription status
3. Send payment failure notification
4. Log failure reason
5. Schedule retry (if applicable)

---

## Security Features

### **Webhook Validation**
- Signature verification using LemonSqueezy secret
- IP whitelist validation
- Timestamp validation to prevent replay attacks
- Payload integrity checks

### **Data Protection**
- Encrypted storage of payment data
- PCI DSS compliance
- GDPR compliance for EU users
- Secure transmission (HTTPS only)

---

## Error Handling

### **Invalid Signature**
```json
{
  "status": "error",
  "message": "Invalid webhook signature",
  "code": 401
}
```

### **Processing Error**
```json
{
  "status": "error",
  "message": "Failed to process webhook",
  "code": 500,
  "retry_after": 300
}
```

### **Validation Error**
```json
{
  "status": "error",
  "message": "Invalid webhook payload",
  "code": 400
}
```

---

## Integration Examples

### **LemonSqueezy Configuration**
```javascript
// Webhook endpoint configuration
const webhookConfig = {
  url: 'https://api.aevorex.com/api/v1/billing/lemonsqueezy',
  events: [
    'order_created',
    'order_updated',
    'order_refunded',
    'subscription_created',
    'subscription_updated',
    'subscription_cancelled',
    'subscription_resumed',
    'subscription_expired',
    'payment_success',
    'payment_failed',
    'payment_refunded'
  ],
  secret: 'your_webhook_secret_here'
};
```

### **Webhook Processing**
```python
import requests
import hashlib
import hmac
import json

def process_lemonsqueezy_webhook(payload, signature, secret):
    # Verify signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        json.dumps(payload).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return {"status": "error", "message": "Invalid signature"}
    
    # Process webhook
    event_type = payload.get('meta', {}).get('event_name')
    data = payload.get('data', {})
    
    if event_type == 'order_created':
        return process_order_created(data)
    elif event_type == 'subscription_updated':
        return process_subscription_updated(data)
    # ... handle other events
    
    return {"status": "success", "message": "Webhook processed"}

def process_order_created(data):
    # Extract order information
    order_id = data.get('id')
    attributes = data.get('attributes', {})
    user_email = attributes.get('user_email')
    total = attributes.get('total')
    
    # Update user subscription
    # ... subscription logic
    
    return {
        "status": "success",
        "message": "Order processed successfully",
        "order_id": order_id
    }
```

---

## Monitoring and Logging

### **Webhook Monitoring**
- Real-time webhook processing status
- Failed webhook retry mechanism
- Processing time metrics
- Error rate monitoring

### **Audit Logging**
- All webhook events logged
- User subscription changes tracked
- Payment events recorded
- Security events monitored

---

**Total Billing Endpoints: 1** ✅

