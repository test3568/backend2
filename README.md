### Local Setup

### 1. Update submodule
```shell
git submodule update --init --remote
```

### 2. Follow steps for basic docker compose setup in `stack` repository

### 3. Install GDAL, GEOS: https://docs.djangoproject.com/en/5.1/ref/contrib/gis/install/geolibs/

### 4. Create `.env` file. Working example for docker-compose local deploy (replace GDAL_LIBRARY_PATH and GEOS_LIBRARY_PATH):
```dotenv
DJANGO_SECRET_KEY=eJWuyaUEO7W8SmiAR2AYmzmosHT25zTyRRx2sz8JA0buWvqppUHjVuFfESF9Vw4h
DJANGO_DEBUG=true
POSTGIS_HOST=localhost
POSTGIS_USER=postgres
POSTGIS_PASSWORD=pass
POSTGIS_PORT=9990
REDIS_HOST=localhost
REDIS_PORT=9991
KAFKA_HOST=localhost
KAFKA_PORT=9993
GDAL_LIBRARY_PATH=/opt/homebrew/Cellar/gdal/3.10.0_3/lib/libgdal.dylib
GEOS_LIBRARY_PATH=/opt/homebrew/Cellar/geos/3.13.0/lib/libgeos_c.dylib
KAFKA_CONSUMER_TOPIC=polygons
KAFKA_PRODUCER_TOPIC=polygons_back
DJANGO_LOG_LEVEL=INFO
APP_LOG_LEVEL=DEBUG
```

### 5. Install python dependencies
```shell
pip install -r requirements.txt
```

## Run

### Kafka consumer
```shell
python manage.py run_kafka_consumer
```
