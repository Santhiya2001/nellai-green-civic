FROM node:20-slim

# In networks that terminate TLS with a certificate only the system CA
# store trusts (not Node's bundled one), npm install hangs on TLS
# handshakes with no clear error. Point Node at the system store.
ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
