"""仅验证文档一致性；不把静态检查报告当软件测试证据。"""
from pathlib import Path
import csv, hashlib, json, re, sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8')
errors = []
checks = {}

def require(condition, message):
    if not condition:
        errors.append(message)

docs = sorted(ROOT.glob('[0-9][0-9]-*.md'))
checks['engineeringDocumentCount'] = len(docs)
require(len(docs) == 45 and {int(p.name[:2]) for p in docs} == set(range(45)), '工程文档00～44缺失或重复')
checks['utf8FilesChecked'] = 0
for path in ROOT.rglob('*'):
    if path.is_file() and path.suffix in {'.md','.py','.json','.csv'}:
        try:
            path.read_text(encoding='utf-8-sig')
            checks['utf8FilesChecked'] += 1
        except UnicodeError:
            errors.append(f'UTF-8读取失败: {path.relative_to(ROOT)}')

links = 0
for path in list(docs) + list((ROOT/'contracts').glob('*.md')) + list((ROOT/'templates').glob('*.md')):
    body = path.read_text(encoding='utf-8')
    require(sum(1 for line in body.splitlines() if line.startswith('```')) % 2 == 0,
            f'代码围栏不成对: {path.name}')
    require('cite' not in body, f'工程文档含失效会话引用: {path.name}')
    for target in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', body):
        if re.match(r'^[a-z]+://',target):
            continue
        target = target.strip('<>')
        filename, _, anchor = target.partition('#')
        dest = path.parent/filename if filename else path
        # 本次检查结束时生成报告；首次运行时该自引用尚不存在。
        require(dest.exists() or dest == ROOT/'validation-report.json',f'断链: {path.name} → {target}')
        if anchor and dest.exists():
            require(f'id="{anchor}"' in dest.read_text(encoding='utf-8'),
                    f'缺少显式锚点: {path.name} → {target}')
        links += 1
checks['localLinksChecked'] = links

with (ROOT/'traceability.csv').open(encoding='utf-8-sig',newline='') as f:
    rows = list(csv.DictReader(f))
reqids = [r['需求ID'] for r in rows]
tcids = [r['验收测试'] for r in rows]
require(len(reqids)==48 and len(set(reqids))==48,'需求编号缺失或重复')
require(len(tcids)==48 and len(set(tcids))==48,'测试关联缺失或重复')
srs=(ROOT/'01-prd.md').read_text(encoding='utf-8')
matrix=(ROOT/'23-需求追踪矩阵.md').read_text(encoding='utf-8')
cases=(ROOT/'30-测试用例与验收规程.md').read_text(encoding='utf-8')
for row in rows:
    rid,tid=row['需求ID'],row['验收测试']
    require(rid in srs and rid in matrix,f'需求未同步: {rid}')
    require(f'### {tid} ' in cases and f'id="{tid.lower()}"' in cases,f'测试缺失: {tid}')
    require((ROOT/row['设计文档']).exists(), f'设计文档缺失: {rid}')
    require(row['首次增量'] in {f'I{i}' for i in range(10)}|{'F1+'}, f'错误增量: {rid}')
    if row['实现位置'] != '未实现':
        for location in row['实现位置'].split(';'):
            require((ROOT.parents[1]/location).exists(), f'实现路径不存在: {rid} {location}')
        for evidence in row['证据'].split(';'):
            require((ROOT/evidence).exists(), f'执行记录不存在: {rid} {evidence}')
        require('部分实现' in row['状态'], f'当前不得将父需求标为已验收: {rid}')
checks['requirementsChecked'] = len(reqids)
checks['testCasesChecked'] = len(tcids)
checks['traceabilityCoverage'] = '48/48 requirements linked to design, increment and test'

source_rec=json.loads((ROOT/'sources'/'来源记录.json').read_text(encoding='utf-8'))
source_file=ROOT/'sources'/source_rec['archivedFile']
source_hash=hashlib.sha256(source_file.read_bytes()).hexdigest()
require(source_hash==source_rec['sha256'],'母文档副本hash不匹配')
original=Path(source_rec['sourcePath'])
if original.exists():
    require(hashlib.sha256(original.read_bytes()).hexdigest()==source_hash,'母文档与原路径内容不一致')
checks['sourceSha256']=source_hash
checks['sourceArchiveVerified']=True

source_text=source_file.read_text(encoding='utf-8-sig')
source_sections=set(int(n) for n in re.findall(r'^#{1,2}\s+(\d+)\.',source_text,re.M))
require(set(range(129)).issubset(source_sections),'原文主要章节0～128不完整')
coverage=(ROOT/'29-范围覆盖与母文档映射.md').read_text(encoding='utf-8')
covered=set()
for start,end in re.findall(r'^\|(\d+)～(\d+)\|',coverage,re.M):
    covered.update(range(int(start),int(end)+1))
require(set(range(129)).issubset(covered),'母文档覆盖表未覆盖0～128')
checks['sourceSectionCoverage']='0–128 covered by chapter mapping'

schemas=list((ROOT/'contracts').glob('*.schema.json'))
for path in schemas:
    schema=json.loads(path.read_text(encoding='utf-8'))
    require(schema.get('$schema')=='https://json-schema.org/draft/2020-12/schema',f'模式版本错误: {path.name}')
checks['jsonSchemasParsed']=len(schemas)
try:
    import jsonschema
except ImportError:
    checks['schemaMetaValidation']='unavailable: jsonschema not installed; parsed JSON only'
else:
    for path in schemas:
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding='utf-8')))
    envelope=json.loads((ROOT/'contracts'/'ipc-envelope.schema.json').read_text(encoding='utf-8'))
    example=json.loads((ROOT/'contracts'/'ipc-request.example.json').read_text(encoding='utf-8'))
    validator=jsonschema.Draft202012Validator(envelope,format_checker=jsonschema.FormatChecker())
    require(not list(validator.iter_errors(example)),'合法IPC示例不通过schema')
    invalid=dict(example); invalid.pop('expectedRevision')
    require(bool(list(validator.iter_errors(invalid))),'schema未拒绝缺少revision的修改请求')
    invalid=dict(example,protocolVersion=2)
    require(bool(list(validator.iter_errors(invalid))),'schema未拒绝未知protocolVersion')
    checks['schemaMetaValidation']='passed: schema validity, positive IPC example, two negative examples'

checks['generatedMarkdownCharacters']=sum(len(p.read_text(encoding='utf-8')) for p in docs)
checks['templateCount']=len(list((ROOT/'templates').glob('*.md')))
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'scope':'Documentation structure and evidence-link existence only; actual software test results are in evidence/',
        'status':'passed' if not errors else 'failed','checks':checks,'errors':errors,
        'limitations':['Runtime schema coverage does not imply full requirement acceptance.',
                      'Physical manufacturing, body meshes and AI models remain unvalidated.',
                      'Parent acceptance cases remain incomplete; executed subcases are tracked in document 34.']}
(ROOT/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
