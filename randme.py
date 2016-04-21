from random import _urandom
print _urandom(32).encode('base-64')[:-2]
