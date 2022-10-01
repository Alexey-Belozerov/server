from celery import shared_task


@shared_task
def bar():
    return 'Привет Django Celery Redis'
