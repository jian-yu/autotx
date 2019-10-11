from hsnhub_tx.utils.pool import Pool
import unittest


class TestPool(unittest.TestCase):
    def test_create(self):
        bufCap = 10
        maxBufNumber = 10
        pool = Pool(bufCap, maxBufNumber)
        self.assertEqual(bufCap, pool.BufCap())
        self.assertEqual(maxBufNumber, pool.MaxBufNumber())
        self.assertEqual(1, pool.BufNumber())

    def test_poolPut(self):
        bufCap = 10
        maxBufNumber = 20
        pool = Pool(bufCap, maxBufNumber)
        dataLen = bufCap * maxBufNumber
        data = []
        for i in range(0, dataLen):
            data.append(i)
        count = 0
        for item in data:
            err = pool.Put(item)
            self.assertIsNone(err)
            count += 1
            self.assertEqual(pool.Total(), count)
            targetBufNumber = int(count / bufCap)
            if count % bufCap != 0:
                targetBufNumber += 1
            self.assertEqual(targetBufNumber, pool.BufNumber())
        pool.Close()
        err = pool.Put(item)
        self.assertIsNotNone(err)

    def test_poolGet(self):
        bufCap = 10
        maxBufNumber = 20
        pool = Pool(bufCap, maxBufNumber)
        dataLen = bufCap * maxBufNumber
        count = dataLen
        targetBufNumber = maxBufNumber
        data = []
        for i in range(0, dataLen):
            data.append(i)
        for item in data:
            pool.Put(item)
        for value in data:
            val, err = pool.Get()
            self.assertIsNone(err)
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, dataLen)
            count -= 1
            self.assertEqual(count, pool.Total())
            self.assertEqual(targetBufNumber, pool.BufNumber())
        pool.Put(dataLen)
        pool.Close()
        _, err = pool.Get()
        self.assertIsNotNone(err)


if __name__ == '__main__':
    unittest.main()
