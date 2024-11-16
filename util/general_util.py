"""General utility functions."""


def remove_surrounding_quotes(s):
    """remove_surrounding_quotes removes surrounding quotes from a string."""
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith('\\"') and s.endswith('\\"'):
        return s[2:-2]
    return s


# Examples
print(remove_surrounding_quotes('"hello"'))  # Output: hello
print(remove_surrounding_quotes('\\"hello\\"'))  # Output: hello
print(remove_surrounding_quotes('hello'))  # Output: hello
