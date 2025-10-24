import generator as G
c = G.Custom(class_name='test', args=[G.Arg('test','abc'), G.Arg('type','')])
gc = G.Generator(custom=c,prefix='pre_',name='gen1',pattern='abc')
G.save_policy('tmp/gen_policy.xml',[gc])
pol = G.load_policy('tmp/gen_policy.xml')
print(gc)
print(pol[0])