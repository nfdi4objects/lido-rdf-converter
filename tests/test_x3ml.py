import hashlib
from lxml import etree
import libs.x3ml as x3ml

LIDO_NS = x3ml.used_namespaces['lido']
XML_NS = x3ml.used_namespaces['xml']


def test_basic_utils():
    assert x3ml.not_none(1, "a", {}) is True
    assert x3ml.not_none(None, 1) is False
    assert x3ml.apply_valid_arg(lambda s: s.upper(), "abc") == "ABC"
    assert x3ml.apply_valid_arg(lambda s: s.upper(), None, "DEFAULT") == "DEFAULT"
    assert x3ml.str2bool("True") is True
    assert x3ml.str2bool("no") is False

def test_namespace_expand_compress():
    expanded = x3ml.expand_with_namespaces("lido:event")
    assert expanded == f"{{{LIDO_NS}}}event"
    compressed = x3ml.compress_with_namespaces(expanded)
    assert compressed == "lido:event"
    # unknown stays the same
    assert x3ml.expand_with_namespaces("unknown:tag") == "unknown:tag"
    assert x3ml.compress_with_namespaces("{urn:other}tag") == "{urn:other}tag"


def test_xpath_lido_and_transform_subs():
    xml = f'''
    <root xmlns:lido="{LIDO_NS}">
      <parent>
        <lido:child lido:attr="VAL"/>
      </parent>
    </root>'''
    root = etree.fromstring(xml.encode('utf-8'))
    parent = root.find('./parent')
    # xpath that selects child elements that have the lido:attr attribute
    subs = x3ml.xpath_lido(parent, './lido:child[@lido:attr]')
    assert len(subs) == 1
    # transform_subs should have populated the .text of the child from the attribute
    assert subs[0].text == "VAL"


def test_root_path_and_get_IDs():
    xml = f'''
    <root xmlns:lido="{LIDO_NS}">
      <lido:recordWrap>
         <lido:recordID>ID123</lido:recordID>
      </lido:recordWrap>
    </root>'''
    root = etree.fromstring(xml.encode('utf-8'))
    record_wrap = root.find(f'.//{{{LIDO_NS}}}recordWrap')
    record_id = record_wrap.find(f'./{{{LIDO_NS}}}recordID')
    # root_path_as_list should return a slash-separated path of local names
    assert x3ml.full_path(record_id) == "root/recordWrap/recordID"
    # get_IDs should discover the ID value from recordWrap
    ids = x3ml.get_IDs(record_wrap)
    assert ids == ["ID123"]


def test_Info_from_elem_and_lang_and_modes():
    # element with text and xml:lang
    elem = etree.Element(f'{{{LIDO_NS}}}title')
    elem.text = "  Hello  "
    elem.set(f'{{{XML_NS}}}lang', "en")
    info = x3ml.Info.from_elem(elem, 0)
    Mode = x3ml.IDMode
    assert info.text ==  "  Hello  "
    assert info.lang == "en"
    assert info.mode == Mode.NONE
    # element with subelements and no own text -> path mode
    parent = etree.Element(f'{{{LIDO_NS}}}parent')
    etree.SubElement(parent, f'{{{LIDO_NS}}}child')
    info2 = x3ml.Info.from_elem(parent, 1)
    assert info2.mode in (Mode.LIDO_ID,Mode.UUID)  # path expected unless mapped ID is found


def test_ExP_fromElements_and_subs_behavior():
    # create ExP for S and O and test subs against a LIDO fragment
    s_elem = etree.Element("s")
    s_elem.text = "lido:recordWrap"
    o_elem = etree.Element("o")
    o_elem.text = "lido:recordID"
    exp = x3ml.ExP.fromElements(s_elem, o_elem, "v", "g")
    assert exp.path == "lido:recordWrap"
    assert exp.entity == "lido:recordID"  # entity carries the text given

    # create a small LIDO document to use ExP.subs
    xml = f'''
    <root xmlns:lido="{LIDO_NS}">
      <lido:recordWrap>
         <lido:recordID>R1</lido:recordID>
      </lido:recordWrap>
      <lido:recordWrap>
         <lido:recordID>R2</lido:recordID>
      </lido:recordWrap>
    </root>'''
    root = etree.fromstring(xml.encode('utf-8'))
    # use an ExP that looks for recordWrap elements
    s = x3ml.ExP(path="lido:recordWrap", entity="http://example.org/type")
    subs = s.subs(root)
    assert len(subs) == 2
    # test that O.subs can find recordID children
    o = x3ml.ExP(path="lido:recordID", entity="http://example.org/object")
    infos = [x3ml.Info.from_elem(e, i) for i, e in enumerate(o.subs(root))]
    assert any(info.text == "R1" for info in infos)
    assert any(info.text == "R2" for info in infos)


