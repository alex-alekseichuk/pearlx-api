from flask_apscheduler import APScheduler
from apscheduler.triggers.cron import CronTrigger

from .tasks.refresh_from_timestream import refresh_from_timestream


scheduler = APScheduler()


def init_scheduler(app):
    scheduler.init_app(app)

    scheduler.add_job(
        id="refresh_from_timestream",
        func=refresh_from_timestream,
        args=(app,),
        trigger=CronTrigger.from_crontab(app.config["SCHEDULER_REFRESH_FROM_TIMESTREAM"]),
    )

    scheduler.start()
