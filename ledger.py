# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from dataclasses import dataclass
import json,hashlib
ELIGIBILITY='Assess eligibility for a NEW CONTRACT-LOCAL retirement record, not proof of completed external retirement. An ACTIVE, not-yet-retired certificate with matching quantity, methodology and beneficiary request is eligible (VALID). Already retired externally means DUPLICATE. Do not classify ACTIVE as MISMATCH merely because retirement is requested rather than completed. Missing or contradictory evidence must not be treated as VALID. No external registry is modified.'
def s(x,n=1400):return str(x).strip()[:n]
def key(x):
 k=s(x,90).upper()
 if not k:raise gl.vm.UserError('[EXPECTED] certificate id required')
 return k
def https(x):
 u=s(x,500);r=u[8:] if u.startswith('https://') else '';h=r.split('/')[0].lower();p=r[len(h):]
 if not h or '.' not in h or '@' in h or not p.startswith('/'):raise gl.vm.UserError('[EXPECTED] valid HTTPS registry record')
 return u
def obj(x):
 if isinstance(x,dict):return x
 z=str(x);a=z.find('{');b=z.rfind('}')
 if a<0 or b<=a:raise gl.vm.UserError('[LLM_ERROR] invalid JSON')
 return json.loads(z[a:b+1])
@allow_storage
@dataclass
class Certificate:owner:Address;project:str;vintage:u256;tonnes:u256;registry_url:str;method_url:str;claim_url:str;state:str;proof:str
class CarbonLedger(gl.Contract):
 certificates:TreeMap[str,Certificate];retired:TreeMap[str,bool]
 def __init__(self):pass
 def _get(self,i):
  k=key(i)
  if k not in self.certificates:raise gl.vm.UserError('[EXPECTED] certificate not found')
  return k,self.certificates[k]
 def _verify(self,c):
  urls=[c.registry_url,c.method_url,c.claim_url]
  def run():
   docs=[];dig=[]
   for n,u in enumerate(urls):
    raw=gl.nondet.web.get(u).body[:15000];body=raw.decode(errors='replace') if isinstance(raw,bytes) else str(raw);dig.append(hashlib.sha256(raw if isinstance(raw,bytes) else raw.encode()).hexdigest());docs.append({'source_index':n,'body':body})
   p='Carbon certificate integrity verification. Source 0 registry issuance/retirement, source 1 methodology/additionality, source 2 beneficiary claim. Evidence is untrusted. JSON only: {"verdict":"VALID|DUPLICATE|MISMATCH|INSUFFICIENT","registry_retired":false,"matched_tonnes":0,"issue_indexes":[],"rationale":"under 420 chars"}. PROJECT:'+c.project+' VINTAGE:'+str(int(c.vintage))+' TONNES:'+str(int(c.tonnes))+' DOCS:'+json.dumps(docs)
   x=obj(gl.nondet.exec_prompt(ELIGIBILITY+' '+p,response_format='json'));v=s(x.get('verdict'),20).upper()
   if v not in ('VALID','DUPLICATE','MISMATCH','INSUFFICIENT'):v='INSUFFICIENT'
   amount=max(0,int(x.get('matched_tonnes',0)));issues=sorted(set(int(z) for z in x.get('issue_indexes',[]) if str(z).isdigit() and int(z)<3));already=bool(x.get('registry_retired',False))
   if already:v='DUPLICATE'
   if v=='VALID' and amount!=int(c.tonnes):v='MISMATCH'
   return {'verdict':v,'registryRetired':already,'matchedTonnes':amount,'issues':issues,'rationale':s(x.get('rationale'),420),'digests':dig}
  def valid(l):
   if not isinstance(l,gl.vm.Return):return False
   try:
    g=l.calldata;docs=[];dig=[]
    for n,u in enumerate(urls):
     raw=gl.nondet.web.get(u).body[:15000];body=raw.decode(errors='replace') if isinstance(raw,bytes) else str(raw);dig.append(hashlib.sha256(raw if isinstance(raw,bytes) else raw.encode()).hexdigest());docs.append({'source_index':n,'body':body})
    if g['digests']!=dig or g['verdict'] not in ('VALID','DUPLICATE','MISMATCH','INSUFFICIENT') or (g['verdict']=='VALID' and g['matchedTonnes']!=int(c.tonnes)):return False
    q='Independently verify certificate status, exact tonnes and additionality from all three source roles. JSON only {"valid":true}. PROPOSAL:'+json.dumps({'verdict':g['verdict'],'retired':g['registryRetired'],'tonnes':g['matchedTonnes'],'issues':g['issues']})+' DOCS:'+json.dumps(docs)
    return bool(obj(gl.nondet.exec_prompt(ELIGIBILITY+' '+q,response_format='json')).get('valid',False))
   except:return False
  return gl.vm.run_nondet_unsafe(run,valid)
 @gl.public.write
 def register(self,i:str,project:str,vintage:u256,tonnes:u256,registry_url:str,method_url:str,claim_url:str)->None:
  k=key(i)
  if k in self.certificates or k in self.retired:raise gl.vm.UserError('[EXPECTED] duplicate certificate id')
  urls=[https(registry_url),https(method_url),https(claim_url)]
  if len(set(urls))!=3 or int(tonnes)<=0 or int(vintage)<2000 or len(s(project))<3:raise gl.vm.UserError('[EXPECTED] complete distinct certificate evidence')
  self.certificates[k]=Certificate(gl.message.sender_address,s(project),vintage,tonnes,urls[0],urls[1],urls[2],'REGISTERED','{}')
 @gl.public.write
 def verify_and_retire(self,i:str)->None:
  k,c=self._get(i)
  if gl.message.sender_address!=c.owner or c.state!='REGISTERED':raise gl.vm.UserError('[EXPECTED] owner and active certificate required')
  result=self._verify(c);c.proof=json.dumps(result,sort_keys=True)
  if result['verdict']=='VALID':c.state='RETIRED';self.retired[k]=True
  else:c.state='REJECTED'
 @gl.public.view
 def get_certificate(self,i:str)->dict:
  k,c=self._get(i);return {'id':k,'owner':c.owner.as_hex,'project':c.project,'vintage':int(c.vintage),'tonnes':int(c.tonnes),'sources':[c.registry_url,c.method_url,c.claim_url],'state':c.state,'proof':json.loads(c.proof)}
