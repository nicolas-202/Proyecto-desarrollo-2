# Etapa 1: Build de la aplicación
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# Etapa 2: Servidor nginx para servir la app
FROM nginx:alpine

# Copiar build de React a nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
