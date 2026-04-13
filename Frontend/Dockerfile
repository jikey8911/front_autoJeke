FROM node:20-alpine

WORKDIR /app

# Instalar pnpm
RUN npm install -g pnpm

# Copiar archivos de dependencias
COPY package.json pnpm-lock.yaml ./

# Instalar dependencias
RUN pnpm install

# Copiar el resto del código
COPY . .

EXPOSE 5173

# Iniciar servidor de desarrollo exponiendo al exterior
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
