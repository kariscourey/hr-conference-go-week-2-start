import json
import pika
import django
import inspect
import os
import sys
import time
from django.core.mail import send_mail
from pika.exceptions import AMQPConnectionError


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval(ch, method, properties, body):

    print("  Received %r" % body)

    body_dict = json.loads(body)

    presenter_name = body_dict["presenter_name"]
    presenter_email = body_dict["presenter_email"]
    title = body_dict["title"]

    sent = send_mail(
        'Your presentation has been accepted',
        f"{presenter_name}, we're happy to tell you that your presentation {title} has been accepted",
        'admin@conference.go',
        [presenter_email],
        fail_silently=False,
    )

    if sent:
        print("  Message sent with body %r" % body)
    else:
        print("  Message failed to send with body %r" % body)


def process_rejection(ch, method, properties, body):

    print("  Received %r" % body)

    body_dict = json.loads(body)

    presenter_name = body_dict["presenter_name"]
    presenter_email = body_dict["presenter_email"]
    title = body_dict["title"]

    sent = send_mail(
        'Your presentation has been rejected',
        f"{presenter_name}, we're saddened to tell you that your presentation {title} has been rejected",
        'admin@conference.go',
        [presenter_email],
        fail_silently=False,
    )

    if sent:
        print("  Message sent regarding %r" % body)
    else:
        print("  Message failed to send regarding %r" % body)



def connect_to_queue(host_name, processes):
    parameters = pika.ConnectionParameters(host=host_name)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    for i in processes:
        channel.queue_declare(queue=i["queue_name"])
        channel.basic_consume(
            queue=i["queue_name"],
            on_message_callback=i["process_type"],
            auto_ack=True,
        )

    channel.start_consuming()


while True:
    try:

        host_name = "rabbitmq"

        processes = [
            {
                "process_type": process_approval,
                "queue_name": "presentation_approvals",
            },
            {
                "process_type": process_rejection,
                "queue_name": "presentation_rejections",
            }
        ]

        connect_to_queue(host_name, processes)

    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)



# def main():
#     while True:
#         try:

#             host_name = "rabbitmq"

#             processes = [
#                 {
#                     "process_type": process_approval,
#                     "queue_name": "presentation_approvals",
#                 },
#                 {
#                     "process_type": process_rejection,
#                     "queue_name": "presentation_rejections",
#                 }
#             ]

#             # connect_to_queue(host_name, processes)

#             parameters = pika.ConnectionParameters(host=host_name)
#             connection = pika.BlockingConnection(parameters)
#             channel = connection.channel()

#             for i in processes:
#                 channel.queue_declare(queue=i["queue_name"])
#                 channel.basic_consume(
#                     queue=i["queue_name"],
#                     on_message_callback=i["process_type"],
#                     auto_ack=True,
#                 )

#             channel.start_consuming()

#         except AMQPConnectionError:
#             print("Could not connect to RabbitMQ")
#             time.sleep(2.0)


# if __name__ == "main":
#     main()
