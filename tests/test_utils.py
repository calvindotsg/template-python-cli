from template_python_cli.utils import InputError, error_message


def test_input_error_is_exception() -> None:
    assert issubclass(InputError, Exception)
    assert str(InputError("x")) == "x"


def test_error_message_with_message() -> None:
    assert error_message(InputError("boom")) == "boom"


def test_error_message_empty_fallback() -> None:
    assert error_message(RuntimeError()) == "RuntimeError"
