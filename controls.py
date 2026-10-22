"""Deterministic architecture-control demonstration; no LLM or legal judgments."""
from dataclasses import dataclass
from hashlib import sha256
import unicodedata

@dataclass(frozen=True)
class Evidence:
    source_id: str
    version: str
    language: str
    text: str
    tenant: str
    page: int

    @property
    def digest(self):
        return sha256(self.text.encode('utf-8')).hexdigest()

def normalize(text):
    """NFC preserves Arabic letters; whitespace cleanup does not translate text."""
    return ' '.join(unicodedata.normalize('NFC', text).split())

def assess(record, *, tenant, quote, version, confidence, arabic_reviewed=False):
    """Default-deny mismatched sources; require explicit Arabic human review."""
    reasons=[]
    if record.tenant != tenant: reasons.append('tenant_boundary')
    if record.version != version: reasons.append('stale_version')
    if not quote.strip() or normalize(quote) not in normalize(record.text): reasons.append('unsupported_quote')
    if not 0 <= confidence <= 1: raise ValueError('confidence must be within [0,1]')
    if confidence < .9: reasons.append('low_confidence')
    if record.language not in ('ar','en'): reasons.append('unsupported_language')
    if record.language == 'ar' and not arabic_reviewed: reasons.append('arabic_review_required')
    if record.page < 1 or not record.source_id or not record.version: reasons.append('incomplete_provenance')
    return {'status':'human_review' if reasons else 'eligible_for_human_approval',
            'reasons':reasons,'citation':{'source':record.source_id,'version':record.version,
            'page':record.page,'sha256':record.digest},'text':normalize(quote)}

def traceability(requirements, assignments):
    """Report orphan and unsupported IDs, rather than hiding incomplete scope."""
    ids=[r['id'] for r in requirements]
    if len(ids)!=len(set(ids)): raise ValueError('duplicate requirement ids')
    accepted={'confirmed','assumption','recommendation'}
    if any(r.get('status') not in accepted for r in requirements): raise ValueError('unclassified requirement')
    gaps=[]
    for r in requirements:
        a=assignments.get(r['id'],{})
        missing=[k for k in ('component','acceptance_test','owner') if not a.get(k)]
        if missing:gaps.append({'id':r['id'],'missing':missing})
    return {'gaps':gaps,'unknown_assignments':sorted(set(assignments)-set(ids)),
            'status':'review_required' if gaps or set(assignments)-set(ids) else 'mapped'}
