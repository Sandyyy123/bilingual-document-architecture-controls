import json
from controls import Evidence, assess, traceability
r=Evidence('SYNTHETIC-AR-01','v1','ar','هذه وثيقة تجريبية للمراجعة البشرية.','demo',1)
print(json.dumps({'evidence_gate':assess(r,tenant='demo',quote='وثيقة تجريبية',version='v1',confidence=.97),
 'traceability':traceability([{'id':'R-001','status':'confirmed'}],{'R-001':{'component':'evidence-store','acceptance_test':'citation hash/version/page test','owner':'platform'}})},ensure_ascii=False,indent=2))
