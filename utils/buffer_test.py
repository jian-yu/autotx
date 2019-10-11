import unittest
from autotx.utils.buffer import Buffer


class TestBuffer(unittest.TestCase):
    def test_create(self):
        size = 10
        buffer = Buffer(size)
        self.assertEqual(size, buffer.Cap())

    def test_bufPut(self):
        size = 10
        buffer = Buffer(size)
        data = []
        # 情况一：新缓存
        for i in range(0, size):
            data.append(i)
        count = 0
        for item in data:
            ok, err = buffer.Put(item)
            self.assertIsNone(err)
            self.assertTrue(ok)
            count += 1
            self.assertEqual(buffer.Len(), count)
        # 情况二：缓存已满
        ok, err = buffer.Put(data)
        self.assertIsNone(err)
        self.assertFalse(ok)
        buffer.Close()
        # 情况三：缓存已关闭
        ok, err = buffer.Put(data)
        self.assertIsNotNone(err)

    def test_bufGet(self):
        size = 10
        # 情况一：新缓存
        buffer = Buffer(size)
        for i in range(0, size):
            buffer.Put(i)
        count = size
        while count >= 1:
            data, err = buffer.Get()
            self.assertEqual(data, size - count)
            self.assertIsNone(err)
            count -= 1
        # 情况二：缓存已空
        data, err = buffer.Get()
        self.assertIsNone(data)
        self.assertIsNone(err)
        buffer.Close()
        # 情况三：缓存已关闭
        data, err = buffer.Get()
        self.assertIsNone(data)
        self.assertIsNotNone(err)

    def test_bufPutAndGet(self):
        size = 10
        buffer = Buffer(size)
        data = []
        # 情况一：新缓存
        for i in range(0, size):
            data.append(i)
        count = 0
        # 情况二：把输入放入缓存
        for item in data:
            ok, err = buffer.Put(item)
            self.assertIsNone(err)
            self.assertTrue(ok)
            count += 1
            self.assertEqual(buffer.Len(), count)
        # 情况三：取出缓存数据
        while count >= 4:
            val, err = buffer.Get()
            self.assertEqual(val, data[size - count])
            self.assertIsNone(err)
            count -= 1
        # 情况四：缓存已关闭
        buffer.Close()
        ok, err = buffer.Put(data)
        self.assertIsNotNone(err)
        data, err = buffer.Get()
        self.assertIsNone(data)
        self.assertIsNotNone(err)


if __name__ == '__main__':
    unittest.main()
