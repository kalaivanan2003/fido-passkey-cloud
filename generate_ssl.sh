#!/bin/bash

# ============================================================
#   Generate a self-signed SSL certificate for HTTPS
#   Run ONCE on your EC2:  bash generate_ssl.sh
#   Then restart App.py — camera will work over HTTPS
# ============================================================

set -e

CERT_DIR="$(dirname "$(realpath "$0")")/ssl"
mkdir -p "$CERT_DIR"

echo "🔐 Generating self-signed SSL certificate..."

# Get public IP automatically
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || \
            curl -s https://api.ipify.org 2>/dev/null || \
            hostname -I | awk '{print $1}')

echo "   Using IP: $PUBLIC_IP"

# Create OpenSSL config with Subject Alternative Name (required by modern browsers)
cat > "$CERT_DIR/openssl.cnf" << EOF
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
x509_extensions    = v3_req

[dn]
C  = IN
ST = TamilNadu
L  = Chennai
O  = FIDO Cloud
CN = $PUBLIC_IP

[v3_req]
subjectAltName = @alt_names
keyUsage       = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
IP.1 = $PUBLIC_IP
IP.2 = 127.0.0.1
EOF

# Generate private key + self-signed certificate (valid 825 days)
openssl req -x509 -nodes -days 825 \
    -newkey rsa:2048 \
    -keyout "$CERT_DIR/key.pem" \
    -out    "$CERT_DIR/cert.pem" \
    -config "$CERT_DIR/openssl.cnf"

echo ""
echo "✅ SSL certificate created:"
echo "   cert: $CERT_DIR/cert.pem"
echo "   key:  $CERT_DIR/key.pem"
echo ""
echo "🌐 Your app will be available at:"
echo "   https://$PUBLIC_IP:5000"
echo ""
echo "⚠️  Browser will show 'Not secure / Certificate warning'"
echo "   Click  Advanced → Proceed to $PUBLIC_IP (unsafe)"
echo "   This is expected for self-signed certs — camera WILL work."
echo ""
echo "➡️  Now restart your app:  python App.py"
