FROM alpine:latest

# Installation des outils une fois pour toutes
RUN apk add --no-cache \
    curl \
    bash \
    mysql-client

# Dossier de travail
WORKDIR /

# On ne copie pas encore les scripts ici pour garder 
# la flexibilité du montage de volume pendant le dev
#ENTRYPOINT ["/bin/bash"]
