###############################################
# ATTENTION - This script generates a root CA #
# certificate and than a server certificate,  #
# and signs it with this root CA certificate  #
###############################################

# When providing a client of https to connect to a server with certificate, you need to
# give to the client the Root CA certificate used to sign the server certificate. So:
# RootCA -> used to sign Server cert
# Server -> uses Server cert
# Client -> Validates Server cert with RootCA cert

# 1. Creating a Root CA self-signed certificate
# Generating a private key for the Root CA (Certification Authority)
openssl genrsa -aes256 -out rootca.key 2048
# Generating the public key (Certificate) for the CA using the private key
openssl req \
        -new \
        -nodes \
        -batch \
        -key rootca.key \
        -x509 \
        -out rootca.crt \
        -days 3650 \
        -subj "/C=IT/ST=Italy/L=Turin/O=Tim S.p.A CA/OU=WAI group/CN=TIM Root CA"

#2. Creating a server certificate using the Root CA self-signed certificate as CA
# Generating a private server key and a Certificate Signing Request (CSR)
openssl req \
        -new \
        -nodes \
        -newkey rsa:2048 \
        -keyout server.key \
        -out server.req \
        -batch \
        -subj "/C=IT/ST=Italy/L=Turin/O=Tim S.p.A/OU=WAI group controller_tim/CN=163.162.89.28" \
        -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:163.162.89.28,IP:163.162.89.28"))
# Signing the CSR using the Root CA certificate
openssl x509 \
        -req \
        -in server.req \
        -CA rootca.crt \
        -CAkey rootca.key \
        -CAcreateserial \
        -out server.crt \
        -days 3650 \
        -sha256 \
        -extfile <(printf "subjectAltName=DNS:163.162.89.28,IP:163.162.89.28")