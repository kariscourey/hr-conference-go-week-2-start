import json
import pika
import django
import os
import sys
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

host_name = "rabbitmq"


def process_approval(ch, method, properties, body):

    print("  Received %r" % body)

    queue_name = "presentation_approvals"

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

    connect_to_queue(queue_name, process_approval, host_name)


def process_rejection(ch, method, properties, body):

    print("  Received %r" % body)

    sent = send_mail(
        'Your presentation has been rejected',
        f"{presenter_name}, we're saddened to tell you that your presentation {presenter_title} has been rejected",
        'admin@conference.go',
        ['{presenter_email}'],
        fail_silently=False,
    )

    if sent:
        print("  Message sent regarding %r" % body)
    else:
        print("  Message failed to send regarding %r" % body)

    connect_to_queue(queue_name, process_rejection, host_name)


def connect_to_queue(queue_name, process_type, host_name):
    parameters = pika.ConnectionParameters(host=host_name)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=process_type,
        auto_ack=True,
    )
    channel.start_consuming()


def main():
    process_approval()
    process_rejection()

if __name__ == "main":
    main()
