import asyncio
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from product.application.factory.fetch_product_data_usecase_factory import FetchProductDataUsecaseFactory
from util.log.log import Log

logger = Log.get_logger()
from ecos.application.factory.fetch_ecos_data_usecase_factory import FetchEcosDataUsecaseFactory

load_dotenv()

cron_etf_hour = os.getenv("CRON_ETF_HOUR", "03")
cron_etf_minute = os.getenv("CRON_ETF_MINUTE", "00")
cron_bond_hour = os.getenv("CRON_FUND_HOUR", "04")
cron_bond_minute = os.getenv("CRON_FUND_MINUTE", "00")
cron_fund_hour = os.getenv("CRON_BOND_HOUR", "03")
cron_fund_minute = os.getenv("CRON_BOND_MINUTE", "30")

cron_exchange_hour = os.getenv("CRON_EXCHANGE_HOUR", "05")
cron_exchange_minute = os.getenv("CRON_EXCHANGE_MINUTE", "30")
cron_interest_hour = os.getenv("CRON_INTEREST_HOUR", "05")
cron_interest_minute = os.getenv("CRON_INTEREST_MINUTE", "00")

scheduler: AsyncIOScheduler | None = None


def create_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
        trigger = CronTrigger(hour=cron_exchange_hour, minute=cron_exchange_minute)
        scheduler.add_job(run_scheduler_ecos_exchange, trigger)

        trigger = CronTrigger(hour=cron_interest_hour, minute=cron_interest_minute)
        scheduler.add_job(run_scheduler_ecos_interest, trigger)

        trigger = CronTrigger(hour=cron_etf_hour, minute=cron_etf_minute)
        scheduler.add_job(run_scheduler_product_etf, trigger)
    return scheduler


def start_scheduler():
    sched = create_scheduler()
    if not sched.running:
        sched.start()
        logger.info("Scheduler started")


def stop_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


## 환율
async def run_scheduler_ecos_exchange():
    usecase = FetchEcosDataUsecaseFactory.create()
    await usecase.fetch_and_save_exchange_rate("", "")

## 환율
async def run_scheduler_ecos_interest():
    usecase = FetchEcosDataUsecaseFactory.create()
    await usecase.fetch_and_save_interest_rate("", "")

## ETF
async def run_scheduler_product_etf():
    usecase = FetchProductDataUsecaseFactory.create()
    await usecase.fetch_and_save_etf_data()
