from resume_builder import main


def test_main_prints_greeting(capsys: object) -> None:
    main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert captured.out == "Hello from resume-builder!\n"
