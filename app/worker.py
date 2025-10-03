# app/worker.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .core.db import SessionLocal
from .models.product import Product
from .scraper.runner import scrape_once
from random import randint
from time import sleep

scheduler = BackgroundScheduler()

@scheduler.scheduled_job("interval", hours=3)
def job():
    db: Session = SessionLocal()
    try:
        for product in db.query(Product).all():
            try:
                scrape_once(db, product)
            except Exception as e:
                print("erro scraping", product.id, e)
    finally:
        db.close()

if __name__ == "__main__":
    scheduler.start()
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
