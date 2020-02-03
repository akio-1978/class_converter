import unittest
import json
from object_onverter import ObjectConverter

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

        builder = ObjectConverter(mapping={'<MAPPING_ROOT>' : TestClass})
        result = builder.convert(dict_data)
        self.assertEqual(result.value1, 'string value 1')

        # 生成したクラスのメソッドを呼んでみる
        self.assertEqual(result.test_method(), 'TestObject.test_method')

    # ネストしたクラスを生成する
    def test_nested_object(self):
        # jsonのキーとクラスをマッピングするdict
        object_mapping = {
            '<MAPPING_ROOT>' : TestClass,
            'nested' : NestedTestClass
        }
        # 生成元のソース
        dict_data = {
            'value1' : 'string value 1',
            'nested' : {
                'value' : 'nested value 1'
            }
       }

        builder = ObjectConverter(mapping=object_mapping)
        result = builder.convert(dict_data)
        self.assertEqual(result.value1, 'string value 1')

        self.assertIsInstance(result.nested, NestedTestClass)
        self.assertEqual(result.nested.value, 'nested value 1')

    # マッピングを指定しない場合はただのdict
    def test_nested_dict(self):
        object_mapping = {
            '<MAPPING_ROOT>' : TestClass
        }

        # 生成元のソース
        dict_data = {
            'value1' : 'string value 1',
            'nested' : {
                'value' : 'nested value 1'
            }
        }

        builder = ObjectConverter(mapping = object_mapping)
        result = builder.convert(dict_data)
        self.assertEqual(result.value1, 'string value 1')
        self.assertIsInstance(result.nested, dict)
        self.assertEqual(result.nested['value'], 'nested value 1')

    # リストの処理
    def test_sequence(self):
        mapping = {
            '<MAPPING_ROOT>' : TestClass,
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

        builder = ObjectConverter(mapping=mapping)
        result = builder.convert(source_dict)
        self.assertEqual(result.value1, 'string value 1')
        self.assertEqual(len(result.nestedObjects), 3)

        for i in range(3):
            self.assertIsInstance(result.nestedObjects[i], NestedTestClass)
            self.assertEqual(result.nestedObjects[i].value, str(i))

    # ルート要素自体がリストの場合
    def test_root_sequence(self):
        object_mapping = {
            '<MAPPING_ROOT>' : TestClass,
        }

        source_list = [
            {'value' : '0'},
            {'value' : '1'},
            {'value' : '2'},
        ]

        builder = ObjectConverter(mapping=object_mapping)
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
            '<MAPPING_ROOT>' : TestClass,
            'nested' : NestedTestClass
        }
        # 生成元のソース - 比較の都合のため一行で
        string_data = '{"value1": "string value 1", "nested": {"value": "nested value 1"}}'
        dict_data = json.loads(string_data)

        builder = ObjectConverter(mapping=object_mapping)
        result = builder.convert(dict_data)
        dump_string = json.dumps(result, default=default_method)
        self.assertEqual(dump_string, string_data)

        # 再変換しても結果が同じこと
        result = builder.convert(json.loads(dump_string))
        self.assertEqual(result.value1, 'string value 1')
        self.assertIsInstance(result.nested, NestedTestClass)
        self.assertEqual(result.nested.value, 'nested value 1')

if __name__ == '__main__':
    unittest.main()
