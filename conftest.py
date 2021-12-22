from refguide_checker import Checker
import _pytest.doctest
import doctest
import pytest


# @pytest.fixture(autouse=True)
# def refguide_checker(monkeypatch):
#
#     def custom_checker() -> "doctest.OutputChecker":
#         # return Checker(atol=0.000000001)
#         return Checker(atol=0.001)
#
#     monkeypatch.setattr(_pytest.doctest, "_get_checker", custom_checker)


def pytest_configure(config):

    def custom_checker() -> "doctest.OutputChecker":

        # return Checker(atol=0.00000001)
        return Checker(atol=0.000001)

    _pytest.doctest._get_checker = custom_checker
