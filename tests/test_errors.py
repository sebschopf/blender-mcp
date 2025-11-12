from blender_mcp import errors


def test_exceptions_exist_and_subclass_exception():
    assert issubclass(errors.BlenderMCPError, Exception)
    assert issubclass(errors.InvalidParamsError, errors.BlenderMCPError)
    assert issubclass(errors.PolicyDeniedError, errors.BlenderMCPError)
    assert issubclass(errors.HandlerNotFoundError, errors.BlenderMCPError)
