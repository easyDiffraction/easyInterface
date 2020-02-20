from easyInterface.Common.Utils.BaseClasses import Base, Data, Unit


def data_checker(data):
    assert isinstance(data, Data)
    keys = data.keys()
    assert len(keys) == 6
    expected_keys = ['value', 'unit', 'error', 'constraint', 'hide', 'refine']
    for this_key in expected_keys:
        assert this_key in keys
    assert isinstance(data['unit'], Unit)
    assert isinstance(data['hide'], bool)
    assert isinstance(data['refine'], bool)


def base_checker(base):
    assert isinstance(base, Base)
    keys = base.keys()
    assert len(keys) == 5
    expected_keys = ['header', 'tooltip', 'url', 'mapping', 'store']
    for this_key in expected_keys:
        assert this_key in keys
    assert isinstance(base['store'], Data)
    data_checker(base['store'])
    assert isinstance(base['header'], str)
    assert isinstance(base['tooltip'], str)
    assert isinstance(base['url'], str)


def test_DataClass():
    d = Data(1, 's')
    data_checker(d)
    assert str(d) == '1'
    assert d['value'] == 1
    assert str(d['unit']) == 's'

    d = Data(1, '')
    data_checker(d)
    assert str(d) == '1'
    assert d['value'] == 1
    assert str(d['unit']) == ''

    d = Data(None, '')
    data_checker(d)
    assert str(d) == 'None'
    assert d['value'] is None
    assert str(d['unit']) == ''


def test_DataClass_min():
    d = Data(1, 's')
    assert d.min == 0.8


def test_DataClass_max():
    d = Data(1, 's')
    assert d.max == 1.2


def test_BaseClass():
    b = Base(1, 's')
    base_checker(b)
    assert b['header'] == 'Undefined'
    assert b['tooltip'] == ''
    assert b['url'] == ''
    assert b['mapping'] is None


def test_Base_get_value():
    b = Base(1, 's')
    assert b.value == 1
    assert b['store']['value'] == 1


def test_Base_set_value():
    b = Base(1, 's')
    b.value = 2
    assert b.value == 2
    assert b['store']['value'] == 2


def test_Base_get_refine():
    b = Base(1, 's')
    assert b.refine is False
    assert b['store']['refine'] is False


def test_Base_set_refine():
    b = Base(1, 's')
    b.refine = True
    assert b.refine is True
    assert b['store']['refine'] is True


def test_Base_get():
    b = Base(1, 's')
    assert b.get('hide') is True


def test_Base_set():
    b = Base(1, 's')
    b.set('hide', False)
    assert b.get('hide') is False


def test_Base_unit_conversion_factor():
    b = Base(1, 's')
    fac = b.unitConversionFactor('h')
    assert fac == 1/3600


def test_Base_convert_units():
    b = Base(1, 's')
    b.convertUnits('h')
    base_checker(b)
    assert b.value == 1/3600
    assert str(b['store']['unit']) == 'h'


def test_Base_value_in_unit():
    b = Base(1, 's')
    val = b.valueInUnit('h')
    assert val == 1/3600
