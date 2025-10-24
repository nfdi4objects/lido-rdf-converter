import generator as G
c = G.Custom(class_name='test', args=[G.Arg('test','abc'), G.Arg('type','')])
gc = G.Generator(custom=c,prefix='pre_',name='gen1',pattern='abc')
gc.save_to_file('tmp/gen.xml')
gc2 = G.Generator.load_from_file('tmp/gen.xml')
print(gc)
print(gc2)