"""Tests for searches involving wildcards (*, ?)"""

from dxr.testing import SingleFileTestCase, MINIMAL_MAIN


class WildcardTests(SingleFileTestCase):
    """Tests for searches involving wildcards (*, ?)"""

    source = r"""
        int get_foo() {
            return 0;
        }
        
        int get_bar() {
            return 0;
        }
        
        int getX() {
            return 0;
        }

        int main() {
          return get_foo() + get_bar() + getX();
        }
        """

    def test_function_asterisk(self):
        """Test searching for functions using an asterisk."""
        self.found_lines_eq(
            'function:get*',
            [
                ('int <b>get_foo</b>() {', 2),
                ('int <b>get_bar</b>() {', 6),
                ('int <b>getX</b>() {', 10),
            ])

    def test_function_question(self):
        """Test searching for functions using a question mark."""
        self.found_lines_eq(
            'function:get_fo?',
            [
                ('int <b>get_foo</b>() {', 2),
            ])

    def test_function_underscore(self):
        """Test that underscore is treated literally when searching for functions."""
        self.found_nothing(
            'function:get_',
            [
            ])

    def test_function_ref_asterisk(self):
        """Test searching for function references using an asterisk."""
        self.found_lines_eq(
            'function-ref:get*',
            [
                ('return <b>get_foo</b>() + <b>get_bar</b>() + <b>getX</b>();', 15),
            ])

    def test_function_ref_question(self):
        """Test searching for function references using a question mark."""
        self.found_lines_eq(
            'function-ref:get_fo?',
            [
                ('return <b>get_foo</b>() + get_bar() + getX();', 15),
            ])

    def test_function_ref_underscore(self):
        """Test that underscore is treated literally when searching for function references."""
        self.found_nothing(
            'function-ref:get_',
            [
            ])
