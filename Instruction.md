Security Architecture
1. Role-based access (`aas-user` for Read-only, `aas-admin` for Admin).
2. IP Whitelist: Nginx filtering using `.env` (`CUSTOMER_ALLOWED_IP`).
3. SSL Encrypted Gateway over `:8443`





1. Start System Infrastructure:
   make up-docker

2. Verify System Health:
   make check-all

3. Convert Excel & Upload AAS Data to BaSyx Servers:
   make run

4. Verify Security & Token Authentication:
   make check-token

5. Extract Quick Access Tokens (for AAS Web UI at http://localhost:3000):
   make get-user-token
   make get-admin-token

6. Issue New Customer Account (Direction 1):
   make add-customer USER={$custom} PASSWORD={$custom} ROLE=aas-user or aas-admin

7. Inspect Nginx Gateway Audit Logs:
   make check-logs-get
   make check-logs-post
   make check-logs-blocked


### when client ask data from MY server ###

1. Create Account
make add-customer USER=<username> PASSWORD=<password> ROLE=<aas-user or aas-admin>

2. Partner Requests Data from MY Nginx Gateway
curl -i -H "Authorization: Bearer <TOKEN>" http://<MY_IP>:8080/shells

3. Check Audit Logs
make check-logs-get 
make check-logs-post
make check-logs-blocked

### when MY server request data to partner server ###
need to test!
# first we need id and password
1.make request-partner IP=<PARTNER_IP> USER=<username> PASSWORD=<password>
