import pytest
from click.testing import CliRunner
from src.cli.main import cli

def test_cli_help():
    """Testa o comando de ajuda do CLI"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output
    
def test_cli_version():
    """Testa o comando de versão do CLI"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '0.1.0' in result.output
    
def test_cli_run():
    """Testa o comando run do CLI"""
    runner = CliRunner()
    result = runner.invoke(cli, ['run'])
    assert result.exit_code == 0
    assert 'Starting Synapse' in result.output
    
def test_cli_config():
    """Testa o comando config do CLI"""
    runner = CliRunner()
    result = runner.invoke(cli, ['config'])
    assert result.exit_code == 0
    assert 'Current configuration:' in result.output 