# -*- coding: utf-8 -*-
"""
gen_italian_html.py
加载 gen_italian.py 的数据(AVERE/ESSERE/MODELS/VERBS)与变位引擎(ENGINE_JS)，
执行 node 验收，并生成自包含单文件 HTML：verbo-italiano.html
"""
import runpy, os, json, base64, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "verbo-italiano.html")

ns = runpy.run_path(os.path.join(HERE, "gen_italian.py"))
VERBS = ns["VERBS"]
MODELS = ns["MODELS"]
AVERE = ns["AVERE"]
ESSERE = ns["ESSERE"]
ENGINE_JS = ns["ENGINE_JS"]

NODE = r"C:\Users\迪丽希斯\.workbuddy\binaries\node\versions\22.22.2-2\node.exe"
if not os.path.exists(NODE):
    NODE = "node"


def minjs(s):
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())


def build_data_js():
    verbs_data = []
    for v in VERBS:
        is_irr = 1 if (v["b"] or v["ch"] or v["pp"]) else 0
        verbs_data.append({
            "i": v["i"], "c": v["c"], "aux": v["aux"], "ch": v["ch"],
            "pp": v["pp"], "b": v["b"], "x": v["x"], "bi": v.get("bi", ""), "ir": is_irr,
        })
    return ("var AVERE=" + json.dumps(AVERE, ensure_ascii=False, separators=(",", ":")) +
            ";\nvar ESSERE=" + json.dumps(ESSERE, ensure_ascii=False, separators=(",", ":")) +
            ";\nvar MODELS=" + json.dumps(MODELS, ensure_ascii=False, separators=(",", ":")) +
            ";\nvar VERBS=" + json.dumps(verbs_data, ensure_ascii=False, separators=(",", ":")) + ";\n")


