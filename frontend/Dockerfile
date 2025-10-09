# Usar uma imagem leve do Nginx para servir HTML estático
FROM nginx:alpine

# Copiar todos os arquivos do frontend para o diretório padrão do Nginx
COPY . /usr/share/nginx/html

# Expor a porta 80 (porta padrão do Nginx)
EXPOSE 80

# O Nginx já inicia automaticamente com o comando padrão
