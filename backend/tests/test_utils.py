from app.utils import remove_overlaps_in_list_of_strings


def test_remove_overlaps_in_strings():
    # this might be hella confusing, but first ab abc are merged to abc on the right
    # then abc and abc are duplicates and merge to abc
    # finally ab and abc merge to abc. You just remove adjancent duplicates repeatedly

    # test multiple
    arr = ["ab", "abc", "ab", "abc"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == ["abc"]

    # test no match
    arr = ["abcde", "fghijkabcde"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr == arr2

    # test match in the middle of a word
    arr = ["abc def ghi", "ef ghi jklm nop"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == ["abc d", "ef ghi jklm nop"]

    # test almost match, but fail on last char
    arr = ["abc def ghij", "ef ghi jklm nop"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == arr

    # test multiple candidates, but pick the longest match
    arr = ["abc def abc def", "abc def ghi"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == ["abc def ", "abc def ghi"]

    # test almost match but fail on last char... again
    arr = ["abc def ghi", "gh"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == arr

    # test 1st sequence is longer than second with match
    arr = ["abc def ghi", "ghi"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == ["abc def ", "ghi"]

    # test second sequence is longer than first with a match
    arr = ["abc def", "abc def ghi"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == ["abc def ghi"]

    # test multipe cascading full matches
    arr = ["abc", "abc def", "abc def ghi", "ghi jkl mno"]
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == ["abc def ", "ghi jkl mno"]

    # test complete match reduces arr size
    arr = ["abc def ghi"] * 2
    arr2 = remove_overlaps_in_list_of_strings(arr)
    assert arr2 == arr[:1]
