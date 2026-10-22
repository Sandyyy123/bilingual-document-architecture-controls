import pytest
from controls import Evidence,assess,traceability,normalize

def run(**kw):
 r=kw.pop('record',Evidence('S1','v2','en','A synthetic source statement.','tenant-a',2))
 args=dict(tenant='tenant-a',quote='source statement',version='v2',confidence=.95)
 args.update(kw);return assess(r,**args)

def test_citation_is_exact_version_page_hash():
 out=run();assert out['status']=='eligible_for_human_approval'
 assert out['citation']['version']=='v2' and out['citation']['page']==2 and len(out['citation']['sha256'])==64
@pytest.mark.parametrize('kwargs,reason',[
 ({'tenant':'other'},'tenant_boundary'),({'version':'v1'},'stale_version'),
 ({'quote':'invented assertion'},'unsupported_quote'),({'quote':''},'unsupported_quote'),
 ({'confidence':.2},'low_confidence')])
def test_fail_closed(kwargs,reason): assert reason in run(**kwargs)['reasons']
def test_arabic_requires_named_review_state():
 r=Evidence('A','v1','ar','وثيقة تجريبية','tenant-a',1)
 assert 'arabic_review_required' in run(record=r,quote='وثيقة',version='v1')['reasons']
 assert run(record=r,quote='وثيقة',version='v1',arabic_reviewed=True)['status']=='eligible_for_human_approval'
def test_arabic_not_transliterated():assert normalize('  وثيقة  تجريبية ')=='وثيقة تجريبية'
def test_invalid_confidence():
 with pytest.raises(ValueError):run(confidence=1.2)
def test_trace_gaps_and_unknown():
 out=traceability([{'id':'R1','status':'assumption'}],{'R2':{}})
 assert out['gaps'][0]['id']=='R1' and out['unknown_assignments']==['R2']
def test_trace_complete():
 assert traceability([{'id':'R1','status':'confirmed'}],{'R1':{'component':'A','owner':'B','acceptance_test':'C'}})['status']=='mapped'
def test_duplicate_ids():
 with pytest.raises(ValueError):traceability([{'id':'R','status':'confirmed'}]*2,{})
