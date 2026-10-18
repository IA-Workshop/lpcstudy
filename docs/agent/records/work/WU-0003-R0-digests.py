import json, sys
g=json.load(open(sys.argv[1])); c=json.load(open(sys.argv[2]))
def flat(x,p=''):
    if isinstance(x,dict):
        for k,v in x.items(): yield from flat(v,p+'/'+str(k))
    elif isinstance(x,list) and x and all(isinstance(e,(int,float)) for e in x):
        for i,e in enumerate(x): yield p+f'[{i}]',e
    else: yield p,x
for sysn in ['lorenz63','rossler','chua']:
    print('==',sysn)
    G=dict(flat(g['systems'][sysn]['context'])); C=dict(flat(c['systems'][sysn]['context']))
    for k in G:
        a,b=G[k],C.get(k,'<absent>')
        eq = (a==b)
        extra=''
        if not eq and isinstance(a,float) and isinstance(b,float): extra=f'  rel={abs(a-b)/abs(a):.3g}'
        print(f"  context{k}: {'equal' if eq else 'DIFFER'}{extra}" + ('' if eq or 'digest' in k else f'  gpu={a} cpu={b}'))
    vg=g['systems'][sysn]['validation']; vc=c['systems'][sysn]['validation']
    for k in ['delay_jacobian_rel_err','gain_rel_err','crlb_ratio_median','crlb_ratio_min','crlb_ratio_max']:
        print(f'  V {k}: gpu={vg[k]!r} cpu={vc[k]!r} |d|={abs(vg[k]-vc[k]):.3g} rel={abs(vg[k]-vc[k])/abs(vg[k]):.3g}')
    for k in vg['estimators']:
        print('  validation estimator', k, 'weights_digest equal' if vg['estimators'][k].get('weights_digest')==vc['estimators'][k].get('weights_digest') else 'weights_digest DIFFER')
    ag=g['systems'][sysn]['fitted'].get('allocator_digest'); ac=c['systems'][sysn]['fitted'].get('allocator_digest')
    print('  fitted/allocator_digest', 'equal' if ag==ac else 'DIFFER')
for k in g['estimators']:
    print('estimator',k,'weights_digest','equal' if g['estimators'][k]['weights_digest']==c['estimators'][k]['weights_digest'] else 'DIFFER')
