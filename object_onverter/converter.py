
class ObjectConverter:
    # 生成時にマッピング定義を受け取る
    def __init__(self, *, mapping):
        self.mapping = mapping

    # 変換の呼出しメソッド
    def convert(self, src):
        # 最上位の要素はマッピング'<root>'と必ずマッチする前提
        return self._convert_value('<MAPPING_ROOT>', self.mapping['<MAPPING_ROOT>'], src)

    # 値に従って処理方法を決める
    def _convert_value(self, key, func, value):
        # リストの場合、要素全てをfuncで変換していく
        if isinstance(value, (list, tuple)):
            return self._convert_sequence(key, func, value)

        # dictの場合、そのままキーと値を取り出す
        if isinstance(value, dict):
            return self._convert_dict(key, func, value)

        # classの場合__dict__を取り出してdictとして扱う
        if isinstance(value, object) and hasattr(value, '__dict__'):
            return self._convert_dict(key, func, value.__dict__)

        # どれにも該当しないものはそのまま返す
        return value

    # dictの中身を変換していく
    def _convert_dict(self, key, func, src):
        # _call_functionで生成したオブジェクトに中身を詰める
        return self._assign_dict(self._call_function(key, func, src), key, src)

    # mappingで指定されたオブジェクトの生成
    def _call_function(self, key, func, src):
        return func()

    # dictの中身を取り出して当てはめて行く
    def _assign_dict(self, dest, key, src):

        for srcKey, value in src.items():

            # keyがマッピングに定義されている
            if srcKey in self.mapping:
                func = self.mapping[srcKey]
                # マッピングされた関数を実行して結果をセットする
                self._set_value(dest, srcKey, self._convert_value(srcKey, func, value))

            # keyがマッピング定義にない物は、そのままセットする
            else:
                # ここで渡されたvalueの中にマッピング定義された値があっても無視する
                self._set_value(dest, srcKey, value)

        # createdにsrcの中身が反映された状態
        return dest

    # リストの処理
    def _convert_sequence(self, key, func, sequence):
        current = []
        for value in sequence:
            current.append(self._convert_value(key, func, value))
        return current

    # dictとclass両方に対応する値setter
    def _set_value(self, dest, key, value):
        if isinstance(dest, dict):
            dest[key] = value
        else:
            setattr(dest, key, value)

    # dict変換用インスタンスを得るユーティリティメソッド
    # もしOrderedDictを使いたい場合はdict_objectに指定する
    #
    @classmethod
    def dict_converter(cls, mapping, *, dict_object=dict):
        reverse_mapping = {}

        # マッピング先を全てdictにしてしまう
        for key in mapping.keys():
            reverse_mapping[key] = dict_object

        # dictに変換するためのインスタンス
        return ObjectConverter(mapping=reverse_mapping)
