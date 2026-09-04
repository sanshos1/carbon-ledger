from conftest import CONTRACT
REG='https://registry.example/credits/C7';MET='https://method.example/additionality/M2';CLAIM='https://buyer.example/claim/C7'
def mocks(vm):
 vm.strict_mocks=True;vm.check_pickling=True
 vm.mock_web(r'registry\.example',{'status':200,'body':'Certificate C7 issued, active, 50 tonnes, vintage 2025.'});vm.mock_web(r'method\.example',{'status':200,'body':'M2 additionality requirements satisfied.'});vm.mock_web(r'buyer\.example',{'status':200,'body':'Buyer requests retirement of C7 for 50 tonnes.'})
 vm.mock_llm(r'.*Carbon certificate integrity verification.*','{"verdict":"VALID","registry_retired":false,"matched_tonnes":50,"issue_indexes":[],"rationale":"All records align."}')
def test_valid_certificate_retires_once(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);mocks(direct_vm);c.register(' c7 ','Forest Delta',2025,50,REG,MET,CLAIM);c.verify_and_retire('C7');v=c.get_certificate(' c7 ')
 assert v['state']=='RETIRED' and v['proof']['matchedTonnes']==50 and len(v['proof']['digests'])==3
 with direct_vm.expect_revert('owner and active'):c.verify_and_retire('C7')
def test_duplicate_certificate_and_sources_rejected(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);c.register('C8','Forest Delta',2025,50,REG,MET,CLAIM)
 with direct_vm.expect_revert('duplicate certificate id'):c.register(' c8 ','Forest Delta',2025,50,REG,MET,CLAIM)
 with direct_vm.expect_revert('distinct certificate evidence'):c.register('C9','Forest Delta',2025,50,REG,REG,CLAIM)
def test_forged_amount_fails_validator(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);mocks(direct_vm);c.register('C10','Forest Delta',2025,50,REG,MET,CLAIM);result=c._verify(c.certificates['C10']);direct_vm.mock_llm(r'.*Independently verify.*','{"valid":true}');assert direct_vm.run_validator(leader_result=result) is True;forged=dict(result);forged['matchedTonnes']=500
 assert direct_vm.run_validator(leader_result=forged) is False
