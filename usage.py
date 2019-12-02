from object_onverter import ObjectConverter

# こういうクラスを
class ParentClass:
    def parentValue(self):
        return self.value
class ChildClass:
    def childValue(self):
        return self.child_value

# こんなdictから作りたい
src_dict = {
    'value' : 'parent value',
    'child' : {
        'child_value' : 'child value'
    },
}

# dict -> classのマッピングを定義して
mapping = {
    '<root_mapping>' : ParentClass,
    'child' : ChildClass
}

# 変換します
converter = ObjectConverter(mapping=mapping)
parent = converter.convert(src_dict)

print(parent.parentValue())         # parent value
print(parent.child.childValue())    # child value
