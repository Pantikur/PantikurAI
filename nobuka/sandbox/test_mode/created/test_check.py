#!/usr/bin/env python3
class TestModule:
    def __init__(self):
        self.name = 'test'
    
    def run(self):
        return True

def validate():
    m = TestModule()
    return m.run()

if __name__ == '__main__':
    validate()
