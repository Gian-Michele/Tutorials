# Certificate creation steps #
The procedure to create may differ in different situations. Normally you create a certificate, and than you make it validate by a *Trusted Third Party* (*TTP*), that is a *Certification Authority* (*CA*). In some case you may need a certificate recognized only by yourself, in order to make a **TLS connection** between recognized devices or software. In this case you prepare a *self-signed certificate*.


## Create a certificate and make it sign by a Certification Authority (CA) ##
In this case you are going to use a TTP to be recognized, and to sign your certificate. Steps are the following:

1. Create a **Certificate Signing Request** (**CSR**);
2. Send the **CSR** to a *Trusted Third Party* (*TTP*);
3. Follow the specific procedure of the TTP to get your information verified;
4. Generate a **Public Key**. The TTP signs your CSR;
5. Now you can issue your verified Public Key.

Here, the private key is related to the CSR, like the public key and the certificate itself.


## Creating a CA a certificate and make it sign by a Certification Authority (CA) ##
In this case you are going to use "yourself" to be recognized, and to sign your certificate. Steps are the following:

1. Creating the **Certification Authority** (**CA**);
   1. Create a private key (`rootca.key`);
   2. Use the private key to self-sign a public key (`rootca.crt`);
   3. Now you have a CA certificate to use to sign other certificates;
2. Create a **Certificate Signing Request** (CSR) to be used by the newly CA;
   1. Create a private key (`server.key`);
   2. Generate the CSR (`server.req`);
3. **Sign the CSR** using the CA keys;
   1. Create a public key using the CA public and private keys together with the CSR (`server.crt`);


## Verify the certificates using openssl tool ##
You can use the following command to check that the certificate is valid against the CA root certificate:
        
    openssl verify -CAfile rootca.crt server.crt