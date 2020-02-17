import unittest
import manufacturers

class TestManufactorers(unittest.TestCase):

    def testHocManufactorer(self):
        m = manufacturers.HocManufactorer()
        self.assertEqual(m.reload_speed, 1)
        self.assertEqual(m.damage, 3.5)
        self.assertEqual(m.fire_rate, 10)
        self.assertEqual(m.accuracy, 72)
        self.assertEqual(m.magazine_size, 150)
        self.assertEqual(m.weight, 10)

    def testVockarManufactorer(self):
        m = manufacturers.VockarManufactorer()
        self.assertEqual(m.reload_speed, 3)
        self.assertEqual(m.damage, 7.5)
        self.assertEqual(m.fire_rate, 2.5)
        self.assertEqual(m.accuracy, 100)
        self.assertEqual(m.magazine_size, 50)
        self.assertEqual(m.weight, 6)

    def testMajinaManufactorer(self):
        m = manufacturers.MajinaManufactorer()
        self.assertEqual(m.reload_speed, 0.6)
        self.assertEqual(m.damage, 3)
        self.assertEqual(m.fire_rate, 5)
        self.assertEqual(m.accuracy, 60)
        self.assertEqual(m.magazine_size, 30)
        self.assertEqual(m.weight, 1)

    def testBrightManufactorer(self):
        m = manufacturers.BrightManufactorer()
        self.assertEqual(m.reload_speed, 2)
        self.assertEqual(m.damage, 10)
        self.assertEqual(m.fire_rate, 5)
        self.assertEqual(m.accuracy, 18)
        self.assertEqual(m.magazine_size, 25)
        self.assertEqual(m.weight, 30)

    def testJenkinsManufactorer(self):
        m = manufacturers.JenkinsManufactorer()
        self.assertEqual(m.reload_speed, 2)
        self.assertEqual(m.damage, 5)
        self.assertEqual(m.fire_rate, 5)
        self.assertEqual(m.accuracy, 60)
        self.assertEqual(m.magazine_size, 50)
        self.assertEqual(m.weight, 10)

    def testSternwelManufactorer(self):
        m = manufacturers.SternwelManufactorer()
        self.assertEqual(m.reload_speed, 2)
        self.assertEqual(m.damage, 3.5)
        self.assertEqual(m.fire_rate, 5)
        self.assertEqual(m.accuracy, 48)
        self.assertEqual(m.magazine_size, 100)
        self.assertEqual(m.weight, 8)
        self.assertTrue(m.element in ("fire","water","earth","air","EXPLOSION"))

if __name__ == "__main__":
    unittest.main()
