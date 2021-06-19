

import pytest

import pyrepsys.helpers


def test_find_nearest_step():
    int_list = [1, 2, 3, 4, 5, 6, 7]
    check_for = 2.6
    expected_nearest = 3

    nearest = pyrepsys.helpers.find_nearest_step(check_for, int_list)
    assert expected_nearest == nearest

    check_for = 4.5
    expected_nearest = 5
    nearest = pyrepsys.helpers.find_nearest_step(check_for, int_list)
    assert expected_nearest == nearest

    check_for = 7
    expected_nearest = 7
    nearest = pyrepsys.helpers.find_nearest_step(check_for, int_list)
    assert expected_nearest == nearest

    # larger than largest step
    check_for = 8
    with pytest.raises(ValueError):
        nearest = pyrepsys.helpers.find_nearest_step(check_for, int_list)
    
    float_list = [0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1]
    check_for = 0.6
    expected_nearest = 0.6
    nearest = pyrepsys.helpers.find_nearest_step(check_for, float_list)
    assert expected_nearest == nearest

    check_for = 1.621
    expected_nearest = 1.5
    nearest = pyrepsys.helpers.find_nearest_step(check_for, float_list)
    assert expected_nearest == nearest

    check_for = 1.65
    expected_nearest = 1.8
    nearest = pyrepsys.helpers.find_nearest_step(check_for, float_list)
    assert expected_nearest == nearest

    check_for = 0.2
    with pytest.raises(ValueError):
        nearest = pyrepsys.helpers.find_nearest_step(check_for, float_list)

def test_convert_resolution():
    pyrepsys.helpers.measured_claim_steps = [1, 1.5, 2, 2.5, 3]
    pyrepsys.helpers.review_steps = [1, 2, 3]

    def check(input, expect):
        converted = pyrepsys.helpers.convert_resolution(
            input,
            target_domain
        )
        assert expect == converted

    target_domain = pyrepsys.helpers.ResolutionDomain.REVIEW
    check(input=2.51, expect=3)
    check(input=2.5, expect=3)
    check(input=1, expect=1)
    with pytest.raises(ValueError):
        check(input=0, expect=None)
    with pytest.raises(ValueError):
        check(input=0.99, expect=None)

    target_domain = pyrepsys.helpers.ResolutionDomain.MEASURED_CLAIM
    check(input=1, expect=1)
    check(input=1.25, expect=1.5)
    check(input=1.7499, expect=1.5)
    check(input=1.75, expect=2)
    check(input=1.7501, expect=2)
    check(input=1.76, expect=2)
    check(input=1, expect=1)
    with pytest.raises(ValueError):
        check(input=3.1, expect=None)

    # binary:
    pyrepsys.helpers.measured_claim_steps = [0, 0.25, 0.5, 0.75, 1]
    pyrepsys.helpers.review_steps = [0, 1]

    target_domain = pyrepsys.helpers.ResolutionDomain.MEASURED_CLAIM
    check(input=0, expect=0)
    check(input=0.5236, expect=0.5)

    target_domain = pyrepsys.helpers.ResolutionDomain.REVIEW
    check(input=0.5236, expect=1)
    check(input=0.4999, expect=0)
    check(input=0.5, expect=1)
    check(input=0.5, expect=1)