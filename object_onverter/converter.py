MAPPING_ROOT = '<root>'


class ObjectConverter:
    # 生成時にマッピング定義を受け取る
    def __init__(self, *, mapping):
        self.mapping = mapping

    # これを呼び出して変換する
    def convert(self, src):
        return self._convert_value(self.mapping[MAPPING_ROOT], MAPPING_ROOT, src)

    # dictからのオブジェクト生成
    def _convert_dict(self, func, key, value):
        # オブジェクトを生成する（別メソッドに分離）
        created, should_scan_values = self._create_object(func, key, value)
        if not should_scan_values:
            # dictの中身を個別にスキャンしない
            return created
        else:
            return self._scan_values(created, value)

    # dictの中身をひとつずつ変換
    def _scan_values(self, created, src):
        for key, value in src.items():
            if key in self.mapping:
                func = self.mapping[key]
                # マッピングされた関数を実行して結果をセットする
                self._set_value(created, key, self._convert_value(func, key, value))
            else:
                # マッピングに定義されていないものは、そのままセットする
                self._set_value(created, key, value)
        return created

    # リストの処理
    def _convert_sequence(self, func, key, sequence):
        current = []
        for value in sequence:
            current.append(self._convert_value(func, key, value))
        return current

    # マッピングされた値の処理
    def _convert_value(self, func, key, value):
        if isinstance(value, (list, tuple)):
            result = self._convert_sequence(func, key, value)
        elif isinstance(value, dict):
            result = self._convert_dict(func, key, value)
        elif isinstance(value, object) and hasattr(value, '__dict__'):
            # クラスのインスタンスは__dict__を取り出して扱う
            result = self._convert_dict(func, key, value.__dict__)
        else:
            result = value
        return result

    # 値設定用のメソッド（必要に応じてオーバーライドする） ※1
    def _set_value(self, obj, key, value):
        if isinstance(obj, dict):
            obj[key] = value
        else:
            setattr(obj, key, value)
    
    # オブジェクト生成時に使用するメソッド（必要に応じてオーバーライドする）※2
    def _create_object(self, func, key, value):
        # 値と一緒にFalseを返すとvalueの中身をスキャンしない
        return func(), True
    
    # dict変換用インスタンスを得るユーティリティメソッド
    @classmethod
    def dict_converter(cls, mapping):
        reverse_mapping = {}
        # 全てdictにマップするように作り直す こんなイメージ
        # before {MAPPING_ROOT : TestObject, 'nested' : NestedObject}
        # after  {MAPPING_ROOT : dict, 'nested' : dict}
        for key in mapping.keys():
            reverse_mapping[key] = dict
        # 6.dict変換用インスタンス
        return ObjectConverter(mapping=reverse_mapping)
