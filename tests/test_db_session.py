from app.db.session import make_mysql_url

from tests.conftest import make_settings


def test_make_mysql_url_uses_asyncmy_driver_and_existing_settings() -> None:
    settings = make_settings(
        mysql_host="db.example",
        mysql_port=3307,
        mysql_user="app_user",
        mysql_password="secret",
        mysql_database="fastapi_backend_template_test",
    )

    url = make_mysql_url(settings)

    assert url.drivername == "mysql+asyncmy"
    assert url.host == "db.example"
    assert url.port == 3307
    assert url.username == "app_user"
    assert url.password == "secret"
    assert url.database == "fastapi_backend_template_test"
    assert url.query == {"charset": "utf8mb4"}
