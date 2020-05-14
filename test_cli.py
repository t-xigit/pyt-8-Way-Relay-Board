import time
from click.testing import CliRunner
from k8_box import cli


def test_add():
    pass


def test_test_all():
    runner = CliRunner()
    result = runner.invoke(cli, ['test-all'])
    assert result.exit_code == 0


def test_set_all_off():
    runner = CliRunner()
    result = runner.invoke(cli, ['set-all-off'])
    assert result.exit_code == 0


def test_set_relay():
    runner = CliRunner()
    result = runner.invoke(cli, ['set-relay', '-r', '0', '-s', '1'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '1', '-s', '1'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '2', '-s', '1'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '3', '-s', '1'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '4', '-s', '1'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '5', '-s', '1'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '6', '-s', '1'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '7', '-s', '1'])
    time.sleep(0.5)

    result = runner.invoke(cli, ['set-relay', '-r', '0', '-s', '0'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '1', '-s', '0'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '2', '-s', '0'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '3', '-s', '0'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '4', '-s', '0'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '5', '-s', '0'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '6', '-s', '0'])
    time.sleep(0.5)
    result = runner.invoke(cli, ['set-relay', '-r', '7', '-s', '0'])
    time.sleep(0.5)
    assert result.exit_code == 0
