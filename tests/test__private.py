from airly._private import _DictToObj
from unittest import TestCase

class _DictToObjTestCase(TestCase):
    def test_init_with_iterable(self):
        data = { 'key1': 'value1', 'key2': 2 }
        sut = _DictToObj(data)
        self.assertEqual('value1', sut['key1'])
        self.assertEqual('value1', sut.key1)
        self.assertEqual(2, sut['key2'])
        self.assertEqual(2, sut.key2)

    def test_init_with_kwargs(self):
        sut = _DictToObj(key1='value1', key2=2)
        self.assertEqual('value1', sut['key1'])
        self.assertEqual('value1', sut.key1)
        self.assertEqual(2, sut['key2'])
        self.assertEqual(2, sut.key2)
