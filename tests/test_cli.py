from ctk.cli import main


def test_version_command(capsys):
    code = main(["version"])
    out = capsys.readouterr().out
    assert code == 0
    assert "0.2.0" in out


def test_help_command(capsys):
    code = main([])
    out = capsys.readouterr().out
    assert code == 0
    assert "CallMeTK OS" in out
