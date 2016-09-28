import datetime
from context import *
from flcoll.models import *

class TestEvenement(TestCase):
    def test_create(self):
        e = Evenement(titre="Mon titre d'événement", date_debut=datetime.datetime(2017,6,6), uid_organisateur="test.user")


if __name__ == '__main__':
    unittest.main()
