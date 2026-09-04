import json,re,time
from pathlib import Path
from genlayer_py import create_client,create_account
from genlayer_py.chains import studionet
ROOT=Path(__file__).parents[1];ENV=(ROOT.parents[3]/'accounts.env').read_text()
def secret(n):return re.search(rf'^ACCOUNT_{n}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)',ENV,re.M).group(1).strip()
deploy=json.loads((ROOT/"records/deployment.json").read_text());contract=deploy['contract']
account=create_account(account_private_key=secret(3));client=create_client(chain=studionet,account=account)
def send(c,fn,args):
 tx=c.write_contract(address=contract,function_name=fn,args=args);print(fn,tx,flush=True)
 c.wait_for_transaction_receipt(transaction_hash=tx,status='ACCEPTED',retries=18,interval=10000);info=c.get_transaction(transaction_hash=tx)
 if info.get('status_name')!='ACCEPTED' or not any(r.get('execution_result')=='SUCCESS' for r in info.get('consensus_data',{}).get('leader_receipt',[])):raise RuntimeError({'function':fn,'tx':tx,'status':info.get('status_name'),'execution':info.get('tx_execution_result_name')})
 return tx
def negative(c,fn,args,label):
 try:c.simulate_write_contract(address=contract,function_name=fn,args=args);raise RuntimeError(label+' unexpectedly passed')
 except RuntimeError:raise
 except Exception:print('negative',label,'rejected',flush=True)
certificate='CL-'+str(int(time.time()))
base=f'https://raw.githubusercontent.com/sanshos1/carbon-ledger/{deploy["evidenceCommit"]}/specimens/'
args=[certificate,'Forest Delta',2025,50,base+'registry-record.txt',base+'methodology.txt',base+'beneficiary-claim.txt']
registered=send(client,'register',args)
negative(client,'register',args,'duplicate id')
verified=send(client,'verify_and_retire',[certificate])
state=client.read_contract(address=contract,function_name='get_certificate',args=[certificate])
assert state['state']=='RETIRED' and state['proof']['verdict']=='VALID' and state['proof']['matchedTonnes']==50 and len(state['proof']['digests'])==3
proof={'certificateId':certificate,'transactions':{'register':registered,'verify':verified},'state':state}
(ROOT/"records/retirement.json").parent.mkdir(parents=True,exist_ok=True)
(ROOT/"records/retirement.json").write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
