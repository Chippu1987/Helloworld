import main
import unittest

class TestHelloWorld(unittest.TestCase):
    
    def test_hello_world(self):
        func_output=main.hello_world(self)
        print(func_output)
        self.assertEqual(func_output,'Hello DevX - Github Actions!')

if __name__ == '__main__':
    unittest.main()
