from setuptools import setup
from Cython.Build import cythonize
# ext = Extension(name='test', sources=['test.pyx'])

setup(ext_modules=cythonize('del_stop_word.pyx', compiler_directives={'language_level': "3"}))

# ————————————————
# 版权声明：本文为CSDN博主「Johnson0722」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/John_xyz/article/details/100068136
