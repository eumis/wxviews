import wx
from wxviews.app import register_dependencies, launch

def run_sandbox():
    register_dependencies()
    launch('app')

if __name__ == '__main__':
    run_sandbox()
