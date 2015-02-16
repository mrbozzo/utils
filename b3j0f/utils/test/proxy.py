#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

from unittest import main

from inspect import getargspec, isbuiltin, getmembers, isroutine

from b3j0f.utils.ut import UTCase
from b3j0f.utils.proxy import (
    get_proxy, proxify_routine, proxify_elt, proxified_elt, is_proxy
)


class ProxyRoutineTest(UTCase):
    """Test proxy routine function.
    """

    def _assert_routine(self, routine, _get_proxy=True):
        """Assert properties on a proxified routine.

        :param routine: routine to proxify.
        :param bool get_proxy: (private) play get_routine if True.
        """

        # get proxy
        proxy = get_proxy(routine) if _get_proxy else proxify_routine(routine)

        try:
            func_argspec = getargspec(routine)
        except TypeError:
            pass
        else:
            proxy_argspec = getargspec(proxy)
            self.assertEqual(func_argspec, proxy_argspec)

        if not isbuiltin(routine):
            self.assertIs(routine.__class__, proxy.__class__)
            self.assertIsNot(proxy.__dict__, routine.__dict__)
        self.assertEqual(proxy.__name__, routine.__name__)
        self.assertEqual(proxy.__doc__, routine.__doc__)
        self.assertEqual(proxy.__module__, proxify_routine.__module__)
        # assert proxified element is routine
        proxified = proxified_elt(proxy)
        self.assertIs(proxified, routine)
        # repeat assertion with proxify_routine function
        if _get_proxy:
            self._assert_routine(routine, _get_proxy=False)

    def test_function_empty(self):

        def test(a, b=1, *args, **kwargs):
            """Default test function.
            """
            pass

        self._assert_routine(test)

    def test_builtin(self):
        """Test to proxify a builtin function
        """

        self._assert_routine(min, True)

    def test_lambda(self):
        """Test lambda expression.
        """

        self._assert_routine(lambda a, b=2, *args, **kwargs: None)

    def test_method(self):
        """Test to proxify a method.
        """

        self._assert_routine(self.test_method)


class ProxyEltTest(UTCase):
    """Test proxy elt function.
    """

    def _assert_elt(self, add_bases=False, add_dict=None):
        """Assert to proxify an elt.
        """

        class A(object):
            def a(self):
                pass

        class B:
            def b(self):
                pass

        class C(A, B):
            def test(self):
                pass

        elt = C()

        bases = (elt.__class__.__base__,) if add_bases else None
        _dict = {'test': lambda: None} if add_dict else None

        proxy = proxify_elt(elt, bases=bases, _dict=_dict)

        if add_bases:
            # check if forgave bases are not proxified
            for base in elt.__class__.__bases__[1:]:
                self.assertNotIsInstance(proxy, base)
            # check if gave bases are proxified
            for base in bases:
                self.assertIsInstance(proxy, base)
                for name, member in getmembers(base, lambda m: isroutine(m)):
                    elt_member = getattr(elt, name, None)
                    if hasattr(elt_member, '__func__'):
                        elt_member = elt_member.__func__
                        proxy_member = getattr(proxy, name).__func__
                        proxified_member = proxified_elt(proxy_member)
                        proxified_member = getattr(
                            proxified_member, '__func__', proxified_member
                        )
                        self.assertIs(proxified_member, elt_member)
                        if not isbuiltin(elt_member):
                            self.assertIs(
                                elt_member.__class__, proxy_member.__class__
                            )
                            self.assertIsNot(
                                elt_member.__dict__, proxy_member.__dict__
                            )
                        self.assertEqual(
                            elt_member.__name__, proxy_member.__name__
                        )
                        self.assertEqual(
                            elt_member.__doc__, proxy_member.__doc__
                        )
                        self.assertEqual(
                            proxy_member.__module__, proxify_elt.__module__
                        )

        if add_dict:
            for name in _dict:
                member = _dict[name]
                proxy_member = getattr(proxy, name)
                proxified_member = proxified_elt(proxy_member)
                proxified_member = getattr(
                    proxified_member, '__func__', proxified_member
                )
                self.assertIs(proxified_member, member)

    def test_elt(self):
        """Test to proxify an elt.
        """

        self._assert_elt()

    def test_elt_bases(self):
        """Test to proxify an elt with bases.
        """

        self._assert_elt(add_bases=True)

    def test_elt_dict(self):
        """Test to proxify an elt with _dict.
        """

        self._assert_elt(add_dict=True)

    def test_elt_bases_dict(self):
        """Test to proxify an elt with bases and _dict.
        """

        self._assert_elt(add_bases=True, add_dict=True)


if __name__ == '__main__':
    main()
