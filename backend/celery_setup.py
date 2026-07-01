from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    celery.conf.beat_schedule = {
        'daily-interview-reminders': {
            'task': 'tasks.send_interview_reminders',
            'schedule': crontab(hour=8, minute=0), 
        },
        # MONTHLY PLACEMENT REPORT ---
        'monthly-placement-reports': {
            'task': 'tasks.send_monthly_reports',
            # Runs on the 1st day of every month at 9:00 AM
            'schedule': crontab(day_of_month='1', hour=9, minute=0),
        }
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery