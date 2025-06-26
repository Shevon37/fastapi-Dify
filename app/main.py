from core.Router import router
from fastapi import FastAPI
from config import settings
from core import Events


application = FastAPI(
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)


# 事件监听
print("ok")
application.add_event_handler("startup", Events.startup(application))
application.add_event_handler("shutdown", Events.stop(application))
app = application
app.include_router(router)
