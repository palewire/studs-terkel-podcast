"""
Saves the Flask app to a static files in the ./docs/ directory.
"""
from flask_frozen import Freezer
from app import app

app.config.update(
    FREEZER_DESTINATION='./docs/'
)
freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()
