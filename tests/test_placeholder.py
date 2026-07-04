"""Placeholder test — verifies CI pipeline works."""


def test_import():
    """项目包可以正常导入"""
    import liuzhai_ics  # noqa
    assert liuzhai_ics.__version__ == "1.0.0"
