# ref: https://docs.gunicorn.org/en/stable/settings.html

bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
loglevel = "info"
accesslog = "-"  # stdout
access_log_format = '%(M)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
