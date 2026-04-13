FROM node:20-alpine

WORKDIR /app

# 1. Instalar git (Vital para dependencias externas de GitHub)
# --no-cache mantiene la imagen pequeña al no guardar los índices de paquetes
RUN apk add --no-cache git

# 2. Instalar pnpm
RUN npm install -g pnpm

# 3. Copiar archivos de dependencias
COPY package.json pnpm-lock.yaml ./

# 4. Instalar dependencias 
# (Ahora pnpm podrá usar git para descargar @jikey8911/jeikei-ui)
RUN pnpm install

# 5. Copiar el resto del código
COPY . .

EXPOSE 3000

# Iniciar servidor de desarrollo exponiendo al exterior
CMD ["pnpm", "dev", "--host", "0.0.0.0"]