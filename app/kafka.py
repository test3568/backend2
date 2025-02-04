from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from django.conf import settings

from logger import logger


class Kafka:
    def __init__(self):
        self.topic = settings.KAFKA_PRODUCER_TOPIC

        self.producer = Producer({
            'bootstrap.servers': settings.KAFKA_SERVER,
            'acks': 'all'
        })

        self.admin = AdminClient({
            "bootstrap.servers": settings.KAFKA_SERVER,
        })
        topic_list = [
            NewTopic("polygons", 1, 1),
            NewTopic("polygons_back", 1, 1)
        ]
        self.admin.create_topics(topic_list)

    def delivery_callback(self, err, msg):
        if err:
            logger.error('ERROR: Message failed delivery: {}. Retrying...'.format(err))
            self.add(msg)
        else:
            logger.debug(f"Produced event to topic {msg.topic()}: key = {msg.key()} value = {msg.value()}")

    def add(self, message: str):
        self.producer.produce(self.topic, message, callback=self.delivery_callback)
        self.producer.poll(10000)
        self.producer.flush()


kafka = Kafka()
