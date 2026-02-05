# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copy package.json only for caching
# Copy package.json only for caching
COPY package*.json ./
# 切换国内淘宝源 (修复网络问题)
RUN npm config set registry https://registry.npmmirror.com
RUN npm ci

# Copy source code
COPY . .

# Build
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config (optional, using default for now)
# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
