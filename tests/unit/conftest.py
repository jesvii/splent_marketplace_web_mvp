import pytest

import app as marketplace_app


@pytest.fixture
def app():
    flask_app = marketplace_app.create_app()
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
