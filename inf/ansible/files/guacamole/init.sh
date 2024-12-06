# https://krdesigns.com/articles/how-to-install-guacamole-using-docker-step-by-step
docker compose up -d
sleep 15
docker run --rm guacamole/guacamole:1.4.0 /opt/guacamole/bin/initdb.sh --mysql > initdb.sql
docker cp initdb.sql guacamoledb:/initdb.sql
docker cp dbinit.sh guacamoledb:/dbinit.sh
docker exec -it guacamoledb /dbinit.sh