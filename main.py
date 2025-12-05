# # run.py — starts the Flask app
# import os
# from app import create_app

# if __name__ == "__main__":
#     env = os.environ.get("FLASK_ENV", "production")
#     app = create_app()
#     debug = env == "development" or os.environ.get("FLASK_DEBUG") == "1"
#     app.run(host="0.0.0.0", port=5000, debug=debug)


# from app import create_app, db
# from flask_migrate import Migrate

# app = create_app()
# migrate = Migrate(app, db)

# if __name__ == "__main__":
#     app.run(debug=True)


from app import create_app, db
from app.models import Teacher,ClassRoom

app = create_app()

# Optional: add access to models in the shell
@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Teacher": Teacher, "Classroom": ClassRoom}

if __name__ == "__main__":
    app.run(debug=True)
