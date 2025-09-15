#!/bin/bash
# End-to-End Webhook Testing Script

echo "🧪 LemonSqueezy Webhook End-to-End Test"
echo "========================================"

# 1. Generate signature for subscription_created
echo "📝 Generating signature for subscription_created..."
SIGNATURE_CREATED=$(python3 gen_signature.py subscription_created.json | grep "X-Signature:" | cut -d' ' -f2)
echo "Signature: $SIGNATURE_CREATED"

# 2. Test subscription_created webhook
echo ""
echo "🚀 Testing subscription_created webhook..."
curl -s -X POST http://localhost:8084/api/v1/billing/lemonsqueezy \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIGNATURE_CREATED" \
  -d @subscription_created.json | jq '.'

echo ""
echo "⏳ Waiting 2 seconds..."
sleep 2

# 3. Generate signature for subscription_updated
echo ""
echo "📝 Generating signature for subscription_updated..."
SIGNATURE_UPDATED=$(python3 gen_signature.py subscription_updated.json | grep "X-Signature:" | cut -d' ' -f2)
echo "Signature: $SIGNATURE_UPDATED"

# 4. Test subscription_updated webhook
echo ""
echo "🔄 Testing subscription_updated webhook..."
curl -s -X POST http://localhost:8084/api/v1/billing/lemonsqueezy \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIGNATURE_UPDATED" \
  -d @subscription_updated.json | jq '.'

echo ""
echo "⏳ Waiting 2 seconds..."
sleep 2

# 5. Test duplicate webhook (idempotency)
echo ""
echo "🔄 Testing duplicate webhook (idempotency)..."
curl -s -X POST http://localhost:8084/api/v1/billing/lemonsqueezy \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIGNATURE_CREATED" \
  -d @subscription_created.json | jq '.'

echo ""
echo "⏳ Waiting 2 seconds..."
sleep 2

# 6. Test invalid signature
echo ""
echo "❌ Testing invalid signature..."
curl -s -X POST http://localhost:8084/api/v1/billing/lemonsqueezy \
  -H "Content-Type: application/json" \
  -H "X-Signature: invalid_signature_123" \
  -d @subscription_created.json | jq '.'

echo ""
echo "✅ End-to-End Test Complete!"
echo ""
echo "🔍 Check Supabase for results:"
echo "SELECT * FROM users ORDER BY created_at DESC LIMIT 5;"
echo "SELECT * FROM subscriptions ORDER BY created_at DESC LIMIT 5;"
echo "SELECT * FROM webhook_events ORDER BY received_at DESC LIMIT 5;"
