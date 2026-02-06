from time import sleep
from celery import shared_task

# Example function to send a lot of emails, a big process to use with celery 
@shared_task
def notify_customers(message):
    print('Sending 10k emails...')
    print(message)
    # Manual delay
    sleep(10)
    print('Emails were successfuly sent!')