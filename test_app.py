from base_test import BaseTest


def test_app():
    testing_data = b'bla bla'
    with BaseTest(testing_data) as btest:
        assert testing_data == btest.http_test(("GET", "/get-hello"))
