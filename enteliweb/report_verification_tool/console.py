'''
Created on Nov 25, 2015

@author: hwang
'''
from cmd import Cmd
from test.test_support import args_from_interpreter_flags


class Console(Cmd):
    
    def do_hello(self, args):
        """
        Says hello. If you provide a name, it will greet you with it.
        """
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print "Hello, %s"% name
        
    def do_quit(self, args):
        """
        Quits the program
        """
        raise SystemExit
    
    def do_setup(self, args):
        i = SetupCLI()
        i.prompt = '[Setup]' + self.prompt
        i.cmdloop()
    
    
class SetupCLI(Cmd):
    
    def do_Hi(self, args):
        """
        say hi
        """
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print "Hi, %s"% name
    
    def do_return(self, args):
        """
        exit from setup CLI
        """
        return True
    
    
if __name__ == '__main__':
    prompt = Console()
    prompt.prompt = '=>>'
    prompt.cmdloop('Starting prompt ...')