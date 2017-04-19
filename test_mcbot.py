import pytest
from mcbot import Parser

@pytest.mark.parametrize('msg', [
    'Hey', 'How are you?', 'what\'s up', 'sup'])
def test_greetings(msg):
    parser = Parser(msg)
    assert parser.respond() in Parser.GREETINGS
    
    
    
