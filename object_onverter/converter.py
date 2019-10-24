MAPPING_ROOT = '<root>'


class ObjectConverter:
    # 生成時にマッピング定義を受け取る
    def __init__(self, *, mapping):
        self.mapping = mapping

    # これを呼び出して変換する
    def convert(self, src):
        return self._convert_value(self.mapping[MAPPING_ROOT], MAPPING_ROOT, src)

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
            result = self._scan_values(func(), value)
        elif isinstance(value, object) and hasattr(value, '__dict__'):
            # クラスのインスタンスは__dict__を取り出して扱う
            result = self._scan_values(func(), value.__dict__)
        else:
            result = value
        return result

    # 値設定用のメソッド dictはkeyに、classはattributeに
    def _set_value(self, obj, key, value):
        if isinstance(obj, dict):
            obj[key] = value
        else:
            setattr(obj, key, value)
