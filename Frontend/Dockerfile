FROM node:20-alpine

WORKDIR /app

# Instalar git y bash (bash es útil para entrar al contenedor a debugear)
RUN apk add --no-cache git bash

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
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]