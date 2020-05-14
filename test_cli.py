from click.testing import CliRunner
from k8_box import cli

# Unit Test

def test_test_all():
	runner = CliRunner()
	result = runner.invoke(cli, ['test-all'])
	assert result.exit_code == 0
