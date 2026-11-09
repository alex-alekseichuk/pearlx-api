import os

from src.pearlx_api_flex import create_app, db
from src.pearlx_api_flex.scheduler import init_scheduler


app = create_app(os.getenv("FLASK_ENV", "development"))

if app.config["SCHEDULER_ENABLED"]:
    init_scheduler(app)


@app.shell_context_processor
def shell():
    return {"db": db}


if __name__ == "__main__":
    debug = bool(int(os.getenv("FLASK_DEBUG", 0)))
    app.run(host="0.0.0.0", debug=debug)
