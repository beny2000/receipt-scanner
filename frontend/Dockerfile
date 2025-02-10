FROM node:18

WORKDIR /app

COPY receipt-scanner/package.json receipt-scanner/package-lock.json ./
RUN npm install
RUN npm install -g serve

COPY receipt-scanner/ .
RUN npm run build

CMD ["serve", "-s", "build"]

