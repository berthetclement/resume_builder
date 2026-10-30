import resume_builder


def test_public_api() -> None:
    # given
    expected = {
        "__version__",
        "init_resume",
        "render_resume",
        "render_pdf",
    }

    # then
    assert set(resume_builder.__all__) == expected
    for name in expected:
        assert hasattr(resume_builder, name), f"Make sure all functions ({name}) from '__ALL__' are well imported"
