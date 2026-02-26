# 🦞 bigdata_nanp — BigData stack (Batchs and stream over docker)
bigdata tps and stuffs

**Folders:**
- **[mysql](https://github.com/ngoupatrick/bigdata_nanp/tree/main/mysql)**: Contains sql scripts to setup mysql database
- **[nifi](https://github.com/ngoupatrick/bigdata_nanp/tree/main/nifi)**: docker labs to ingest datas from mysql database to minio throw nifi

## Versions

* SE: **Ubuntu 22.04.5 LTS**
* Runtime enviromment for test: **Docker version 29.1.5**.
* Browser: **Opera 126.x**
* Others versions: in **compose.yml**

## Install

### Docker (if not already installed)

- **[Install](https://docs.docker.com/engine/install/)**



```bash
# prerequises
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release -y

# Add GPG keys
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

# Update repository & install docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- **<u>Docker service</u>** 
```bash
# start & stop & status
sudo systemctl status docker
sudo systemctl start docker
sudo systemctl stop docker
```

- **<u>User access Config</u>**
```bash
# configure user
sudo groupadd docker # add group if not exist
sudo usermod -aG docker $USER
newgrp docker # Or restart session
```
---

### Portainer
```bash
# Create Docker Volume 'portainer_data'
sudo docker volume create --driver local --opt type=none --opt device={path_to_your_local_folder} --opt o=bind portainer_data

# Inspect the volume (check)
docker volume inspect portainer_data

# Start Portainer
sudo docker run -d -p 7003:8000 -p 7443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v /run/docker.sock:/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

#### Access from browser **`https://localhost:7443`**

---

### Run project & some cleaning ops

```bash
# Be sure to be in the folder with compose.yml file
# start all
docker compose up -d

# stop all and clean some volume
docker compose down -v --remove-orphans

# logs (you can also have access to logs on portainer)
docker logs -f {container}

# Bash access of specific container
docker exec -it {container} bash

# remove unused images
docker image prune -a

# remove all container not used for the last 24h
docker container prune --filter "until=24h"

# remove unused volume
docker volume prune
```