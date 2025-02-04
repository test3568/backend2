import ujson
from confluent_kafka import Consumer, TopicPartition, KafkaError
import json
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection


from app.kafka import Kafka
from polygons.models import PolygonIntersection

from logger import logger

consumer_conf = {
    'bootstrap.servers': settings.KAFKA_SERVER,
    'group.id': 'polygons_back_consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'isolation.level': 'read_committed',
    'enable.partition.eof': False
}

consumer = Consumer(consumer_conf)
kafka = Kafka()

def consume_messages():
    consumer.assign([TopicPartition(settings.KAFKA_CONSUMER_TOPIC, 0)])
    try:
        while True:
            msg = consumer.poll(timeout=1)

            if msg is None:
                continue

            error = msg.error()
            if error:
                logger.error(f"Kafka poll error: {error}")
                if error.code() == KafkaError.NOT_COORDINATOR:
                    logger.warning(f"NOT_COORDINATOR error code, exiting")
                continue

            # noinspection PyArgumentList
            msg_value = msg.value()
            try:
                message = json.loads(msg_value.decode('utf-8'))
            except json.decoder.JSONDecodeError:
                logger.error(f"Message JSONDecodeError: {msg_value}")
                continue

            logger.debug(f"Received message: {message}")
            message['error'] = False
            message['intersection_polygon_ids'] = 0
            try:
                message = process_message(message)
            except Exception:
                logger.exception(f'Unknown error with task: {message}')
                message['error'] = True
            finally:
                message_dump = json.dumps(message)
                kafka.add(message_dump)
                consumer.commit(asynchronous=False)

    except KeyboardInterrupt:
        logger.warning("Consumer interrupted.")
    finally:
        consumer.close()


def process_message(message):
    if message['antimeridian_crossing']:
        for coordinate in message['polygon']['coordinates'][0]:
            if coordinate[0] < 0:
                coordinate[0] += 360
    crossing_polygon = GEOSGeometry(str(message['polygon']), srid=4326).json
    with connection.cursor() as cursor:
        cursor.execute("""
        WITH transformed_polygons AS (
            SELECT id,
                   ST_SetSRID(ST_GeomFromText(
                           'POLYGON((' ||
                           string_agg(
                                   CASE
                                       WHEN ST_X((dump.point).geom) < 0 AND antimeridian_crossing IS TRUE THEN
                                           ST_X((dump.point).geom) + 360 || ' ' || ST_Y((dump.point).geom)
                                       ELSE
                                           ST_X((dump.point).geom) || ' ' || ST_Y((dump.point).geom)
                                       END
                               , ',')
                               || '))'
                   ), 4326) as transformed_geom
            FROM (SELECT id, ST_DumpPoints(polygon) AS point, antimeridian_crossing FROM polygons_polygon) as dump
            GROUP BY dump.id
        )
        SELECT transformed_polygons.id
        FROM transformed_polygons,
             (SELECT ST_GeomFromGeoJSON(%s) AS new_geom) AS new_polygon
        WHERE ST_Intersects(transformed_polygons.transformed_geom, new_polygon.new_geom)
        """, [crossing_polygon])
        rows = cursor.fetchall()
        intersection_ids = [i[0] for i in rows]
        if message['editing_polygon_id'] and message['editing_polygon_id'] in intersection_ids:
            intersection_ids.remove(message['editing_polygon_id'])

    if intersection_ids:
        message['intersection_polygon_ids'] = intersection_ids
        polygon_dump = ujson.dumps(message['polygon'])
        pi = PolygonIntersection(
            name=message['name'], polygon=polygon_dump, antimeridian_crossing=message['antimeridian_crossing'],
            edited_polygon_id=message['editing_polygon_id'], intersection_polygon_ids=intersection_ids
        )
        pi.save()
        message['intersection_id'] = pi.id
    return message