# ---------------------------------------------------------------------------
# Node 验收
# ---------------------------------------------------------------------------
def run_node_test():
    testdir = os.path.join(HERE, "_engine_test")
    os.makedirs(testdir, exist_ok=True)
    data_js = build_data_js()
    with open(os.path.join(testdir, "engine.js"), "w", encoding="utf-8") as f:
        f.write(data_js + ENGINE_JS)
    test = r"""
const fs=require('fs');
const path=require('path');
eval(fs.readFileSync(path.join(__dirname,'engine.js'),'utf8'));
function findVerb(inf){return VERBS.find(function(v){return v.i===inf;});}
var fails=0;
function expect(inf,label,got,want){
  if(got!==want){fails++;console.log('  ✗ ['+inf+'] '+label+'  got='+got+'  want='+want);}
}
function show(inf){
  var v=findVerb(inf);
  if(!v){console.log('NO EXISTE:',inf);fails++;return;}
  var c=buildFull(v);
  console.log('=== '+inf+' ('+v.c+') aux='+c.aux+(c.refl?' REFL':'')+' ===');
  console.log(' pres:   '+c.ind_pres.join(' | '));
  console.log(' perf:   '+c.ind_perf.join(' | '));
  console.log(' imperf: '+c.ind_imperf.join(' | '));
  console.log(' plus:   '+c.ind_plus.join(' | '));
  console.log(' remoto: '+c.ind_remoto.join(' | '));
  console.log(' rem_ant:'+c.ind_remoto_ant.join(' | '));
  console.log(' fut:    '+c.ind_fut.join(' | '));
  console.log(' fut_perf:'+c.ind_fut_perf.join(' | '));
  console.log(' subj:   '+c.subj_pres.join(' | '));
  console.log(' subj_imp:'+c.subj_imperf.join(' | '));
  console.log(' cond:   '+c.cond_pres.join(' | '));
  console.log(' cond_pf:'+c.cond_perf.join(' | '));
  console.log(' imp:    '+c.imp.join(' | '));
  console.log(' inf/comp:'+c.inf+' / '+c.inf_comp+'  ger/comp:'+c.ger+' / '+c.ger_comp+'  pp:'+c.pp+'  ppr:'+c.ppr);
  console.log('');
}
// 规则动词
show('parlare'); show('credere'); show('finire'); show('aprire'); show('dormire');
// 拼写修正
show('cercare'); show('pagare'); show('cominciare'); show('lasciare'); show('inviare');
// 完全不规则
['essere','avere','andare','dare','stare','fare','dire','bere','sapere','volere','potere','dovere',
 'venire','tenere','uscire','sedere','rimanere','salire','morire','udire','porre','trarre','condurre',
 'cogliere','scegliere','togliere','sciogliere','spegnere','valere','parere','piacere','tacere','nuocere',
 'dolere','godere','apparire','comparire','scomparire'].forEach(show);
// 前缀派生
show('ottenere'); show('contenere'); show('riuscire'); show('divenire');
// 自反
show('lavarsi'); show('alzarsi'); show('vestirsi');
// ===== 断言校验（锁定正确性，防止回归）=====
function chk(inf,field,idx,want){
  var v=findVerb(inf);
  if(!v){fails++;console.log('  X NO EXISTE: '+inf);return;}
  var c=buildFull(v);
  var got = Array.isArray(c[field]) ? c[field][idx] : c[field];
  if(got!==want){fails++;console.log('  X ['+inf+'] '+field+'['+idx+'] got='+got+' want='+want);}
}
function chkAux(inf,want){var v=findVerb(inf);if(!v){fails++;return;}var c=buildFull(v);if(c.aux!==want){fails++;console.log('  X ['+inf+'] aux got='+c.aux+' want='+want);}}
function chkRefl(inf,want){var v=findVerb(inf);var c=buildFull(v);if(!!c.refl!==want){fails++;console.log('  X ['+inf+'] refl got='+c.refl+' want='+want);}}
// regole
chk('parlare','ind_pres',0,'parlo'); chk('parlare','ind_pres',5,'parlano'); chk('parlare','ind_fut',0,'parlerò'); chk('parlare','imp',1,'parla');
chk('credere','ind_pres',0,'credo'); chk('credere','ind_pres',5,'credono');
chk('finire','ind_pres',0,'finisco'); chk('finire','ind_pres',2,'finisce'); chk('finire','ind_pres',3,'finiamo'); chk('finire','ind_pres',5,'finiscono'); chk('finire','imp',1,'finisci');
chk('dormire','ind_pres',0,'dormo'); chk('dormire','ind_pres',5,'dormono');
// ortografia
chk('cercare','ind_pres',1,'cerchi'); chk('cercare','ind_pres',3,'cerchiamo'); chk('cercare','ind_fut',0,'cercherò');
chk('pagare','ind_pres',1,'paghi'); chk('pagare','ind_pres',3,'paghiamo');
chk('cominciare','ind_pres',0,'comincio'); chk('cominciare','ind_pres',1,'cominci');
chk('lasciare','ind_pres',0,'lascio'); chk('lasciare','ind_pres',1,'lasci');
chk('inviare','ind_pres',0,'invio'); chk('inviare','ind_pres',1,'invii'); chk('inviare','ind_pres',4,'inviate'); chk('inviare','imp',1,'invia');
chk('studiare','ind_pres',0,'studio'); chk('studiare','ind_pres',1,'studi'); chk('studiare','ind_pres',2,'studia'); chk('studiare','subj_pres',1,'studi'); chk('studiare','imp',1,'studia'); chk('studiare','imp',2,'studi');
chk('odiare','ind_pres',1,'odi'); chk('viaggiare','ind_pres',1,'viaggi'); chk('sbagliare','ind_pres',1,'sbagli');
// irregolari completi
chk('essere','ind_pres',0,'sono'); chk('essere','ind_pres',2,'è'); chk('essere','ind_pres',5,'sono'); chk('essere','ind_remoto',0,'fui'); chk('essere','ind_fut',0,'sarò'); chk('essere','imp',1,'sii');
chk('avere','ind_pres',0,'ho'); chk('avere','ind_pres',2,'ha'); chk('avere','ind_remoto',0,'ebbi'); chk('avere','imp',1,'abbi');
chk('andare','ind_pres',0,'vado'); chk('andare','ind_pres',5,'vanno'); chk('andare','imp',1,"va'"); chkAux('andare','e');
chk('dare','ind_pres',0,'do'); chk('dare','ind_pres',2,'dà'); chk('dare','ind_remoto',0,'diedi');
chk('stare','ind_pres',0,'sto'); chk('stare','ind_remoto',0,'stetti'); chk('stare','imp',1,"sta'");
chk('fare','ind_pres',0,'faccio'); chk('fare','ind_pres',5,'fanno'); chk('fare','ind_remoto',0,'feci');
chk('dire','ind_pres',0,'dico'); chk('dire','ind_pres',5,'dicono'); chk('dire','ind_remoto',0,'dissi');
chk('bere','ind_pres',0,'bevo'); chk('bere','ind_remoto',0,'bevvi'); chk('bere','ind_fut',0,'berrò');
chk('sapere','ind_pres',0,'so'); chk('sapere','ind_pres',5,'sanno'); chk('sapere','imp',1,'sappi');
chk('volere','ind_pres',0,'voglio'); chk('volere','ind_pres',2,'vuole'); chk('volere','imp',1,'vogli');
chk('potere','ind_pres',0,'posso'); chk('potere','ind_pres',2,'può'); chk('potere','imp',1,'—');
chk('dovere','ind_pres',0,'devo'); chk('dovere','imp',1,'—');
chk('venire','ind_pres',0,'vengo'); chk('venire','ind_pres',3,'veniamo'); chkAux('venire','e');
chk('tenere','ind_pres',0,'tengo'); chk('tenere','ind_pres',1,'tieni'); chk('tenere','ind_fut',0,'terrò');
chk('uscire','ind_pres',0,'esco'); chk('uscire','ind_pres',5,'escono'); chkAux('uscire','e');
chk('salire','ind_pres',0,'salgo'); chk('salire','ind_pres',5,'salgono'); chkAux('salire','e');
chk('morire','ind_pres',0,'muoio'); chk('morire','pp',0,'morto'); chkAux('morire','e');
chk('sedere','ind_pres',0,'siedo'); chk('sedere','ind_pres',2,'siede');
chk('porre','ind_pres',0,'pongo'); chk('porre','ind_remoto',0,'posi'); chk('porre','pp',0,'posto');
chk('trarre','ind_pres',0,'traggo'); chk('trarre','ind_pres',5,'traggono'); chk('trarre','ind_remoto',0,'trassi'); chk('trarre','pp',0,'tratto');
chk('condurre','ind_pres',0,'conduco'); chk('condurre','ind_remoto',0,'condussi'); chk('condurre','pp',0,'condotto');
chk('produrre','ind_pres',0,'produco'); chk('produrre','ind_remoto',0,'produssi'); chk('produrre','pp',0,'prodotto');
chk('introdurre','ind_pres',0,'introduco'); chk('introdurre','ind_pres',1,'introduci');
chk('cogliere','ind_pres',0,'colgo'); chk('cogliere','ind_pres',5,'colgono'); chk('cogliere','pp',0,'colto');
chk('valere','ind_pres',0,'valgo'); chk('valere','ind_pres',5,'valgono'); chk('valere','ind_remoto',0,'valsi'); chkAux('valere','e');
chk('parere','ind_pres',0,'paio'); chk('parere','imp',1,'—'); chkAux('parere','e');
chk('piacere','ind_pres',0,'piaccio'); chk('piacere','ind_pres',5,'piacciono'); chk('piacere','ind_remoto',0,'piacqui'); chkAux('piacere','e');
chk('tacere','ind_pres',0,'taccio'); chk('tacere','pp',0,'taciuto');
chk('nuocere','ind_pres',0,'nuoccio'); chk('nuocere','ind_remoto',0,'nocqui'); chk('nuocere','pp',0,'nociuto');
chk('spegnere','ind_pres',0,'spengo'); chk('spegnere','pp',0,'spento');
chk('togliere','ind_pres',0,'tolgo'); chk('togliere','pp',0,'tolto');
chk('sciogliere','ind_pres',0,'sciolgo'); chk('sciogliere','pp',0,'sciolto');
chk('udire','ind_pres',0,'odo'); chk('udire','ind_pres',2,'ode');
chk('rimanere','ind_pres',0,'rimango'); chk('rimanere','ind_pres',5,'rimangono'); chk('rimanere','ind_remoto',0,'rimasi'); chkAux('rimanere','e');
chk('apparire','ind_pres',0,'appaio'); chk('apparire','ind_pres',5,'appaiono'); chkAux('apparire','e');
chk('comparire','ind_pres',0,'compaio'); chk('comparire','ind_remoto',5,'comparvero'); chkAux('comparire','e');
chk('scomparire','ind_pres',0,'scompaio'); chkAux('scomparire','e');
chk('divenire','ind_pres',0,'divengo'); chkAux('divenire','e');
chk('riuscire','ind_pres',0,'riesco'); chk('riuscire','ind_pres',5,'riescono'); chkAux('riuscire','e');
// prefisso
chk('ottenere','ind_pres',0,'ottengo'); chk('ottenere','imp',1,'ottieni'); chk('ottenere','ind_fut',0,'otterrò');
chk('contenere','ind_pres',0,'contengo'); chk('contenere','ind_pres',1,'contieni');
chk('appartenere','ind_pres',0,'appartengo'); chkAux('appartenere','e');
chk('sostenere','ind_pres',0,'sostengo');
// riflessivi
chk('lavarsi','ind_pres',0,'mi lavo'); chk('lavarsi','ind_pres',1,'ti lavi'); chk('lavarsi','imp',1,'lavati'); chk('lavarsi','inf',0,'lavarsi'); chkAux('lavarsi','e'); chkRefl('lavarsi',true);
chk('alzarsi','ind_pres',0,'mi alzo'); chk('alzarsi','pp',0,'alzato'); chkRefl('alzarsi',true);
chk('vestirsi','ind_pres',0,'mi vesto'); chk('vestirsi','imp',1,'vestiti'); chkRefl('vestirsi',true);
chk('sedersi','ind_pres',0,'mi siedo'); chk('sedersi','imp',1,'siediti'); chkRefl('sedersi',true);
// imperativo negativo
chk('parlare','imp_neg',1,'non parlare'); chk('parlare','imp_neg',2,'non parli'); chk('parlare','imp_neg',3,'non parliamo'); chk('parlare','imp_neg',4,'non parlate'); chk('parlare','imp_neg',5,'non parlino');
chk('finire','imp_neg',1,'non finire'); chk('finire','imp_neg',4,'non finite');
chk('lavarsi','imp_neg',1,'non ti lavare'); chk('lavarsi','imp_neg',2,'non si lavi'); chk('lavarsi','imp_neg',3,'non ci laviamo'); chk('lavarsi','imp_neg',4,'non vi lavate'); chk('lavarsi','imp_neg',5,'non si lavino');
// participio passato 性数一致
chk('parlare','pp4',0,'parlato'); chk('parlare','pp4',1,'parlata'); chk('parlare','pp4',2,'parlati'); chk('parlare','pp4',3,'parlate');
chk('morire','pp4',0,'morto'); chk('morire','pp4',1,'morta'); chk('morire','pp4',2,'morti'); chk('morire','pp4',3,'morte');
chk('trarre','pp4',0,'tratto'); chk('trarre','pp4',1,'tratta'); chk('trarre','pp4',2,'tratti'); chk('trarre','pp4',3,'tratte');
chk('condurre','pp4',0,'condotto'); chk('condurre','pp4',3,'condotte');

console.log('TOTAL VERBOS:', VERBS.length);
console.log('ASSERTIONS DONE, fails='+fails);
console.log(fails===0 ? 'NODE TEST OK' : ('NODE TEST FAILED: '+fails+' diffs'));
"""
    with open(os.path.join(testdir, "test.js"), "w", encoding="utf-8") as f:
        f.write(test)
    r = subprocess.run([NODE, "test.js"], cwd=testdir, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout)
    if r.returncode != 0:
        print("STDERR:", r.stderr)
        sys.exit(1)
    return testdir


