from unittest import TestCase

from text_history import TextHistory, InsertAction, ReplaceAction, DeleteAction

class TextHistoryTestCase(TestCase):
    def test_text__trivial(self):
        h = TextHistory()

        self.assertEqual('', h.text)
        with self.assertRaises(AttributeError):
            h.text = 'NEW'

    def test_version__trivial(self):
        h = TextHistory()

        self.assertEqual(0, h.version)
        with self.assertRaises(AttributeError):
            h.version = 42

    def test_action(self):
        h = TextHistory()
        action = InsertAction(pos=0, text='abc', from_version=0, to_version=10)

        self.assertEqual(10, h.action(action))
        self.assertEqual('abc', h.text)
        self.assertEqual(10, h.version)

    def test_action__bad(self):
        h = TextHistory()
        action = InsertAction(pos=0, text='abc', from_version=10, to_version=10)

        with self.assertRaises(ValueError):
            h.action(action)

    def test_insert(self):
        h = TextHistory()

        self.assertEqual(1, h.insert('abc'))
        self.assertEqual('abc', h.text)
        self.assertEqual(1, h.version)

        self.assertEqual(2, h.insert('xyz', pos=2))
        self.assertEqual('abxyzc', h.text)
        self.assertEqual(2, h.version)

        self.assertEqual(3, h.insert('END'))
        self.assertEqual('abxyzcEND', h.text)
        self.assertEqual(3, h.version)

        self.assertEqual(4, h.insert('BEGIN', pos=0))
        self.assertEqual('BEGINabxyzcEND', h.text)
        self.assertEqual(4, h.version)

    def test_insert__bad(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc'))

        with self.assertRaises(ValueError):
            h.insert('abc', pos=10)

        with self.assertRaises(ValueError):
            h.insert('abc', pos=-1)

    def test_replace(self):
        h = TextHistory()

        self.assertEqual(1, h.replace('abc'))
        self.assertEqual('abc', h.text)
        self.assertEqual(1, h.version)

        self.assertEqual(2, h.replace('xyz', pos=2))
        self.assertEqual('abxyz', h.text)
        self.assertEqual(2, h.version)

        self.assertEqual(3, h.replace('X', pos=2))
        self.assertEqual('abXyz', h.text)
        self.assertEqual(3, h.version)

        self.assertEqual(4, h.replace('END'))
        self.assertEqual('abXyzEND', h.text)
        self.assertEqual(4, h.version)

    def test_replace__bad(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc'))

        with self.assertRaises(ValueError):
            h.replace('abc', pos=10)

        with self.assertRaises(ValueError):
            h.replace('abc', pos=-1)

    def test_delete(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc xyz'))

        self.assertEqual(2, h.delete(pos=1, length=2))
        self.assertEqual('a xyz', h.text)
        self.assertEqual(2, h.version)

        self.assertEqual(3, h.delete(pos=3, length=0))
        self.assertEqual('a xyz', h.text)
        self.assertEqual(3, h.version)

    def test_delete__bad(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc'))

        with self.assertRaises(ValueError):
            h.delete(pos=10, length=2)

        with self.assertRaises(ValueError):
            h.delete(pos=1, length=3)

        with self.assertRaises(ValueError):
            h.delete(pos=-1, length=2)

    def test_get_actions(self):
        h = TextHistory()
        h.insert('a')
        h.insert('bc')
        h.replace('B', pos=1)
        h.delete(pos=0, length=1)
        self.assertEqual('Bc', h.text)

        actions = h.get_actions(1)

        self.assertEqual(3, len(actions))
        insert, replace, delete = actions
        self.assertIsInstance(insert, InsertAction)
        self.assertIsInstance(replace, ReplaceAction)
        self.assertIsInstance(delete, DeleteAction)

        # insert
        self.assertEqual(1, insert.from_version)
        self.assertEqual(2, insert.to_version)
        self.assertEqual('bc', insert.text)
        self.assertEqual(1, insert.pos)

        # replace
        self.assertEqual(2, replace.from_version)
        self.assertEqual(3, replace.to_version)
        self.assertEqual('B', replace.text)
        self.assertEqual(1, replace.pos)

        # delete
        self.assertEqual(3, delete.from_version)
        self.assertEqual(4, delete.to_version)
        self.assertEqual(0, delete.pos)
        self.assertEqual(1, delete.length)

    def test_get_actions__bad(self):
        h = TextHistory()
        h.insert('a')
        h.insert('b')
        h.insert('c')

        with self.assertRaises(ValueError):
            h.get_actions(0, 10)
        with self.assertRaises(ValueError):
            h.get_actions(10, 10)
        with self.assertRaises(ValueError):
            h.get_actions(2, 1)
        with self.assertRaises(ValueError):
            h.get_actions(-1, 1)

    def test_get_actions__empty(self):
        h = TextHistory()
        self.assertEqual([], h.get_actions())

        h.insert('a')
        self.assertEqual([], h.get_actions(0, 0))


class TestOptimization(TestCase):
    def test_insert_trivial(self):
        h = TextHistory()
        h.insert('abcd qwe')
        h.replace('A', pos=0)
        h.insert('gg', pos=2)
        h.insert('pop', pos=7)
        #pdb.set_trace()
        actions = h.get_actions(1)
        self.assertEqual(3, len(actions))
        
        v1, v2, v3 = actions
        self.assertEqual('A', v1.text)
        self.assertEqual(0, v1.pos)
        self.assertEqual(2, v1.to_version)

        self.assertEqual('gg', v2.text)
        self.assertEqual(2, v2.pos)
        self.assertEqual(3, v2.to_version)

        self.assertEqual('pop', v3.text)
        self.assertEqual(7, v3.pos)
        self.assertEqual(4, v3.to_version)
 
    def test_insert_merge(self):
        h = TextHistory()
        h.insert('abcd qwe')
        h.insert('gg')
        h.insert('pop')
        
        actions = h.get_actions()
        self.assertEqual(1, len(actions))

        v1 = actions[0]
        self.assertEqual('abcd qweggpop', v1.text)
        self.assertEqual(0, v1.pos)
        self.assertEqual(3, v1.to_version)
    
    def test_insert_mix_merge(self):
        h = TextHistory()
        h.insert('abcd qwe')
        h.insert('gg', pos=2)
        
        actions = h.get_actions()
        self.assertEqual(1, len(actions))

        v1 = actions[0]
        self.assertEqual('abggcd qwe', v1.text)
        self.assertEqual(0, v1.pos)
        self.assertEqual(2, v1.to_version)
    
    def test_insert_example(self):
        h = TextHistory()
        h.insert('abc qwe')
        h.replace('A', pos=0)
        h.insert('xy', pos=2)
        h.insert('z', pos=4)

        actions = h.get_actions()
        self.assertEqual(3, len(actions))

        v3 = actions[2]
        self.assertEqual('xyz', v3.text)
        self.assertEqual(2, v3.pos)
        self.assertEqual(4, v3.to_version)