def test_Condition_isValid_text_and_attr():
    # Prepare an element with a child text and an attribute
    xml = f'<e xmlns:lido="{LIDO_NS}" lido:flag="yes"><lido:name>keep</lido:name></e>'
    elem = etree.fromstring(xml.encode('utf-8'))
    cond = x3ml.Condition()
    cond.add('lido:name/text()', 'keep')
    assert cond.isValid(elem) is True
    cond2 = x3ml.Condition()
    # attribute check: access will be expanded as namespace attr name
    cond2.add('lido:flag', 'yes')
    assert cond2.isValid(elem) is True
    cond3 = x3ml.Condition()
    cond3.add('lido:flag', 'no')
    assert cond3.isValid(elem) is False


def test_mapping_and_po_evaluate_integration():
    # Build mapping programmatically: S points to recordWrap, O to recordID
    s = x3ml.ExP(path="lido:recordWrap", entity="http://type")
    o = x3ml.ExP(path="lido:recordID", entity="http://obj")
    pred = x3ml.ExP(path="lido:whatever", entity="http://pred")
    po = x3ml.PO(P=pred, O=o)
    mapping = x3ml.Mapping(S=s)
    mapping.addPO(po)

    # LIDO document with two recordWraps
    xml = f'''
    <root xmlns:lido="{LIDO_NS}">
      <lido:recordWrap><lido:recordID>ID-A</lido:recordID></lido:recordWrap>
      <lido:recordWrap><lido:recordID>ID-B</lido:recordID></lido:recordWrap>
    </root>'''
    root = etree.fromstring(xml.encode('utf-8'))

    results = mapping.evaluate(root)
    # mapping.evaluate returns a list of Mapping_Data objects (one per S.subs)
    assert isinstance(results, list)
    assert len(results) == 2
    texts = [md.text for md in [r.info for r in results] if isinstance(md, x3ml.Info)]
    # info objects are created from each S.subs element and should exist
    assert all(isinstance(r.info, x3ml.Info) for r in results)
    # Evaluate PO evaluation for first S.subs
    po_data_list = results[0].POs
    assert isinstance(po_data_list, list)
    assert all(isinstance(pd, x3ml.PO_Data) for pd in po_data_list)
    # check that O infos include the recordID text
    o_texts = [info.text for info in po_data_list[0].infos]
    assert "ID-A" in o_texts or "ID-B" in o_texts


def test_mappings_from_str_parsing_simple():
    xml = '''
    <root>
      <mapping>
        <domain>
          <source_node>lido:recordWrap</source_node>
          <target_node>
            <entity>
              <type>http://example.org/type</type>
            </entity>
          </target_node>
        </domain>
        <link>
          <path>
            <source_relation>
              <relation>lido:recordWrap</relation>
            </source_relation>
            <target_relation>
              <relationship>http://predicate</relationship>
            </target_relation>
          </path>
          <range>
            <source_node>lido:recordID</source_node>
            <target_node>
              <entity>
                <type>http://object</type>
              </entity>
            </target_node>
          </range>
        </link>
      </mapping>
    </root>
    '''
    mappings = x3ml.Mappings.from_str(xml)
    assert isinstance(mappings, x3ml.Mappings)
    assert len(mappings) == 1
    m = mappings[0]
    assert isinstance(m, x3ml.Mapping)
    assert m.S.path == "lido:recordWrap"
    assert len(m.POs) == 1
    assert m.POs[0].O.path == "lido:recordID"

def test_find_var_returns_variable_value():
    # build element with ./range/target_node/entity[@variable="v1"]
    link = etree.Element("link")
    range_el = etree.SubElement(link, "range")
    target_node = etree.SubElement(range_el, "target_node")
    entity = etree.SubElement(target_node, "entity")
    entity.set("variable", "v1")
    assert x3ml.find_var(link) == "v1"


def test_find_var_entity_without_attribute_returns_empty():
    link = etree.Element("link")
    range_el = etree.SubElement(link, "range")
    target_node = etree.SubElement(range_el, "target_node")
    etree.SubElement(target_node, "entity")  # no variable attribute
    assert x3ml.find_var(link) == ""


def test_find_var_no_entity_returns_empty():
    # link without the expected path should return the default empty string
    link = etree.Element("link")
    assert x3ml.find_var(link) == ""
