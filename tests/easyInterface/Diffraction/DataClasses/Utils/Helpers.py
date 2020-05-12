from easyInterface.Diffraction.DataClasses.Utils.BaseClasses import Base, PathDict


def PathDictDerived(input_constructor, expected:list, expected_type: list, *args):

    constructed = input_constructor(*args)
    assert isinstance(constructed, PathDict)
    keys = constructed.keys()
    print(list(keys))
    print(expected)
    assert len(keys) == len(expected)


    for idx, key in enumerate(expected):
        assert key in keys
        typecheck = isinstance(constructed[key], expected_type[idx])
        if not typecheck:
            print('{} - {}'.format(constructed[key], expected_type[idx]))
        assert typecheck

        if isinstance(constructed[key], Base):
            assert 'header' in constructed[key].keys()
            assert constructed[key]['header'] is not None
            assert 'tooltip' in constructed[key].keys()
            assert constructed[key]['tooltip'] is not None
            assert 'url' in constructed[key].keys()
            assert constructed[key]['url'] is not None