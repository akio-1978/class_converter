import unittest
import json
from classconverter import ClassConverter, MAPPING_ROOT

# テスト用クラスその1
class TestClass():
    def test_method(self):
        return 'TestObject.test_method'

# テスト用クラスその2
class NestedTestClass:
    def test_method(self):
        return 'NestedObject.test_method'


class ClassConverterTest(unittest.TestCase):

    # ルートになるクラスのプロパティを設定するだけ
    def test_object_convert(self):
        dict_data = {
            'value1' : 'string value 1'
        }

        builder = ClassConverter(mapping={MAPPING_ROOT : TestClass})
        result = builder.convert(dict_data)
        self.assertEqual(result.value1, 'string value 1')

        # 生成したクラスのメソッドを呼んでみる
        self.assertEqual(result.test_method(), 'TestObject.test_method')

    # ネストしたクラスを生成する
    def test_nested_object(self):
        # jsonのキーとクラスをマッピングするdict
        object_mapping = {
            MAPPING_ROOT : TestClass,
            'nested' : NestedTestClass
        }
        # 生成元のソース
        dict_data = {
            'value1' : 'string value 1',
            'nested' : {
                'value' : 'nested value 1'
            }
       }

        builder = ClassConverter(mapping=object_mapping)
        result = builder.convert(dict_data)
        self.assertEqual(result.value1, 'string value 1')

        self.assertIsInstance(result.nested, NestedTestClass)
        self.assertEqual(result.nested.value, 'nested value 1')

    # マッピングを指定しない場合はただのdict
    def test_nested_dict(self):
        object_mapping = {
            MAPPING_ROOT : TestClass
        }

        # 生成元のソース
        dict_data = {
            'value1' : 'string value 1',
            'nested' : {
                'value' : 'nested value 1'
            }
        }

        builder = ClassConverter(mapping = object_mapping)
        result = builder.convert(dict_data)
        self.assertEqual(result.value1, 'string value 1')
        self.assertIsInstance(result.nested, dict)
        self.assertEqual(result.nested['value'], 'nested value 1')

    # リストの処理
    def test_sequence(self):
        mapping = {
            MAPPING_ROOT : TestClass,
            'nestedObjects' : NestedTestClass,
        }
        source_dict = {
            "value1" : "string value 1",
            "nestedObjects" : [
                {'value' : '0'},
                {'value' : '1'},
                {'value' : '2'},
            ]
        }

        builder = ClassConverter(mapping=mapping)
        result = builder.convert(source_dict)
        self.assertEqual(result.value1, 'string value 1')
        self.assertEqual(len(result.nestedObjects), 3)

        for i in range(3):
            self.assertIsInstance(result.nestedObjects[i], NestedTestClass)
            self.assertEqual(result.nestedObjects[i].value, str(i))

    # ルート要素自体がリストの場合
    def test_root_sequence(self):
        object_mapping = {
            MAPPING_ROOT : TestClass,
        }

        source_list = [
            {'value' : '0'},
            {'value' : '1'},
            {'value' : '2'},
        ]

        builder = ClassConverter(mapping=object_mapping)
        result = builder.convert(source_list)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

        for i in range(3):
            self.assertIsInstance(result[i], TestClass)
            self.assertEqual(result[i].value, str(i))

    # json -> class -> json
    def test_json_to_class_to_json(self):
        # クラスからjsonの相互変換に使う関数
        def default_method(item):
            if isinstance(item, object) and hasattr(item, '__dict__'):
                return item.__dict__
            else:
                raise TypeError

        # jsonのキーとクラスをマッピングするdict
        object_mapping = {
            MAPPING_ROOT : TestClass,
            'nested' : NestedTestClass
        }
        # 生成元のソース - 比較の都合のため一行で
        string_data = '{"value1": "string value 1", "nested": {"value": "nested value 1"}}'
        dict_data = json.loads(string_data)

        builder = ClassConverter(mapping=object_mapping)
        result = builder.convert(dict_data)
        dump_string = json.dumps(result, default=default_method)
        self.assertEqual(dump_string, string_data)

        # 再変換しても結果が同じこと
        result = builder.convert(json.loads(dump_string))
        self.assertEqual(result.value1, 'string value 1')
        self.assertIsInstance(result.nested, NestedTestClass)
        self.assertEqual(result.nested.value, 'nested value 1')

    # 変換したクラスをdictに戻す
    def test_class_to_dict(self):
        # キーとクラスをマッピングするdict
        object_mapping = {
            MAPPING_ROOT : TestClass,
            'nested' : NestedTestClass
        }
        # 変換元
        dict_data = {
            'value1' : 'string value 1',
            'nested' : {
                'value' : 'nested value 1'
            }
        }

        builder = ClassConverter(mapping=object_mapping)
        result = builder.convert(dict_data)
        # インスタンスの中身を変更
        result.nested.value = 'changed.'
        # ネストを深くしてみる
        nest = NestedTestClass()
        nest.added_value = 'added.'
        result.nested.nested = nest

        # 逆変換用インスタンスの作成
        reverse_builder = ClassConverter.dict_converter(object_mapping)
        result_dict = reverse_builder.convert(result)

        self.assertEqual(result_dict['value1'], 'string value 1')
        self.assertIsInstance(result_dict['nested'], dict)
        self.assertEqual(result_dict['nested']['value'], 'changed.')
        self.assertIsInstance(result_dict['nested']['nested'], dict)
        self.assertEqual(result_dict['nested']['nested']['added_value'], 'added.')

    # クラスのタプルをdictに戻す
    # 対象が広がった感があるので、リスト以外にタプルも扱うようにした
    def test_tuple_to_dict(self):
        # クラスのタプルを作る（汚いコードだけど）
        obj0 = TestClass()
        obj0.value = '0'
        obj1 = TestClass()
        obj1.value = '1'
        obj2 = TestClass()
        obj2.value = '2'
        source_tuple = (obj0, obj1, obj2)

        # 本来のマッピング
        object_mapping = {
            MAPPING_ROOT : TestClass,
        }

        # 逆変換用インスタンスの作成
        builder = ClassConverter.dict_converter(object_mapping)
        result = builder.convert(source_tuple)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

        for i in range(3):
            self.assertIsInstance(result[i], dict)
            self.assertEqual(result[i]['value'], str(i))

    # 値「value」を数値に変換する
    def test_value_type_convert(self):
        mapping = {
            MAPPING_ROOT : TestClass,
        }
        source_dict = {
            'value' : '1024',
            'string_value' : '2048'
        }

        # _set_valueをオーバーライドする
        class TypeConverter(ClassConverter):
            def _set_value(self, obj, key, value):
                setattr(obj, key, int(value) if key == 'value' else value)

        builder = TypeConverter(mapping=mapping)
        result = builder.convert(source_dict)
        self.assertEqual(result.value, 1024)
        self.assertEqual(result.string_value, '2048')

    # 構造を追加する - DynamoDBっぽく変更
    def test_structure_extract(self):
        mapping = {
            MAPPING_ROOT : dict,
        }

        source_object = TestClass()
        source_object.number_value = 128
        source_object.string_value = 256

        # _set_valueをオーバーライドする
        class StructureExtractor(ClassConverter):
            def _set_value(self, obj, key, value):
                if key == 'number_value':
                    obj[key] = {'N' : value}
                elif key == 'string_value':
                    obj[key] = {'S' : str(value)}

        builder = StructureExtractor(mapping=mapping)
        result = builder.convert(source_object)
        self.assertEqual(result['number_value']['N'], 128)
        self.assertEqual(result['string_value']['S'], '256')

    # 構造を畳み込む - DynamoDBっぽい形から変換
    def test_structure_folding(self):
        mapping = {
            MAPPING_ROOT : dict,
            'number_value' : None,
            'string_value' : None
        }

        source_dict = {
            'number_value' : {'N' : '1024'},
            'string_value' : {'S' : '2048'}
        }

        # _create_objectをオーバーライドする
        class StructureFolder(ClassConverter):
            def _create_object(self, func, key, value):
                if key == 'number_value':
                    return int(value['N']), False
                elif key == 'string_value':
                    return str(value['S']), False
                else:
                    return super()._create_object(func, key, value)

        builder = StructureFolder(mapping=mapping)
        result = builder.convert(source_dict)
        self.assertEqual(result['number_value'], 1024)
        self.assertEqual(result['string_value'], '2048')


if __name__ == '__main__':
    unittest.main()