# ---------------------------------------------------------------------------
# 意大利语界面
# ---------------------------------------------------------------------------
UI_JS = r"""
// ===== Interfaccia italiana =====
(function(){
  var listEl=document.getElementById('vlist');
  var idxEl=document.getElementById('idx');
  var searchEl=document.getElementById('search');
  var detailEl=document.getElementById('detail');
  var countEl=document.getElementById('vcount');
  var titleEl=document.getElementById('vtitle');
  var curLetter='', curQuery='', selected=null, cache={};
  var LETTERS='ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

  function norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
  function verbsFiltered(){
    var q=norm(curQuery);
    return VERBS.filter(function(v){
      if(curLetter && v.i.charAt(0).toUpperCase()!==curLetter) return false;
      if(q){var hay=norm(v.i)+' '+norm(v.c);if(hay.indexOf(q)<0)return false;}
      return true;
    });
  }
  function renderIndex(){
    var present={};
    VERBS.forEach(function(v){present[v.i.charAt(0).toUpperCase()]=1;});
    idxEl.innerHTML=LETTERS.map(function(L){
      return '<button class="idxbtn'+(present[L]?'':' off')+'" data-l="'+L+'">'+L+'</button>';
    }).join('');
  }
  var selEl=null,listTimer=null;
  function itemHtml(v){
    var sel=(selected&&selected.i===v.i)?' sel':'';
    return '<div class="vitem'+sel+'" data-inf="'+v.i+'">'+
      '<span class="vinf">'+v.i+'</span>'+
      '<span class="vcn">'+v.c+'</span>'+
      (v.ir?'<span class="tag irr">不规则</span>':'<span class="tag reg">规则</span>')+
      '</div>';
  }
  function renderList(){
    var vs=verbsFiltered();
    countEl.textContent=vs.length+' / '+VERBS.length+' 个动词';
    if(listTimer){clearTimeout(listTimer);listTimer=null;}
    if(!vs.length){listEl.innerHTML='<div class="empty">没有匹配的动词</div>';selEl=null;return;}
    var CH=150;
    listEl.innerHTML=vs.slice(0,CH).map(itemHtml).join('');
    if(vs.length>CH){
      var i=CH;
      (function step(){
        if(i>=vs.length)return;
        var end=Math.min(i+CH,vs.length);
        var frag=document.createElement('div');
        frag.innerHTML=vs.slice(i,end).map(itemHtml).join('');
        while(frag.firstChild)listEl.appendChild(frag.firstChild);
        i=end;
        listTimer=setTimeout(step,1);
      })();
    }
    selEl=listEl.querySelector('.vitem.sel');
  }
  function tenseLabel(key){
    var m={
      ind_pres:['陈述式现在时','Presente'],
      ind_perf:['现在完成时','Passato prossimo'],
      ind_imperf:['过去未完成时','Imperfetto'],
      ind_plus:['过去完成时','Trapassato prossimo'],
      ind_remoto:['简单过去时','Passato remoto'],
      ind_remoto_ant:['先过去时','Trapassato remoto'],
      ind_fut:['将来时','Futuro semplice'],
      ind_fut_perf:['将来完成时','Futuro anteriore'],
      subj_pres:['虚拟式现在时','Congiuntivo presente'],
      subj_perf:['虚拟式现在完成时','Congiuntivo passato'],
      subj_imperf:['虚拟式过去未完成时','Congiuntivo imperfetto'],
      subj_plus:['虚拟式过去完成时','Congiuntivo trapassato'],
      cond_pres:['条件式现在时','Condizionale presente'],
      cond_perf:['条件式过去时','Condizionale passato'],
      imp:['命令式肯定','Imperativo (affermativo)'],
      imp_neg:['命令式否定','Imperativo (negativo)']
    };
    return m[key]||[key,key];
  }
  function tenseBlock(key,arr){
    var lb=tenseLabel(key);
    var rows=arr.map(function(f,i){
      return '<div class="trow'+(i===0?' yo':'')+'"><span class="tper">'+PRON[i]+'</span><span class="tform">'+f+'</span></div>';
    }).join('');
    return '<div class="tense"><div class="tname"><b>'+lb[0]+'</b><i>'+lb[1]+'</i></div>'+rows+'</div>';
  }
  function moodBlock(color,title,keys){
    var inner='';
    keys.forEach(function(k){inner+=tenseBlock(k,cache[selected.i][k]);});
    return '<section class="mood" style="--mc:'+color+'"><h3 class="mhead">'+title+'</h3><div class="tensegrid">'+inner+'</div></section>';
  }
  function select(inf){
    var v=null;
    VERBS.forEach(function(x){if(x.i===inf)v=x;});
    if(!v)return;
    selected=v;
    if(!cache[inf])cache[inf]=buildFull(JSON.parse(JSON.stringify(v)));
    var c=cache[inf];
    titleEl.innerHTML='<span class="big">'+v.i+'</span><span class="cn">'+v.c+'</span>'+
      (v.ir?'<span class="tag irr">不规则</span>':'<span class="tag reg">规则</span>')+
      '<span class="tag type">-'+v.i.slice(-3)+'</span>'+
      (c.refl?'<span class="tag refl">自反</span>':'');
    var html='';
    html+=moodBlock('#009246','陈述式 Indicativo',['ind_pres','ind_perf','ind_imperf','ind_plus','ind_remoto','ind_remoto_ant','ind_fut','ind_fut_perf']);
    html+=moodBlock('#1E5AA8','虚拟式 Congiuntivo',['subj_pres','subj_perf','subj_imperf','subj_plus']);
    html+=moodBlock('#CE2B37','条件式 Condizionale',['cond_pres','cond_perf']);
    html+=moodBlock('#B8860B','命令式 Imperativo',['imp','imp_neg']);
    html+='<section class="mood imp"><h3 class="mhead">非人称形式 Forme impersonali</h3><div class="impgrid">'+
      '<div class="impcell"><span class="ilab">原形 Infinito</span><b>'+c.inf+'</b></div>'+
      '<div class="impcell"><span class="ilab">复合原形 Infinito composto</span><b>'+c.inf_comp+'</b></div>'+
      '<div class="impcell"><span class="ilab">副动词 Gerundio</span><b>'+c.ger+'</b></div>'+
      '<div class="impcell"><span class="ilab">复合副动词 Gerundio composto</span><b>'+c.ger_comp+'</b></div>'+
      '<div class="impcell"><span class="ilab">现在分词 Participio presente</span><b>'+c.ppr+'</b></div>'+
      '<div class="impcell"><span class="ilab">过去分词 Participio passato（阳单/阴单/阳复/阴复）</span><b>'+c.pp4.join(' · ')+'</b></div>'+
      '</div></section>';
    detailEl.innerHTML=html;
    (function alignLabels(){
      var ts=detailEl.querySelectorAll('.tper'),max=0;
      ts.forEach(function(t){t.style.width='auto';});
      ts.forEach(function(t){if(t.scrollWidth>max)max=t.scrollWidth;});
      ts.forEach(function(t){t.style.width=max+'px';});
    })();
    if(selEl)selEl.classList.remove('sel');
    selEl=listEl.querySelector('.vitem[data-inf="'+inf+'"]');
    if(selEl)selEl.classList.add('sel');
    detailEl.scrollTop=0;
  }
  idxEl.addEventListener('click',function(e){
    var b=e.target.closest('.idxbtn');
    if(!b||b.classList.contains('off'))return;
    curLetter=(curLetter===b.dataset.l)?'':b.dataset.l;
    idxEl.querySelectorAll('.idxbtn').forEach(function(x){x.classList.toggle('act',x===b&&!!curLetter);});
    renderList();
  });
  searchEl.addEventListener('input',function(){curQuery=searchEl.value;renderList();});
  listEl.addEventListener('click',function(e){
    var el=e.target.closest('.vitem');
    if(el)select(el.getAttribute('data-inf'));
  });
  renderIndex();select('essere');renderList();
})();
"""

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
:root{--green:#009246;--red:#CE2B37;--gold:#B8860B;--blue:#1E5AA8;--ink:#2b2723;--sub:#8a837a;--bg:#F7F7F4;--card:#ffffff;--line:#e6e3dc;--irr:#FFF8E6;--radius:20px;--radius-sm:14px;--radius-xs:12px;--shadow:0 6px 20px rgba(0,0,0,.07);--shadow-soft:0 3px 10px rgba(0,0,0,.05)}
html,body{background:var(--bg);color:var(--ink);font-family:"Segoe UI","Microsoft YaHei",system-ui,sans-serif}
header{position:sticky;top:0;z-index:50;background:linear-gradient(135deg,#009246,#CE2B37);color:#fff;padding:14px 20px 18px;border-radius:0 0 26px 26px;box-shadow:0 8px 26px rgba(0,0,0,.18)}
header h1{font-size:20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
header h1 .flag{letter-spacing:2px}
header .sub{display:flex;align-items:center;gap:10px;margin-top:8px}
header .sub .logo{height:24px;width:24px;border-radius:10px;object-fit:cover;background:#fff;padding:1px;box-shadow:0 1px 4px rgba(0,0,0,.3)}
header .sub .brand{font-size:16px;font-weight:800;letter-spacing:2px;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.3)}
.toprow{display:flex;gap:10px;align-items:center;margin-top:10px;flex-wrap:wrap}
#search{flex:1;min-width:200px;padding:11px 16px;border:none;border-radius:999px;font-size:14px;outline:none;box-shadow:0 2px 8px rgba(0,0,0,.12)}
#vcount{font-size:12px;opacity:.95;white-space:nowrap}
#idx{display:flex;flex-wrap:wrap;gap:5px;margin:12px 20px 0}
.idxbtn{width:36px;height:36px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:700;cursor:pointer;font-size:14px;transition:transform .12s ease,background .15s ease,box-shadow .15s ease;box-shadow:var(--shadow-soft)}
.idxbtn:hover{background:var(--gold);transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.12)}
.idxbtn.off{opacity:.3;cursor:default}
.idxbtn.act{background:var(--green);color:#fff;border-color:var(--green)}
.layout{display:grid;grid-template-columns:minmax(330px,400px) minmax(0,1fr);gap:18px;padding:16px 20px 40px;align-items:start;max-width:1720px;margin:0 auto}
.rcol{min-width:0}
.vpanel{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:12px;max-height:calc(100vh - 170px);overflow:auto;position:sticky;top:150px;box-shadow:var(--shadow)}
.vitem{display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:var(--radius-xs);cursor:pointer;border-bottom:1px dashed #f0e9dd;transition:background .15s ease,transform .12s ease}
.vitem:hover{background:#eaf6ee}
.vitem.sel{background:var(--green);color:#fff;border-radius:var(--radius-xs)}
 .vitem.sel .vcn{color:#d8ffe0}
.vitem.sel .tag.irr{background:rgba(255,255,255,.25);color:#fff}
.vinf{font-weight:700;font-size:16px}
.vcn{font-size:13px;color:var(--sub);flex:1}
.tag{font-size:11px;padding:3px 10px;border-radius:999px;white-space:nowrap;font-weight:600}
.tag.reg{background:#e6f4ea;color:#1e7a3c}
.tag.irr{background:var(--irr);color:#b8860b}
.tag.type{background:#eef2fa;color:var(--blue)}
.tag.refl{background:#f3e1e6;color:var(--red)}
.empty{padding:30px;text-align:center;color:var(--sub)}
#detail{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px;min-height:400px;box-shadow:var(--shadow)}
#vtitle{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px;padding-bottom:14px;border-bottom:2px solid var(--line)}
#vtitle .big{font-size:32px;font-weight:800;color:var(--green)}
#vtitle .cn{font-size:17px;color:var(--sub)}
.mood{margin-bottom:20px;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow-soft)}
.mhead{background:var(--mc);color:#fff;padding:11px 16px;font-size:16px}
.tensegrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;padding:14px}
.tense{background:#fdfbf7;border:1px solid #efe7da;border-radius:var(--radius-sm);padding:11px 14px}
.tname{display:flex;flex-direction:column;margin-bottom:7px;border-bottom:1px dashed #e5dccd;padding-bottom:6px}
.tname b{font-size:14.5px}
.tname i{font-size:12px;color:var(--sub);font-style:normal}
.trow{display:flex;gap:10px;padding:4px 0;font-size:16px}
.tper{width:100px;color:var(--sub);font-size:13px;padding-top:2px;flex-shrink:0}
.trow.yo .tform{color:var(--green);font-weight:700}
.impgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;padding:14px}
.impcell{background:#fdfbf7;border:1px solid #efe7da;border-radius:var(--radius-sm);padding:15px;text-align:center}
.impcell .ilab{display:block;font-size:12px;color:var(--sub);margin-bottom:5px}
.impcell b{font-size:20px;color:var(--blue)}
@media(max-width:920px){
  .layout{grid-template-columns:1fr}
  .vpanel{position:static;max-height:320px}
  #idx{margin:10px 12px 0}
  .layout{padding:12px}
  header h1{font-size:17px}
  .trow{font-size:17px}
  .tname b{font-size:15.5px}
  .tper{width:auto;min-width:92px;font-size:13px}
  .vinf{font-size:16.5px}
  .vcn{font-size:13.5px}
  #vtitle .big{font-size:28px}
}
"""


def main_html():
    _logo_path = os.path.join(HERE, "assets", "logo-weiyi.jpg")
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            logo_b64 = "data:image/jpeg;base64," + base64.b64encode(_f.read()).decode("ascii")
    else:
        logo_b64 = ""
    data_js = build_data_js()
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>意大利语动词变位表 · Coniugazione dei Verbi Italiani</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20100%20100'%3E%3Crect%20width='33'%20height='100'%20fill='%23009246'/%3E%3Crect%20x='33'%20width='34'%20height='100'%20fill='%23ffffff'/%3E%3Crect%20x='67'%20width='33'%20height='100'%20fill='%23CE2B37'/%3E%3Ctext%20x='50'%20y='68'%20font-size='40'%20text-anchor='middle'%20fill='%23009246'%20font-family='Arial'%20font-weight='bold'%3EIT%3C/text%3E%3C/svg%3E">
<style>__CSS__</style>
</head>
<body>
<header>
  <h1><span class="flag">🇮🇹</span> 意大利语动词变位表 <span class="flag">Coniugazione dei Verbi</span></h1>
  <div class="sub"><img class="logo" src="__LOGO__" alt="唯意意大利语"><span class="brand">唯意意大利语</span></div>
  <div class="toprow">
    <input id="search" type="search" placeholder="搜索动词或中文含义…">
    <span id="vcount"></span>
  </div>
</header>
<div id="idx"></div>
<div class="layout">
  <div class="vpanel" id="vlist"></div>
  <div class="rcol">
    <div id="vtitle"></div>
    <div id="detail"><div class="empty">选择左侧动词查看完整变位</div></div>
  </div>
</div>
<script>
__DATA__
__ENGINE__
</script>
<script>
__UI__
</script>
</body>
</html>"""
    html = (html.replace("__CSS__", CSS).replace("__DATA__", data_js)
               .replace("__ENGINE__", minjs(ENGINE_JS)).replace("__UI__", minjs(UI_JS))
               .replace("__LOGO__", logo_b64))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML 写入:", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    run_node_test()
    main_html()
