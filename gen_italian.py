# -*- coding: utf-8 -*-
"""
生成意大利语动词变位表网页（verbo-italiano.html，自包含单文件）
- 变位引擎：-are/-ere/-ire 三组规则 + -isc 插入 + 拼写(-care/-gare/-ciare/-giare/-sciare/-iare)
  + avere/essere 双助动词复合时态 + 完全不规则模型 + 前缀派生 + 半不规则(rem/pp/fut)覆盖
  + 自反动词独立呈现（mi/ti/si/ci/vi/si + essere 助动词 + 分词性数一致）
- 时态：陈述式(8) 虚拟式(4) 条件式(2) 命令式(1) = 15 组变位 + 6 非人称形式
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "verbo-italiano.html")

# ---------------------------------------------------------------------------
# 助动词（复合时态用）
# ---------------------------------------------------------------------------
AVERE = {
    "pres": ["ho", "hai", "ha", "abbiamo", "avete", "hanno"],
    "imperf": ["avevo", "avevi", "aveva", "avevamo", "avevate", "avevano"],
    "remoto": ["ebbi", "avesti", "ebbe", "avemmo", "aveste", "ebbero"],
    "fut": ["avrò", "avrai", "avrà", "avremo", "avrete", "avranno"],
    "cond": ["avrei", "avresti", "avrebbe", "avremmo", "avreste", "avrebbero"],
    "subj_pres": ["abbia", "abbia", "abbia", "abbiamo", "abbiate", "abbiano"],
    "subj_imperf": ["avessi", "avessi", "avesse", "avessimo", "aveste", "avessero"],
    "inf": "avere",
    "ger": "avendo",
    "pp": "avuto",
}
ESSERE = {
    "pres": ["sono", "sei", "è", "siamo", "siete", "sono"],
    "imperf": ["ero", "eri", "era", "eravamo", "eravate", "erano"],
    "remoto": ["fui", "fosti", "fu", "fummo", "foste", "furono"],
    "fut": ["sarò", "sarai", "sarà", "saremo", "sarete", "saranno"],
    "cond": ["sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero"],
    "subj_pres": ["sia", "sia", "sia", "siamo", "siate", "siano"],
    "subj_imperf": ["fossi", "fossi", "fosse", "fossimo", "foste", "fossero"],
    "inf": "essere",
    "ger": "essendo",
    "pp": "stato",
}

# ---------------------------------------------------------------------------
# 完全不规则模型（MODELS，可含全部字段；半不规则模型可只写 rem/pp/fut 字段，其余按规则派生）
# ---------------------------------------------------------------------------
MODELS = {
    # ==== 核心完全不规则 ====
    "essere": dict(pres=["sono", "sei", "è", "siamo", "siete", "sono"],
        imperf=["ero", "eri", "era", "eravamo", "eravate", "erano"],
        remoto=["fui", "fosti", "fu", "fummo", "foste", "furono"],
        fut=["sarò", "sarai", "sarà", "saremo", "sarete", "saranno"],
        cond=["sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero"],
        subj_pres=["sia", "sia", "sia", "siamo", "siate", "siano"],
        subj_imperf=["fossi", "fossi", "fosse", "fossimo", "foste", "fossero"],
        imp=["", "sii", "sia", "siamo", "siate", "siano"],
        ger="essendo", ppr="essente", pp="stato"),
    "avere": dict(pres=["ho", "hai", "ha", "abbiamo", "avete", "hanno"],
        imperf=["avevo", "avevi", "aveva", "avevamo", "avevate", "avevano"],
        remoto=["ebbi", "avesti", "ebbe", "avemmo", "aveste", "ebbero"],
        fut=["avrò", "avrai", "avrà", "avremo", "avrete", "avranno"],
        cond=["avrei", "avresti", "avrebbe", "avremmo", "avreste", "avrebbero"],
        subj_pres=["abbia", "abbia", "abbia", "abbiamo", "abbiate", "abbiano"],
        subj_imperf=["avessi", "avessi", "avesse", "avessimo", "aveste", "avessero"],
        imp=["", "abbi", "abbia", "abbiamo", "abbiate", "abbiano"],
        ger="avendo", ppr="avente", pp="avuto"),
    "andare": dict(pres=["vado", "vai", "va", "andiamo", "andate", "vanno"],
        imperf=["andavo", "andavi", "andava", "andavamo", "andavate", "andavano"],
        remoto=["andai", "andasti", "andò", "andammo", "andaste", "andarono"],
        fut=["andrò", "andrai", "andrà", "andremo", "andrete", "andranno"],
        cond=["andrei", "andresti", "andrebbe", "andremmo", "andreste", "andrebbero"],
        subj_pres=["vada", "vada", "vada", "andiamo", "andiate", "vadano"],
        subj_imperf=["andassi", "andassi", "andasse", "andassimo", "andaste", "andassero"],
        imp=["", "va'", "vada", "andiamo", "andate", "vadano"],
        ger="andando", ppr="andante", pp="andato"),
    "dare": dict(pres=["do", "dai", "dà", "diamo", "date", "danno"],
        imperf=["davo", "davi", "dava", "davamo", "davate", "davano"],
        remoto=["diedi", "desti", "diede", "demmo", "deste", "diedero"],
        fut=["darò", "darai", "darà", "daremo", "darete", "daranno"],
        cond=["darei", "daresti", "darebbe", "daremmo", "dareste", "darebbero"],
        subj_pres=["dia", "dia", "dia", "diamo", "diate", "diano"],
        subj_imperf=["dessi", "dessi", "desse", "dessimo", "deste", "dessero"],
        imp=["", "da'", "dia", "diamo", "date", "diano"],
        ger="dando", ppr="dante", pp="dato"),
    "stare": dict(pres=["sto", "stai", "sta", "stiamo", "state", "stanno"],
        imperf=["stavo", "stavi", "stava", "stavamo", "stavate", "stavano"],
        remoto=["stetti", "stesti", "stette", "stemmo", "steste", "stettero"],
        fut=["starò", "starai", "starà", "staremo", "starete", "staranno"],
        cond=["starei", "staresti", "starebbe", "staremmo", "stareste", "starebbero"],
        subj_pres=["stia", "stia", "stia", "stiamo", "stiate", "stiano"],
        subj_imperf=["stessi", "stessi", "stesse", "stessimo", "steste", "stessero"],
        imp=["", "sta'", "stia", "stiamo", "state", "stiano"],
        ger="stando", ppr="stante", pp="stato"),
    "fare": dict(pres=["faccio", "fai", "fa", "facciamo", "fate", "fanno"],
        imperf=["facevo", "facevi", "faceva", "facevamo", "facevate", "facevano"],
        remoto=["feci", "facesti", "fece", "facemmo", "faceste", "fecero"],
        fut=["farò", "farai", "farà", "faremo", "farete", "faranno"],
        cond=["farei", "faresti", "farebbe", "faremmo", "fareste", "farebbero"],
        subj_pres=["faccia", "faccia", "faccia", "facciamo", "facciate", "facciano"],
        subj_imperf=["facessi", "facessi", "facesse", "facessimo", "faceste", "facessero"],
        imp=["", "fa'", "faccia", "facciamo", "fate", "facciano"],
        ger="facendo", ppr="facente", pp="fatto"),
    "dire": dict(pres=["dico", "dici", "dice", "diciamo", "dite", "dicono"],
        imperf=["dicevo", "dicevi", "diceva", "dicevamo", "dicevate", "dicevano"],
        remoto=["dissi", "dicesti", "disse", "dicemmo", "diceste", "dissero"],
        fut=["dirò", "dirai", "dirà", "diremo", "direte", "diranno"],
        cond=["direi", "diresti", "direbbe", "diremmo", "direste", "direbbero"],
        subj_pres=["dica", "dica", "dica", "diciamo", "diciate", "dicano"],
        subj_imperf=["dicessi", "dicessi", "dicesse", "dicessimo", "diceste", "dicessero"],
        imp=["", "di'", "dica", "diciamo", "dite", "dicano"],
        ger="dicendo", ppr="dicente", pp="detto"),
    "bere": dict(pres=["bevo", "bevi", "beve", "beviamo", "bevete", "bevono"],
        imperf=["bevevo", "bevevi", "beveva", "bevevamo", "bevevate", "bevevano"],
        remoto=["bevvi", "bevesti", "bevve", "bevemmo", "beveste", "bevvero"],
        fut=["berrò", "berrai", "berrà", "berremo", "berrete", "berranno"],
        cond=["berrei", "berresti", "berrebbe", "berremmo", "berreste", "berrebbero"],
        subj_pres=["beva", "beva", "beva", "beviamo", "beviate", "bevano"],
        subj_imperf=["bevessi", "bevessi", "bevesse", "bevessimo", "beveste", "bevessero"],
        imp=["", "bevi", "beva", "beviamo", "bevete", "bevano"],
        ger="bevendo", ppr="bevente", pp="bevuto"),
    "sapere": dict(pres=["so", "sai", "sa", "sappiamo", "sapete", "sanno"],
        imperf=["sapevo", "sapevi", "sapeva", "sapevamo", "sapevate", "sapevano"],
        remoto=["seppi", "sapesti", "seppe", "sapemmo", "sapeste", "seppero"],
        fut=["saprò", "saprai", "saprà", "sapremo", "saprete", "sapranno"],
        cond=["saprei", "sapresti", "saprebbe", "sapremmo", "sapreste", "saprebbero"],
        subj_pres=["sappia", "sappia", "sappia", "sappiamo", "sappiate", "sappiano"],
        subj_imperf=["sapessi", "sapessi", "sapesse", "sapessimo", "sapeste", "sapessero"],
        imp=["", "sappi", "sappia", "sappiamo", "sappiate", "sappiano"],
        ger="sapendo", ppr="sapiente", pp="saputo"),
    "volere": dict(pres=["voglio", "vuoi", "vuole", "vogliamo", "volete", "vogliono"],
        imperf=["volevo", "volevi", "voleva", "volevamo", "volevate", "volevano"],
        remoto=["volli", "volesti", "volle", "volemmo", "voleste", "vollero"],
        fut=["vorrò", "vorrai", "vorrà", "vorremo", "vorrete", "vorranno"],
        cond=["vorrei", "vorresti", "vorrebbe", "vorremmo", "vorreste", "vorrebbero"],
        subj_pres=["voglia", "voglia", "voglia", "vogliamo", "vogliate", "vogliano"],
        subj_imperf=["volessi", "volessi", "volesse", "volessimo", "voleste", "volessero"],
        imp=["", "vogli", "voglia", "vogliamo", "vogliate", "vogliano"],
        ger="volendo", ppr="volente", pp="voluto"),
    "dovere": dict(pres=["devo", "devi", "deve", "dobbiamo", "dovete", "devono"],
        imperf=["dovevo", "dovevi", "doveva", "dovevamo", "dovevate", "dovevano"],
        remoto=["dovetti", "dovesti", "dovette", "dovemmo", "doveste", "dovettero"],
        fut=["dovrò", "dovrai", "dovrà", "dovremo", "dovrete", "dovranno"],
        cond=["dovrei", "dovresti", "dovrebbe", "dovremmo", "dovreste", "dovrebbero"],
        subj_pres=["deva", "deva", "deva", "dobbiamo", "dobbiate", "debbano"],
        subj_imperf=["dovessi", "dovessi", "dovesse", "dovessimo", "doveste", "dovessero"],
        imp=["", "—", "—", "—", "—", "—"],
        ger="dovendo", ppr="dovente", pp="dovuto"),
    "potere": dict(pres=["posso", "puoi", "può", "possiamo", "potete", "possono"],
        imperf=["potevo", "potevi", "poteva", "potevamo", "potevate", "potevano"],
        remoto=["potetti", "potesti", "potette", "potemmo", "poteste", "potettero"],
        fut=["potrò", "potrai", "potrà", "potremo", "potrete", "potranno"],
        cond=["potrei", "potresti", "potrebbe", "potremmo", "potreste", "potrebbero"],
        subj_pres=["possa", "possa", "possa", "possiamo", "possiate", "possano"],
        subj_imperf=["potessi", "potessi", "potesse", "potessimo", "poteste", "potessero"],
        imp=["", "—", "—", "—", "—", "—"],
        ger="potendo", ppr="potente", pp="potuto"),
    "venire": dict(pres=["vengo", "vieni", "viene", "veniamo", "venite", "vengono"],
        imperf=["venivo", "venivi", "veniva", "venivamo", "venivate", "venivano"],
        remoto=["venni", "venisti", "venne", "venimmo", "veniste", "vennero"],
        fut=["verrò", "verrai", "verrà", "verremo", "verrete", "verranno"],
        cond=["verrei", "verresti", "verrebbe", "verremmo", "verreste", "verrebbero"],
        subj_pres=["venga", "venga", "venga", "veniamo", "veniate", "vengano"],
        subj_imperf=["venissi", "venissi", "venisse", "venissimo", "veniste", "venissero"],
        imp=["", "vieni", "venga", "veniamo", "venite", "vengano"],
        ger="venendo", ppr="veniente", pp="venuto"),
    "tenere": dict(pres=["tengo", "tieni", "tiene", "teniamo", "tenete", "tengono"],
        imperf=["tenevo", "tenevi", "teneva", "tenevamo", "tenevate", "tenevano"],
        remoto=["tenni", "tenesti", "tenne", "tenemmo", "teneste", "tennero"],
        fut=["terrò", "terrai", "terrà", "terremo", "terrete", "terranno"],
        cond=["terrei", "terresti", "terrebbe", "terremmo", "terreste", "terrebbero"],
        subj_pres=["tenga", "tenga", "tenga", "teniamo", "teniate", "tengano"],
        subj_imperf=["tenessi", "tenessi", "tenesse", "tenessimo", "teneste", "tenessero"],
        imp=["", "tieni", "tenga", "teniamo", "tenete", "tengano"],
        ger="tenendo", ppr="tenente", pp="tenuto"),
    "uscire": dict(pres=["esco", "esci", "esce", "usciamo", "uscite", "escono"],
        imperf=["uscivo", "uscivi", "usciva", "uscivamo", "uscivate", "uscivano"],
        remoto=["uscii", "uscisti", "uscì", "uscimmo", "usciste", "uscirono"],
        fut=["uscirò", "uscirai", "uscirà", "usciremo", "uscirete", "usciranno"],
        cond=["uscirei", "usciresti", "uscirebbe", "usciremmo", "uscireste", "uscirebbero"],
        subj_pres=["esca", "esca", "esca", "usciamo", "usciate", "escano"],
        subj_imperf=["uscissi", "uscissi", "uscisse", "uscissimo", "usciste", "uscissero"],
        imp=["", "esci", "esca", "usciamo", "uscite", "escano"],
        ger="uscendo", ppr="uscente", pp="uscito"),
    "sedere": dict(pres=["siedo", "siedi", "siede", "sediamo", "sedete", "siedono"],
        imperf=["sedevo", "sedevi", "sedeva", "sedevamo", "sedevate", "sedevano"],
        remoto=["sedei", "sedesti", "sedé", "sedemmo", "sedeste", "sederono"],
        fut=["sederò", "sederai", "sederà", "sederemo", "sederete", "sederanno"],
        cond=["sederei", "sederesti", "sederebbe", "sederemmo", "sedereste", "sederebbero"],
        subj_pres=["sieda", "sieda", "sieda", "sediamo", "sediate", "siedano"],
        subj_imperf=["sedessi", "sedessi", "sedesse", "sedessimo", "sedeste", "sedessero"],
        imp=["", "siedi", "sieda", "sediamo", "sedete", "siedano"],
        ger="sedendo", ppr="sedente", pp="seduto"),
    "rimanere": dict(pres=["rimango", "rimani", "rimane", "rimaniamo", "rimanete", "rimangono"],
        imperf=["rimanevo", "rimanevi", "rimaneva", "rimanevamo", "rimanevate", "rimanevano"],
        remoto=["rimasi", "rimanesti", "rimase", "rimanemmo", "rimaneste", "rimasero"],
        fut=["rimarrò", "rimarrai", "rimarrà", "rimarremo", "rimarrete", "rimarranno"],
        cond=["rimarrei", "rimarresti", "rimarrebbe", "rimarremmo", "rimarreste", "rimarrebbero"],
        subj_pres=["rimanga", "rimanga", "rimanga", "rimaniamo", "rimaniate", "rimangano"],
        subj_imperf=["rimanessi", "rimanessi", "rimanesse", "rimanessimo", "rimaneste", "rimanessero"],
        imp=["", "rimani", "rimanga", "rimaniamo", "rimanete", "rimangano"],
        ger="rimanendo", ppr="rimanente", pp="rimasto"),
    "salire": dict(pres=["salgo", "sali", "sale", "saliamo", "salite", "salgono"],
        imperf=["salivo", "salivi", "saliva", "salivamo", "salivate", "salivano"],
        remoto=["salii", "salisti", "salì", "salimmo", "saliste", "salirono"],
        fut=["salirò", "salirai", "salirà", "saliremo", "salirete", "saliranno"],
        cond=["salirei", "saliresti", "salirebbe", "saliremmo", "salireste", "salirebbero"],
        subj_pres=["salga", "salga", "salga", "saliamo", "saliate", "salgano"],
        subj_imperf=["salissi", "salissi", "salisse", "salissimo", "saliste", "salissero"],
        imp=["", "sali", "salga", "saliamo", "salite", "salgano"],
        ger="salendo", ppr="saliente", pp="salito"),
    "morire": dict(pres=["muoio", "muori", "muore", "moriamo", "morite", "muoiono"],
        imperf=["morivo", "morivi", "moriva", "morivamo", "morivate", "morivano"],
        remoto=["morii", "moristi", "morì", "morimmo", "moriste", "morirono"],
        fut=["morirò", "morirai", "morirà", "moriremo", "morirete", "moriranno"],
        cond=["morirei", "moriresti", "morirebbe", "moriremmo", "morireste", "morirebbero"],
        subj_pres=["muoia", "muoia", "muoia", "moriamo", "moriate", "muoiano"],
        subj_imperf=["morissi", "morissi", "morisse", "morissimo", "moriste", "morissero"],
        imp=["", "muori", "muoia", "moriamo", "morite", "muoiano"],
        ger="morendo", ppr="morente", pp="morto"),
    "udire": dict(pres=["odo", "odi", "ode", "udiamo", "udite", "odono"],
        imperf=["udivo", "udivi", "udiva", "udivamo", "udivate", "udivano"],
        remoto=["udii", "udisti", "udì", "udimmo", "udiste", "udirono"],
        fut=["udrò", "udrai", "udrà", "udremo", "udrete", "udranno"],
        cond=["udrei", "udresti", "udrebbe", "udremmo", "udreste", "udrebbero"],
        subj_pres=["oda", "oda", "oda", "udiamo", "udiate", "odano"],
        subj_imperf=["udissi", "udissi", "udisse", "udissimo", "udiste", "udissero"],
        imp=["", "odi", "oda", "udiamo", "udite", "odano"],
        ger="udendo", ppr="udente", pp="udito"),
    "porre": dict(pres=["pongo", "poni", "pone", "poniamo", "ponete", "pongono"],
        imperf=["ponevo", "ponevi", "poneva", "ponevamo", "ponevate", "ponevano"],
        remoto=["posi", "ponesti", "pose", "ponemmo", "poneste", "posero"],
        fut=["porrò", "porrai", "porrà", "porremo", "porrete", "porranno"],
        cond=["porrei", "porresti", "porrebbe", "porremmo", "porreste", "porrebbero"],
        subj_pres=["ponga", "ponga", "ponga", "poniamo", "poniate", "pongano"],
        subj_imperf=["ponessi", "ponessi", "ponesse", "ponessimo", "poneste", "ponessero"],
        imp=["", "poni", "ponga", "poniamo", "ponete", "pongano"],
        ger="ponendo", ppr="ponente", pp="posto"),
    "trarre": dict(pres=["traggo", "trai", "trae", "traiamo", "traete", "traggono"],
        imperf=["traevo", "traevi", "traeva", "traevamo", "traevate", "traevano"],
        remoto=["trassi", "traesti", "trasse", "traemmo", "traeste", "trassero"],
        fut=["trarrò", "trarrai", "trarrà", "trarremo", "trarrete", "trarranno"],
        cond=["trarrei", "trarresti", "trarrebbe", "trarremmo", "trarreste", "trarrebbero"],
        subj_pres=["tragga", "tragga", "tragga", "traiamo", "traiate", "traggano"],
        subj_imperf=["traessi", "traessi", "traesse", "traessimo", "traeste", "traessero"],
        imp=["", "trai", "tragga", "traiamo", "traete", "traggano"],
        ger="traendo", ppr="traente", pp="tratto"),
    "condurre": dict(pres=["conduco", "conduci", "conduce", "conduciamo", "conducete", "conducono"],
        imperf=["conducevo", "conducevi", "conduceva", "conducevamo", "conducevate", "conducevano"],
        remoto=["condussi", "conducesti", "condusse", "conducemmo", "conduceste", "condussero"],
        fut=["condurrò", "condurrai", "condurrà", "condurremo", "condurrete", "condurranno"],
        cond=["condurrei", "condurresti", "condurrebbe", "condurremmo", "condurreste", "condurrebbero"],
        subj_pres=["conduca", "conduca", "conduca", "conduciamo", "conduciate", "conducano"],
        subj_imperf=["conducessi", "conducessi", "conducesse", "conducessimo", "conduceste", "conducessero"],
        imp=["", "conduci", "conduca", "conduciamo", "conducete", "conducano"],
        ger="conducendo", ppr="conducente", pp="condotto"),
    # ---- 家族 -durre（PX + duc 词干，规则同 condurre，仅前缀不同；introdurre 现在时特殊）----
    "produrre": dict(
        pres=['produco', 'produci', 'produce', 'produciamo', 'producete', 'producono'],
        imperf=['producevo', 'producevi', 'produceva', 'producevamo', 'producevate', 'producevano'],
        remoto=['produssi', 'producesti', 'produsse', 'producemmo', 'produceste', 'produssero'],
        fut=['produrrò', 'produrrai', 'produrrà', 'produrremo', 'produrrete', 'produrranno'],
        cond=['produrrei', 'produrresti', 'produrrebbe', 'produrremmo', 'produrreste', 'produrrebbero'],
        subj_pres=['produca', 'produca', 'produca', 'produciamo', 'produciate', 'producano'],
        subj_imperf=['producessi', 'producessi', 'producesse', 'producessimo', 'produceste', 'producessero'],
        imp=['', 'produci', 'produca', 'produciamo', 'producete', 'producano'],
        ger='producendo', ppr='producente', pp='prodotto'),
    "tradurre": dict(
        pres=['traduco', 'traduci', 'traduce', 'traduciamo', 'traducete', 'traducono'],
        imperf=['traducevo', 'traducevi', 'traduceva', 'traducevamo', 'traducevate', 'traducevano'],
        remoto=['tradussi', 'traducesti', 'tradusse', 'traducemmo', 'traduceste', 'tradussero'],
        fut=['tradurrò', 'tradurrai', 'tradurrà', 'tradurremo', 'tradurrete', 'tradurranno'],
        cond=['tradurrei', 'tradurresti', 'tradurrebbe', 'tradurremmo', 'tradurreste', 'tradurrebbero'],
        subj_pres=['traduca', 'traduca', 'traduca', 'traduciamo', 'traduciate', 'traducano'],
        subj_imperf=['traducessi', 'traducessi', 'traducesse', 'traducessimo', 'traduceste', 'traducessero'],
        imp=['', 'traduci', 'traduca', 'traduciamo', 'traducete', 'traducano'],
        ger='traducendo', ppr='traducente', pp='tradotto'),
    "ridurre": dict(
        pres=['riduco', 'riduci', 'riduce', 'riduciamo', 'riducete', 'riducono'],
        imperf=['riducevo', 'riducevi', 'riduceva', 'riducevamo', 'riducevate', 'riducevano'],
        remoto=['ridussi', 'riducesti', 'ridusse', 'riducemmo', 'riduceste', 'ridussero'],
        fut=['ridurrò', 'ridurrai', 'ridurrà', 'ridurremo', 'ridurrete', 'ridurranno'],
        cond=['ridurrei', 'ridurresti', 'ridurrebbe', 'ridurremmo', 'ridurreste', 'ridurrebbero'],
        subj_pres=['riduca', 'riduca', 'riduca', 'riduciamo', 'riduciate', 'riducano'],
        subj_imperf=['riducessi', 'riducessi', 'riducesse', 'riducessimo', 'riduceste', 'riducessero'],
        imp=['', 'riduci', 'riduca', 'riduciamo', 'riducete', 'riducano'],
        ger='riducendo', ppr='riducente', pp='ridotto'),
    "dedurre": dict(
        pres=['deduco', 'deduci', 'deduce', 'deduciamo', 'deducete', 'deducono'],
        imperf=['deducevo', 'deducevi', 'deduceva', 'deducevamo', 'deducevate', 'deducevano'],
        remoto=['dedussi', 'deducesti', 'dedusse', 'deducemmo', 'deduceste', 'dedussero'],
        fut=['dedurrò', 'dedurrai', 'dedurrà', 'dedurremo', 'dedurrete', 'dedurranno'],
        cond=['dedurrei', 'dedurresti', 'dedurrebbe', 'dedurremmo', 'dedurreste', 'dedurrebbero'],
        subj_pres=['deduca', 'deduca', 'deduca', 'deduciamo', 'deduciate', 'deducano'],
        subj_imperf=['deducessi', 'deducessi', 'deducesse', 'deducessimo', 'deduceste', 'deducessero'],
        imp=['', 'deduci', 'deduca', 'deduciamo', 'deducete', 'deducano'],
        ger='deducendo', ppr='deducente', pp='dedotto'),
    "sedurre": dict(
        pres=['seduco', 'seduci', 'seduce', 'seduciamo', 'seducete', 'seducono'],
        imperf=['seducevo', 'seducevi', 'seduceva', 'seducevamo', 'seducevate', 'seducevano'],
        remoto=['sedussi', 'seducesti', 'sedusse', 'seducemmo', 'seduceste', 'sedussero'],
        fut=['sedurrò', 'sedurrai', 'sedurrà', 'sedurremo', 'sedurrete', 'sedurranno'],
        cond=['sedurrei', 'sedurresti', 'sedurrebbe', 'sedurremmo', 'sedurreste', 'sedurrebbero'],
        subj_pres=['seduca', 'seduca', 'seduca', 'seduciamo', 'seduciate', 'seducano'],
        subj_imperf=['seducessi', 'seducessi', 'seducesse', 'seducessimo', 'seduceste', 'seducessero'],
        imp=['', 'seduci', 'seduca', 'seduciamo', 'seducete', 'seducano'],
        ger='seducendo', ppr='seducente', pp='sedotto'),
    "indurre": dict(
        pres=['induco', 'induci', 'induce', 'induciamo', 'inducete', 'inducono'],
        imperf=['inducevo', 'inducevi', 'induceva', 'inducevamo', 'inducevate', 'inducevano'],
        remoto=['indussi', 'inducesti', 'indusse', 'inducemmo', 'induceste', 'indussero'],
        fut=['indurrò', 'indurrai', 'indurrà', 'indurremo', 'indurrete', 'indurranno'],
        cond=['indurrei', 'indurresti', 'indurrebbe', 'indurremmo', 'indurreste', 'indurrebbero'],
        subj_pres=['induca', 'induca', 'induca', 'induciamo', 'induciate', 'inducano'],
        subj_imperf=['inducessi', 'inducessi', 'inducesse', 'inducessimo', 'induceste', 'inducessero'],
        imp=['', 'induci', 'induca', 'induciamo', 'inducete', 'inducano'],
        ger='inducendo', ppr='inducente', pp='indotto'),
    "riprodurre": dict(
        pres=['riproduco', 'riproduci', 'riproduce', 'riproduciamo', 'riproducete', 'riproducono'],
        imperf=['riproducevo', 'riproducevi', 'riproduceva', 'riproducevamo', 'riproducevate', 'riproducevano'],
        remoto=['riprodussi', 'riproducesti', 'riprodusse', 'riproducemmo', 'riproduceste', 'riprodussero'],
        fut=['riprodurrò', 'riprodurrai', 'riprodurrà', 'riprodurremo', 'riprodurrete', 'riprodurranno'],
        cond=['riprodurrei', 'riprodurresti', 'riprodurrebbe', 'riprodurremmo', 'riprodurreste', 'riprodurrebbero'],
        subj_pres=['riproduca', 'riproduca', 'riproduca', 'riproduciamo', 'riproduciate', 'riproducano'],
        subj_imperf=['riproducessi', 'riproducessi', 'riproducesse', 'riproducessimo', 'riproduceste', 'riproducessero'],
        imp=['', 'riproduci', 'riproduca', 'riproduciamo', 'riproducete', 'riproducano'],
        ger='riproducendo', ppr='riproducente', pp='riprodotto'),
    "ricondurre": dict(
        pres=['riconduco', 'riconduci', 'riconduce', 'riconduciamo', 'riconducete', 'riconducono'],
        imperf=['riconducevo', 'riconducevi', 'riconduceva', 'riconducevamo', 'riconducevate', 'riconducevano'],
        remoto=['ricondussi', 'riconducesti', 'ricondusse', 'riconducemmo', 'riconduceste', 'ricondussero'],
        fut=['ricondurrò', 'ricondurrai', 'ricondurrà', 'ricondurremo', 'ricondurrete', 'ricondurranno'],
        cond=['ricondurrei', 'ricondurresti', 'ricondurrebbe', 'ricondurremmo', 'ricondurreste', 'ricondurrebbero'],
        subj_pres=['riconduca', 'riconduca', 'riconduca', 'riconduciamo', 'riconduciate', 'riconducano'],
        subj_imperf=['riconducessi', 'riconducessi', 'riconducesse', 'riconducessimo', 'riconduceste', 'riconducessero'],
        imp=['', 'riconduci', 'riconduca', 'riconduciamo', 'riconducete', 'riconducano'],
        ger='riconducendo', ppr='riconducente', pp='ricondotto'),
    "addurre": dict(
        pres=['adduco', 'adduci', 'adduce', 'adduciamo', 'adducete', 'adducono'],
        imperf=['adducevo', 'adducevi', 'adduceva', 'adducevamo', 'adducevate', 'adducevano'],
        remoto=['addussi', 'adducesti', 'addusse', 'adducemmo', 'adduceste', 'addussero'],
        fut=['addurrò', 'addurrai', 'addurrà', 'addurremo', 'addurrete', 'addurranno'],
        cond=['addurrei', 'addurresti', 'addurrebbe', 'addurremmo', 'addurreste', 'addurrebbero'],
        subj_pres=['adduca', 'adduca', 'adduca', 'adduciamo', 'adduciate', 'adducano'],
        subj_imperf=['adducessi', 'adducessi', 'adducesse', 'adducessimo', 'adduceste', 'adducessero'],
        imp=['', 'adduci', 'adduca', 'adduciamo', 'adducete', 'adducano'],
        ger='adducendo', ppr='adducente', pp='addotto'),
    "introdurre": dict(
        pres=['introduco', 'introduci', 'introduce', 'introduciamo', 'introducete', 'introducono'],
        imperf=['introducevo', 'introducevi', 'introduceva', 'introducevamo', 'introducevate', 'introducevano'],
        remoto=['introdussi', 'introducesti', 'introdusse', 'introducemmo', 'introduceste', 'introdussero'],
        fut=['introdurrò', 'introdurrai', 'introdurrà', 'introdurremo', 'introdurrete', 'introdurranno'],
        cond=['introdurrei', 'introdurresti', 'introdurrebbe', 'introdurremmo', 'introdurreste', 'introdurrebbero'],
        subj_pres=['introduca', 'introduca', 'introduca', 'introduciamo', 'introduciate', 'introducano'],
        subj_imperf=['introducessi', 'introducessi', 'introducesse', 'introducessimo', 'introduceste', 'introducessero'],
        imp=['', 'introduci', 'introduca', 'introduciamo', 'introducete', 'introducano'],
        ger='introducendo', ppr='introducente', pp='introdotto'),

    "cogliere": dict(pres=["colgo", "cogli", "coglie", "cogliamo", "cogliete", "colgono"],
        imperf=["coglievo", "coglievi", "coglieva", "coglievamo", "coglievate", "coglievano"],
        remoto=["colsi", "cogliesti", "colse", "cogliemmo", "coglieste", "colsero"],
        fut=["coglierò", "coglierai", "coglierà", "coglieremo", "coglierete", "coglieranno"],
        cond=["coglierei", "coglieresti", "coglierebbe", "coglieremmo", "cogliereste", "coglierebbero"],
        subj_pres=["colga", "colga", "colga", "cogliamo", "cogliate", "colgano"],
        subj_imperf=["cogliessi", "cogliessi", "cogliesse", "cogliessimo", "coglieste", "cogliessero"],
        imp=["", "cogli", "colga", "cogliamo", "cogliete", "colgano"],
        ger="cogliendo", ppr="cogliente", pp="colto"),
    "scegliere": dict(pres=["scelgo", "scegli", "sceglie", "scegliamo", "scegliete", "scelgono"],
        imperf=["sceglievo", "sceglievi", "sceglieva", "sceglievamo", "sceglievate", "sceglievano"],
        remoto=["scelsi", "scegliesti", "scelse", "scegliemmo", "sceglieste", "scelsero"],
        fut=["sceglierò", "sceglierai", "sceglierà", "sceglieremo", "sceglierete", "sceglieranno"],
        cond=["sceglierei", "sceglieresti", "sceglierebbe", "sceglieremmo", "scegliereste", "sceglierebbero"],
        subj_pres=["scelga", "scelga", "scelga", "scegliamo", "scegliate", "scelgano"],
        subj_imperf=["scegliessi", "scegliessi", "scegliesse", "scegliessimo", "sceglieste", "scegliessero"],
        imp=["", "scegli", "scelga", "scegliamo", "scegliete", "scelgano"],
        ger="scegliendo", ppr="scegliente", pp="scelto"),
    "togliere": dict(pres=["tolgo", "togli", "toglie", "togliamo", "togliete", "tolgono"],
        imperf=["toglievo", "toglievi", "toglieva", "toglievamo", "toglievate", "toglievano"],
        remoto=["tolsi", "togliesti", "tolse", "togliemmo", "toglieste", "tolsero"],
        fut=["toglierò", "toglierai", "toglierà", "toglieremo", "toglierete", "toglieranno"],
        cond=["toglierei", "toglieresti", "toglierebbe", "toglieremmo", "togliereste", "toglierebbero"],
        subj_pres=["tolga", "tolga", "tolga", "togliamo", "togliate", "tolgano"],
        subj_imperf=["togliessi", "togliessi", "togliesse", "togliessimo", "toglieste", "togliessero"],
        imp=["", "togli", "tolga", "togliamo", "togliete", "tolgano"],
        ger="togliendo", ppr="togliente", pp="tolto"),
    "sciogliere": dict(pres=["sciolgo", "sciogli", "scioglie", "sciogliamo", "sciogliete", "sciolgono"],
        imperf=["scioglievo", "scioglievi", "scioglieva", "scioglievamo", "scioglievate", "scioglievano"],
        remoto=["sciolsi", "sciogliesti", "sciolse", "sciogliemmo", "scioglieste", "sciolsero"],
        fut=["scioglierò", "scioglierai", "scioglierà", "scioglieremo", "scioglierete", "scioglieranno"],
        cond=["scioglierei", "scioglieresti", "scioglierebbe", "scioglieremmo", "sciogliereste", "scioglierebbero"],
        subj_pres=["sciolga", "sciolga", "sciolga", "sciogliamo", "sciogliate", "sciolgano"],
        subj_imperf=["sciogliessi", "sciogliessi", "sciogliesse", "sciogliessimo", "scioglieste", "sciogliessero"],
        imp=["", "sciogli", "sciolga", "sciogliamo", "sciogliete", "sciolgano"],
        ger="sciogliendo", ppr="sciogliente", pp="sciolto"),
    "spegnere": dict(pres=["spengo", "spegni", "spegne", "spegniamo", "spegnete", "spengono"],
        imperf=["spegnevo", "spegnevi", "spegneva", "spegnevamo", "spegnevate", "spegnevano"],
        remoto=["spensi", "spegnesti", "spense", "spegnemmo", "spegneste", "spensero"],
        fut=["spegnerò", "spegnerai", "spegnerà", "spegneremo", "spegnerete", "spegneranno"],
        cond=["spegnerei", "spegneresti", "spegnerebbe", "spegneremmo", "spegnereste", "spegnerebbero"],
        subj_pres=["spenga", "spenga", "spenga", "spegniamo", "spegniate", "spengano"],
        subj_imperf=["spegnessi", "spegnessi", "spegnesse", "spegnessimo", "spegneste", "spegnessero"],
        imp=["", "spegni", "spenga", "spegniamo", "spegnete", "spengano"],
        ger="spegnendo", ppr="spegnente", pp="spento"),
    "valere": dict(pres=["valgo", "vali", "vale", "valiamo", "valete", "valgono"],
        imperf=["valevo", "valevi", "valeva", "valevamo", "valevate", "valevano"],
        remoto=["valsi", "valesti", "valse", "valemmo", "valeste", "valsero"],
        fut=["varrò", "varrai", "varrà", "varremo", "varrete", "varranno"],
        cond=["varrei", "varresti", "varrebbe", "varremmo", "varreste", "varrebbero"],
        subj_pres=["valga", "valga", "valga", "valiamo", "valiate", "valgano"],
        subj_imperf=["valessi", "valessi", "valesse", "valessimo", "valeste", "valessero"],
        imp=["", "vali", "valga", "valiamo", "valete", "valgano"],
        ger="valendo", ppr="valente", pp="valso"),
    "parere": dict(pres=["paio", "pari", "pare", "paiamo", "parete", "paiono"],
        imperf=["parevo", "parevi", "pareva", "parevamo", "parevate", "parevano"],
        remoto=["parvi", "paresti", "parve", "paremmo", "pareste", "parvero"],
        fut=["parrò", "parrai", "parrà", "parremo", "parrete", "parranno"],
        cond=["parrei", "parresti", "parrebbe", "parremmo", "parreste", "parrebbero"],
        subj_pres=["paia", "paia", "paia", "paiamo", "paiate", "paiano"],
        subj_imperf=["paressi", "paressi", "paresse", "paressimo", "pareste", "paressero"],
        imp=["", "—", "—", "—", "—", "—"],
        ger="parendo", ppr="parente", pp="parso"),
    "piacere": dict(pres=["piaccio", "piaci", "piace", "piacciamo", "piacete", "piacciono"],
        imperf=["piacevo", "piacevi", "piaceva", "piacevamo", "piacevate", "piacevano"],
        remoto=["piacqui", "piacesti", "piacque", "piacemmo", "piaceste", "piacquero"],
        fut=["piacerò", "piacerai", "piacerà", "piaceremo", "piacerete", "piaceranno"],
        cond=["piacerei", "piaceresti", "piacerebbe", "piaceremmo", "piacereste", "piacerebbero"],
        subj_pres=["piaccia", "piaccia", "piaccia", "piacciamo", "piacciate", "piacciano"],
        subj_imperf=["piacessi", "piacessi", "piacesse", "piacessimo", "piaceste", "piacessero"],
        imp=["", "piaci", "piaccia", "piacciamo", "piacete", "piacciano"],
        ger="piacendo", ppr="piacente", pp="piaciuto"),
    "tacere": dict(pres=["taccio", "taci", "tace", "tacciamo", "tacete", "tacciono"],
        imperf=["tacevo", "tacevi", "taceva", "tacevamo", "tacevate", "tacevano"],
        remoto=["tacqui", "tacesti", "tacque", "tacemmo", "taceste", "tacquero"],
        fut=["tacerò", "tacerai", "tacerà", "taceremo", "tacerete", "taceranno"],
        cond=["tacerei", "taceresti", "tacerebbe", "taceremmo", "tacereste", "tacerebbero"],
        subj_pres=["taccia", "taccia", "taccia", "tacciamo", "tacciate", "tacciano"],
        subj_imperf=["tacessi", "tacessi", "tacesse", "tacessimo", "taceste", "tacessero"],
        imp=["", "taci", "taccia", "tacciamo", "tacete", "tacciano"],
        ger="tacendo", ppr="tacente", pp="taciuto"),
    "giacere": dict(pres=["giaccio", "giaci", "giace", "giacciamo", "giacete", "giacciono"],
        imperf=["giacevo", "giacevi", "giaceva", "giacevamo", "giacevate", "giacevano"],
        remoto=["giacqui", "giacesti", "giacque", "giacemmo", "giaceste", "giacquero"],
        fut=["giacerò", "giacerai", "giacerà", "giaceremo", "giacerete", "giaceranno"],
        cond=["giacerei", "giaceresti", "giacerebbe", "giaceremmo", "giacereste", "giacerebbero"],
        subj_pres=["giaccia", "giaccia", "giaccia", "giacciamo", "giacciate", "giacciano"],
        subj_imperf=["giacessi", "giacessi", "giacesse", "giacessimo", "giaceste", "giacessero"],
        imp=["", "giaci", "giaccia", "giacciamo", "giacete", "giacciano"],
        ger="giacendo", ppr="giacente", pp="giaciuto"),
    "nuocere": dict(pres=["nuoccio", "nuoci", "nuoce", "nuociamo", "nuocete", "nuocciono"],
        imperf=["nuocevo", "nuocevi", "nuoceva", "nuocevamo", "nuocevate", "nuocevano"],
        remoto=["nocqui", "nocesti", "nocque", "nocemmo", "noceste", "nocquero"],
        fut=["nuocerò", "nuocerai", "nuocerà", "nuoceremo", "nuocerete", "nuoceranno"],
        cond=["nuocerei", "nuoceresti", "nuocerebbe", "nuoceremmo", "nuocereste", "nuocerebbero"],
        subj_pres=["nuoccia", "nuoccia", "nuoccia", "nuociamo", "nuociate", "nuocciano"],
        subj_imperf=["nuocessi", "nuocessi", "nuocesse", "nuocessimo", "nuoceste", "nuocessero"],
        imp=["", "nuoci", "nuoccia", "nuociamo", "nuocete", "nuocciano"],
        ger="nuocendo", ppr="nuocente", pp="nociuto"),
    "dolere": dict(pres=["dolgo", "duoli", "duole", "doliamo", "dolete", "dolgono"],
        imperf=["dolevo", "dolevi", "doleva", "dolevamo", "dolevate", "dolevano"],
        remoto=["dolsi", "dolesti", "dolse", "dolemmo", "doleste", "dolsero"],
        fut=["dorrò", "dorrai", "dorrà", "dorremo", "dorrete", "dorranno"],
        cond=["dorrei", "dorresti", "dorrebbe", "dorremmo", "dorreste", "dorrebbero"],
        subj_pres=["dolga", "dolga", "dolga", "doliamo", "doliate", "dolgano"],
        subj_imperf=["dolessi", "dolessi", "dolesse", "dolessimo", "doleste", "dolessero"],
        imp=["", "duoli", "dolga", "doliamo", "dolete", "dolgano"],
        ger="dolendo", ppr="dolente", pp="doluto"),
    "godere": dict(remoto=["godei", "godesti", "godé", "godemmo", "godeste", "goderono"],
        fut=["godrò", "godrai", "godrà", "godremo", "godrete", "godranno"],
        cond=["godrei", "godresti", "godrebbe", "godremmo", "godreste", "godrebbero"],
        pp="goduto"),
    # ==== 半不规则（规则现在时 + 不规则远过去时/分词/将来词干）====
    "vedere": dict(remoto=["vidi", "vedesti", "vide", "vedemmo", "vedeste", "videro"],
        fut=["vedrò", "vedrai", "vedrà", "vedremo", "vedrete", "vedranno"],
        cond=["vedrei", "vedresti", "vedrebbe", "vedremmo", "vedreste", "vedrebbero"],
        pp="veduto"),
    "chiedere": dict(remoto=["chiesi", "chiedesti", "chiese", "chiedemmo", "chiedeste", "chiesero"], pp="chiesto"),
    "prendere": dict(remoto=["presi", "prendesti", "prese", "prendemmo", "prendeste", "presero"], pp="preso"),
    "rispondere": dict(remoto=["risposi", "rispondesti", "rispose", "rispondemmo", "rispondeste", "risposero"], pp="risposto"),
    "scendere": dict(remoto=["scesi", "scendesti", "scese", "scendemmo", "scendeste", "scesero"], pp="sceso"),
    "spendere": dict(remoto=["spesi", "spendesti", "spese", "spendemmo", "spendeste", "spesero"], pp="speso"),
    "rendere": dict(remoto=["resi", "rendesti", "rese", "rendemmo", "rendeste", "resero"], pp="reso"),
    "accendere": dict(remoto=["accesi", "accendesti", "accese", "accendemmo", "accendeste", "accesero"], pp="acceso"),
    "leggere": dict(remoto=["lessi", "leggesti", "lesse", "leggemmo", "leggeste", "lessero"], pp="letto"),
    "scrivere": dict(remoto=["scrissi", "scrivesti", "scrisse", "scrivemmo", "scriveste", "scrissero"], pp="scritto"),
    "vincere": dict(remoto=["vinsi", "vincesti", "vinse", "vincemmo", "vinceste", "vinsero"], pp="vinto"),
    "correre": dict(remoto=["corsi", "corresti", "corse", "corremmo", "correste", "corsero"], pp="corso"),
    "perdere": dict(remoto=["persi", "perdesti", "perse", "perdemmo", "perdeste", "persero"], pp="perso"),
    "mettere": dict(remoto=["misi", "mettesti", "mise", "mettemmo", "metteste", "misero"], pp="messo"),
    "emettere": dict(remoto=["emisi", "emettesti", "emise", "emettemmo", "emetteste", "emisero"], pp="emesso"),
    "ardere": dict(remoto=["arsi", "ardesti", "arse", "ardemmo", "ardeste", "arsero"], pp="arso"),
    "vivere": dict(remoto=["vissi", "vivesti", "visse", "vivemmo", "viveste", "vissero"],
        fut=["vivrò", "vivrai", "vivrà", "vivremo", "vivrete", "vivranno"],
        cond=["vivrei", "vivresti", "vivrebbe", "vivremmo", "vivreste", "vivrebbero"],
        pp="vissuto"),
    "nascere": dict(remoto=["nacqui", "nascesti", "nacque", "nascemmo", "nasceste", "nacquero"], pp="nato"),
    "conoscere": dict(remoto=["conobbi", "conoscesti", "conobbe", "conoscemmo", "conosceste", "conobbero"], pp="conosciuto"),
    "crescere": dict(remoto=["crebbi", "crescesti", "crebbe", "crescemmo", "cresceste", "crebbero"], pp="cresciuto"),
    "decidere": dict(remoto=["decisi", "decidesti", "decise", "decidemmo", "decideste", "decisero"], pp="deciso"),
    "dividere": dict(remoto=["divisi", "dividesti", "divise", "dividemmo", "divideste", "divisero"], pp="diviso"),
    "ridere": dict(remoto=["risi", "ridesti", "rise", "ridemmo", "rideste", "risero"], pp="riso"),
    "rompere": dict(remoto=["ruppi", "rompesti", "ruppe", "rompemmo", "rompeste", "ruppero"], pp="rotto"),
    "chiudere": dict(remoto=["chiusi", "chiudesti", "chiuse", "chiudemmo", "chiudeste", "chiusero"], pp="chiuso"),
    "aprire": dict(remoto=["aprii", "apristi", "aprì", "aprimmo", "apriste", "aprirono"], pp="aperto"),
    "offrire": dict(remoto=["offrii", "offristi", "offrì", "offrimmo", "offriste", "offrirono"], pp="offerto"),
    "soffrire": dict(remoto=["soffrii", "soffristi", "soffrì", "soffrimmo", "soffriste", "soffrirono"], pp="sofferto"),
    "coprire": dict(remoto=["coprii", "copristi", "coprì", "coprimmo", "copriste", "coprirono"], pp="coperto"),
    "scoprire": dict(remoto=["scoprii", "scopristi", "scoprì", "scoprimmo", "scopriste", "scoprirono"], pp="scoperto"),
    "cuocere": dict(pres=["cuocio", "cuoci", "cuoce", "cuociamo", "cuocete", "cuociono"],
        subj_pres=["cuocia", "cuocia", "cuocia", "cuociamo", "cuociate", "cuociano"],
        remoto=["cossi", "cuocesti", "cosse", "cuocemmo", "cuoceste", "cossero"], pp="cotto"),
    "scuotere": dict(remoto=["scossi", "scuotesti", "scosse", "scuotemmo", "scuoteste", "scossero"], pp="scosso"),
    "discutere": dict(remoto=["discussi", "discutesti", "discusse", "discutemmo", "discuteste", "discussero"], pp="discusso"),
    "succedere": dict(remoto=["successi", "succedesti", "successe", "succedemmo", "succedeste", "successero"], pp="successo"),
    "accadere": dict(remoto=["accaddi", "accadesti", "accadde", "accademmo", "accadeste", "accaddero"], pp="accaduto"),
    "cadere": dict(remoto=["caddi", "cadesti", "cadde", "cademmo", "cadeste", "caddero"],
        fut=["cadrò", "cadrai", "cadrà", "cadremo", "cadrete", "cadranno"],
        cond=["cadrei", "cadresti", "cadrebbe", "cadremmo", "cadreste", "cadrebbero"],
        pp="caduto"),
    "esprimere": dict(remoto=["espressi", "esprimesti", "espresse", "esprimemmo", "esprimeste", "espressero"], pp="espresso"),
    "comprimere": dict(pres=["comprimo", "comprimi", "comprime", "comprimiamo", "comprimete", "comprimono"],
        subj_pres=["comprima", "comprima", "comprima", "comprimiamo", "comprimiate", "comprimano"],
        remoto=["compressi", "comprimesti", "compresse", "comprimemmo", "comprimeste", "compressero"], pp="compresso"),
    "reprimere": dict(pres=["reprimo", "reprimi", "reprime", "reprimiamo", "reprimete", "reprimono"],
        subj_pres=["reprima", "reprima", "reprima", "reprimiamo", "reprimiate", "reprimano"],
        remoto=["repressi", "reprimesti", "represse", "reprimemmo", "reprimeste", "repressero"], pp="represso"),
    "sopprimere": dict(pres=["sopprimo", "sopprimi", "sopprime", "sopprimiamo", "sopprimete", "sopprimono"],
        subj_pres=["sopprima", "sopprima", "sopprima", "sopprimiamo", "sopprimiate", "sopprimano"],
        remoto=["soppressi", "sopprimesti", "soppresse", "sopprimemmo", "sopprimeste", "soppressero"], pp="soppresso"),
    "concedere": dict(remoto=["concessi", "concedesti", "concesse", "concedemmo", "concedeste", "concessero"], pp="concesso"),
    "benedire": dict(pres=["benedico", "benedici", "benedice", "benediciamo", "benedite", "benedicono"],
        imperf=["benedicevo", "benedicevi", "benediceva", "benedicevamo", "benedicevate", "benedicevano"],
        remoto=["benedissi", "benedicesti", "benedisse", "benedicemmo", "benediceste", "benedissero"],
        fut=["benedirò", "benedirai", "benedirà", "benediremo", "benedirete", "benediranno"],
        cond=["benedirei", "benediresti", "benedirebbe", "benediremmo", "benedireste", "benedirebbero"],
        subj_pres=["benedica", "benedica", "benedica", "benediciamo", "benediciate", "benedicano"],
        subj_imperf=["benedicessi", "benedicessi", "benedicesse", "benedicessimo", "benediceste", "benedicessero"],
        imp=["", "benedici", "benedica", "benediciamo", "benedite", "benedicano"],
        ger="benedicendo", ppr="benedicente", pp="benedetto"),
    "maledire": dict(pres=["maledico", "maledici", "maledice", "malediciamo", "maledite", "maledicono"],
        imperf=["maledicevo", "maledicevi", "malediceva", "maledicevamo", "maledicevate", "maledicevano"],
        remoto=["maledissi", "maledicesti", "maledisse", "maledicemmo", "malediceste", "maledissero"],
        fut=["maledirò", "maledirai", "maledirà", "malediremo", "maledirete", "malediranno"],
        cond=["maledirei", "malediresti", "maledirebbe", "malediremmo", "maledireste", "maledirebbero"],
        subj_pres=["maledica", "maledica", "maledica", "malediciamo", "malediciate", "maledicano"],
        subj_imperf=["maledicessi", "maledicessi", "maledicesse", "maledicessimo", "malediceste", "maledicessero"],
        imp=["", "maledici", "maledica", "malediciamo", "maledite", "maledicano"],
        ger="maledicendo", ppr="maledicente", pp="maledetto"),
    "spingere": dict(remoto=["spinsi", "spingesti", "spinse", "spingemmo", "spingeste", "spinsero"], pp="spinto"),
    "stringere": dict(remoto=["strinsi", "stringesti", "strinse", "stringemmo", "stringeste", "strinsero"], pp="stretto"),
    "aggiungere": dict(remoto=["aggiunsi", "aggiungesti", "aggiunse", "aggiungemmo", "aggiungeste", "aggiunsero"], pp="aggiunto"),
    "giungere": dict(remoto=["giunsi", "giungesti", "giunse", "giungemmo", "giungeste", "giunsero"], pp="giunto"),
    "muovere": dict(remoto=["mossi", "muovesti", "mosse", "muovemmo", "muoveste", "mossero"], pp="mosso"),
    "piangere": dict(remoto=["piansi", "piangesti", "pianse", "piangemmo", "piangeste", "piansero"], pp="pianto"),
    "dipingere": dict(remoto=["dipinsi", "dipingesti", "dipinse", "dipingemmo", "dipingeste", "dipinsero"], pp="dipinto"),
    "fingere": dict(remoto=["finsi", "fingesti", "finse", "fingemmo", "fingeste", "finsero"], pp="finto"),
    "dipendere": dict(remoto=["dipesi", "dipendesti", "dipese", "dipendemmo", "dipendeste", "dipesero"], pp="dipeso"),
    "difendere": dict(remoto=["difesi", "difendesti", "difese", "difendemmo", "difendeste", "difesero"], pp="difeso"),
    "offendere": dict(remoto=["offesi", "offendesti", "offese", "offendemmo", "offendeste", "offesero"], pp="offeso"),
    "tendere": dict(remoto=["tesi", "tendesti", "tese", "tendemmo", "tendeste", "tesero"], pp="teso"),
    "fondere": dict(remoto=["fusi", "fondesti", "fuse", "fondemmo", "fondeste", "fusero"], pp="fuso"),
    "nascondere": dict(remoto=["nascosi", "nascondesti", "nascose", "nascondemmo", "nascondeste", "nascosero"], pp="nascosto"),
    "concludere": dict(remoto=["conclusi", "concludesti", "concluse", "concludemmo", "concludeste", "conclusero"], pp="concluso"),
    "escludere": dict(remoto=["esclusi", "escludesti", "escluse", "escludemmo", "escludeste", "esclusero"], pp="escluso"),
    "includere": dict(remoto=["inclusi", "includesti", "incluse", "includemmo", "includeste", "inclusero"], pp="incluso"),
    "correggere": dict(remoto=["corressi", "correggesti", "corresse", "correggemmo", "correggeste", "corressero"], pp="corretto"),
    "proteggere": dict(remoto=["protessi", "proteggesti", "protesse", "proteggemmo", "proteggeste", "protessero"], pp="protetto"),
    "eleggere": dict(remoto=["elessi", "eleggesti", "elesse", "eleggemmo", "eleggeste", "elessero"], pp="eletto"),
    "reggere": dict(remoto=["ressi", "reggesti", "resse", "reggemmo", "reggeste", "ressero"], pp="retto"),
    "distruggere": dict(remoto=["distrussi", "distruggesti", "distrusse", "distruggemmo", "distruggeste", "distrussero"], pp="distrutto"),
    "friggere": dict(remoto=["frissi", "friggesti", "frisse", "friggemmo", "friggeste", "frissero"], pp="fritto"),
    "porgere": dict(remoto=["porsi", "porgesti", "porse", "porgemmo", "porgeste", "porsero"], pp="porto"),
    "sorgere": dict(remoto=["sorsi", "sorgesti", "sorse", "sorgemmo", "sorgeste", "sorsero"], pp="sorto"),
    "assolvere": dict(remoto=["assolsi", "assolvesti", "assolse", "assolvemmo", "assolveste", "assolsero"], pp="assolto"),
    "risolvere": dict(remoto=["risolsi", "risolvesti", "risolse", "risolvemmo", "risolveste", "risolsero"], pp="risolto"),
    "dissolvere": dict(remoto=["dissolsi", "dissolvesti", "dissolse", "dissolvemmo", "dissolveste", "dissolsero"], pp="dissolto"),
    "emergere": dict(remoto=["emersi", "emergesti", "emerse", "emergemmo", "emergeste", "emersero"], pp="emerso"),
    "immergere": dict(remoto=["immersi", "immergesti", "immerse", "immergemmo", "immergeste", "immersero"], pp="immerso"),
    "sommergere": dict(remoto=["sommersi", "sommergesti", "sommerse", "sommergemmo", "sommergeste", "sommersero"], pp="sommerso"),
    "spargere": dict(remoto=["sparsi", "spargesti", "sparse", "spargemmo", "spargeste", "sparsero"], pp="sparso"),
    "congiungere": dict(remoto=["congiunsi", "congiungesti", "congiunse", "congiungemmo", "congiungeste", "congiunsero"], pp="congiunto"),
    "tingere": dict(remoto=["tinsi", "tingesti", "tinse", "tingemmo", "tingeste", "tinsero"], pp="tinto"),
    "attingere": dict(remoto=["attinsi", "attingesti", "attinse", "attingemmo", "attingeste", "attinsero"], pp="attinto"),
    "percuotere": dict(remoto=["percossi", "percuotesti", "percosse", "percuotemmo", "percuoteste", "percossero"], pp="percosso"),
    "riscuotere": dict(remoto=["riscossi", "riscuotesti", "riscosse", "riscuotemmo", "riscuoteste", "riscossero"], pp="riscosso"),
    "mordere": dict(remoto=["morsi", "mordesti", "morse", "mordemmo", "mordeste", "morsero"], pp="morso"),
    "prescindere": dict(remoto=["prescindei", "prescindesti", "prescindé", "prescindemmo", "prescindeste", "prescinderono"], pp="prescisso"),
    "apparire": dict(pres=["appaio", "appari", "appare", "appariamo", "apparite", "appaiono"],
        subj_pres=["appaia", "appaia", "appaia", "appariamo", "appariate", "appaiano"],
        remoto=["apparsi", "apparisti", "apparse", "apparimmo", "appariste", "apparsero"], pp="apparso"),
    "comparire": dict(pres=["compaio", "compari", "compare", "compariamo", "comparite", "compaiono"],
        subj_pres=["compaia", "compaia", "compaia", "compariamo", "compariate", "compaiano"],
        remoto=["comparsi", "comparisti", "comparse", "comparimmo", "compariste", "comparvero"], pp="comparso"),
    "scomparire": dict(pres=["scompaio", "scompari", "scompare", "scompariamo", "scomparite", "scompaiono"],
        subj_pres=["scompaia", "scompaia", "scompaia", "scompariamo", "scompariate", "scompaiano"],
        remoto=["scomparsi", "scomparisti", "scomparse", "scomparimmo", "scompariste", "scomparvero"], pp="scomparso"),
    # ---- 含 e→ie 词干交替 / 不规则 remoto + pp 的 -ere 动词 ----
    "pendere": dict(remoto=["pesi", "pendesti", "pese", "pendemmo", "pendeste", "pesero"], pp="peso"),
    "riflettere": dict(remoto=["riflettei", "riflettesti", "rifletté", "riflettemmo", "rifletteste", "rifletterono"], pp="riflesso"),
    "smettere": dict(remoto=["smisi", "smettesti", "smise", "smettemmo", "smetteste", "smisero"], pp="smesso"),
    "sorridere": dict(remoto=["sorrisi", "sorridesti", "sorrise", "sorridemmo", "sorrideste", "sorrisero"], pp="sorriso"),
    "evolvere": dict(remoto=["evolvei", "evolvesti", "evolvé", "evolvemmo", "evolveste", "evolverono"]),
    "possedere": dict(pres=["possiedo", "possiedi", "possiede", "possediamo", "possedete", "possiedono"],
        subj_pres=["possieda", "possieda", "possieda", "possediamo", "possediate", "possiedano"],
        imp=["", "possiedi", "possieda", "possediamo", "possedete", "possiedano"],
        remoto=["possedei", "possedesti", "possedé", "possedemmo", "possedeste", "possederono"], pp="posseduto"),
    # ---- -iare 混合型：1-3 单数双 i，但 3 复数去 i（odino/varino）----
    "odiare": dict(pres=["odio", "odii", "odia", "odiamo", "odiate", "odiano"],
        subj_pres=["odii", "odii", "odii", "odiamo", "odiate", "odino"],
        imp=["", "odia", "odii", "odiamo", "odiate", "odino"]),
    "variare": dict(pres=["vario", "varii", "varia", "variamo", "variate", "variano"],
        subj_pres=["varii", "varii", "varii", "variamo", "variate", "varino"],
        imp=["", "varia", "varii", "variamo", "variate", "varino"]),

}

# ---------------------------------------------------------------------------
# 动词数据
# ---------------------------------------------------------------------------
def V(i, c, aux="a", ch="", pp="", b="", x="", rem=None, fut=None, ppr="", bi=""):
    return {"i": i, "c": c, "aux": aux, "ch": ch, "pp": pp, "b": b, "x": x,
            "rem": rem or [], "fut": fut or "", "ppr": ppr, "bi": bi}

VERBS = []

def add(*vs):
    for v in vs:
        VERBS.append(v)

# --- 核心不规则模型 ---
add(V("essere", "是", aux="e", b="essere"),
    V("avere", "有", aux="a", b="avere"),
    V("andare", "去", aux="e", b="andare"),
    V("dare", "给", aux="a", b="dare"),
    V("stare", "停留/处于", aux="e", b="stare"),
    V("fare", "做", aux="a", b="fare"),
    V("dire", "说", aux="a", b="dire"),
    V("bere", "喝", aux="a", b="bere"),
    V("sapere", "知道", aux="a", b="sapere"),
    V("volere", "想要", aux="a", b="volere"),
    V("dovere", "必须", aux="a", b="dovere"),
    V("potere", "能够", aux="a", b="potere"),
    V("venire", "来", aux="e", b="venire"),
    V("tenere", "拿着/保持", aux="a", b="tenere"),
    V("uscire", "出去", aux="e", b="uscire"),
    V("sedere", "坐", aux="e", b="sedere"),
    V("rimanere", "留下/停留", aux="e", b="rimanere"),
    V("salire", "上去/上升", aux="e", b="salire"),
    V("morire", "死亡", aux="e", b="morire"),
    V("udire", "听见", aux="a", b="udire"),
    V("porre", "放置", aux="a", b="porre"),
    V("trarre", "拉/得出", aux="a", b="trarre"),
    V("condurre", "带领", aux="a", b="condurre"),
    V("cogliere", "采摘", aux="a", b="cogliere"),
    V("scegliere", "选择", aux="a", b="scegliere"),
    V("togliere", "拿走", aux="a", b="togliere"),
    V("sciogliere", "溶解", aux="a", b="sciogliere"),
    V("spegnere", "熄灭", aux="a", b="spegnere"),
    V("valere", "值得", aux="e", b="valere"),
    V("parere", "似乎", aux="e", b="parere"),
    V("piacere", "喜欢", aux="e", b="piacere"),
    V("tacere", "沉默", aux="a", b="tacere"),
    V("giacere", "躺", aux="a", b="giacere"),
    V("nuocere", "伤害", aux="a", b="nuocere"),
    V("dolere", "疼痛", aux="e", b="dolere"),
    V("godere", "享受", aux="a", b="godere"))

# --- 前缀派生（完全不规则家族）---
add(
    V("riuscire", "成功", aux="e", b="uscire"),
    V("convenire", "适合", aux="e", b="venire"),
    V("prevenire", "预防", aux="a", b="venire"),
    V("intervenire", "干预", aux="e", b="venire"),
    V("svenire", "昏倒", aux="e", b="venire"),
    V("divenire", "变成", aux="e", b="venire"),
    V("provenire", "来自", aux="e", b="venire"),
    V("avvenire", "发生", aux="e", b="venire"),
    V("rinvenire", "找到", aux="a", b="venire"),
    V("sovvenire", "援助", aux="a", b="venire"),
    V("contenere", "包含", aux="a", b="tenere"),
    V("mantenere", "保持", aux="a", b="tenere"),
    V("ottenere", "获得", aux="a", b="tenere", x="ot"),
    V("ritenere", "认为", aux="a", b="tenere"),
    V("sostenere", "支撑", aux="a", b="tenere"),
    V("appartenere", "属于", aux="e", b="tenere"),
    V("detenere", "拘留", aux="a", b="tenere"),
    V("intrattenere", "娱乐", aux="a", b="tenere"),
    V("trattenere", "留住", aux="a", b="tenere"),
    V("disfare", "拆毁", aux="a", b="fare"),
    V("rifare", "重做", aux="a", b="fare"),
    V("soddisfare", "满足", aux="a", b="fare"),
    V("contraddire", "反驳", aux="a", b="dire"),
    V("predire", "预言", aux="a", b="dire"),
    V("disdire", "取消", aux="a", b="dire"),
    V("ridire", "重说", aux="a", b="dire"),
    V("benedire", "祝福", aux="a", b="benedire"),
    V("maledire", "诅咒", aux="a", b="maledire"),
    V("comporre", "组成/创作", aux="a", b="porre"),
    V("proporre", "提议", aux="a", b="porre"),
    V("imporre", "强加", aux="a", b="porre"),
    V("esporre", "展出", aux="a", b="porre"),
    V("disporre", "安排", aux="a", b="porre"),
    V("opporre", "反对", aux="a", b="porre"),
    V("supporre", "假设", aux="a", b="porre"),
    V("deporre", "放下", aux="a", b="porre"),
    V("anteporre", "置于前", aux="a", b="porre"),
    V("contrapporre", "对立", aux="a", b="porre"),
    V("riporre", "放回", aux="a", b="porre"),
    V("attrarre", "吸引", aux="a", b="trarre"),
    V("distrarre", "使分心", aux="a", b="trarre"),
    V("contrarre", "收缩/感染", aux="a", b="trarre"),
    V("estrarre", "提取", aux="a", b="trarre"),
    V("ritrarre", "描绘", aux="a", b="trarre"),
    V("sottrarre", "减去", aux="a", b="trarre"),
    V("astrarre", "抽象", aux="a", b="trarre"),
    V("produrre", "生产", aux="a", b="produrre"),
    V("tradurre", "翻译", aux="a", b="tradurre"),
    V("ridurre", "减少", aux="a", b="ridurre"),
    V("introdurre", "引入", aux="a", b="introdurre"),
    V("dedurre", "推断", aux="a", b="dedurre"),
    V("sedurre", "引诱", aux="a", b="sedurre"),
    V("indurre", "诱导", aux="a", b="indurre"),
    V("riprodurre", "复制", aux="a", b="riprodurre"),
    V("ricondurre", "带回", aux="a", b="ricondurre"),
    V("addurre", "提出", aux="a", b="addurre"),
    V("rivedere", "再看", aux="a", b="vedere", x="ri"),
    V("prevedere", "预见", aux="a", b="vedere", x="pre"),
    V("provvedere", "供应", aux="a", b="vedere", x="prov"),
    V("intravedere", "瞥见", aux="a", b="vedere"),
    V("descrivere", "描述", aux="a", b="scrivere"),
    V("iscrivere", "登记", aux="a", b="scrivere"),
    V("sottoscrivere", "签署", aux="a", b="scrivere"),
    V("prescrivere", "开处方", aux="a", b="scrivere"),
    V("convincere", "说服", aux="a", b="vincere"),
    V("percorrere", "穿越", aux="a", b="correre"),
    V("concorrere", "竞争", aux="a", b="correre"),
    V("ricorrere", "求助于", aux="a", b="correre"),
    V("accorrere", "赶来", aux="e", b="correre"),
    V("soccorrere", "救助", aux="a", b="correre"),
    V("scorrere", "流动", aux="e", b="correre"),
    V("trascorrere", "度过", aux="a", b="correre"),
    V("decrescere", "减少", aux="e", b="crescere"),
    V("riconoscere", "认出", aux="a", b="conoscere"),
    V("disconoscere", "否认", aux="a", b="conoscere"),
    V("promettere", "承诺", aux="a", b="mettere"),
    V("ammettere", "承认", aux="a", b="mettere"),
    V("commettere", "犯(错)", aux="a", b="mettere"),
    V("permettere", "允许", aux="a", b="mettere"),
    V("scommettere", "打赌", aux="a", b="mettere"),
    V("trasmettere", "传送", aux="a", b="mettere"),
    V("omettere", "省略", aux="a", b="mettere"),
    V("sottomettere", "使屈服", aux="a", b="mettere"),
    V("rimettere", "放回", aux="a", b="mettere"),
    V("riprendere", "恢复/重新开始", aux="a", b="prendere"),
    V("comprendere", "理解/包含", aux="a", b="prendere"),
    V("sorprendere", "使惊讶", aux="a", b="prendere"),
    V("apprendere", "学习", aux="a", b="prendere"),
    V("discendere", "下降", aux="e", b="scendere"),
    V("ascendere", "上升", aux="e", b="scendere"),
    V("riaccendere", "重新点燃", aux="a", b="accendere"),
    V("sospendere", "暂停", aux="a", b="spendere"),
    V("riaprire", "重新打开", aux="a", b="aprire"),
    V("comprimere", "压缩", aux="a", b="comprimere"),
    V("reprimere", "镇压", aux="a", b="reprimere"),
    V("sopprimere", "废除", aux="a", b="sopprimere"),
    V("concludere", "结束", aux="a", b="concludere"),
    V("escludere", "排除", aux="a", b="escludere"),
    V("includere", "包括", aux="a", b="includere"),
)

# --- 半不规则（远过去时/分词不规则，其余规则）---
add(
    V("vedere", "看", aux="a", b="vedere"),
    V("chiedere", "询问", aux="a", b="chiedere"),
    V("prendere", "拿", aux="a", b="prendere"),
    V("rispondere", "回答", aux="a", b="rispondere"),
    V("scendere", "下来", aux="e", b="scendere"),
    V("spendere", "花费", aux="a", b="spendere"),
    V("rendere", "使变得/归还", aux="a", b="rendere"),
    V("accendere", "点燃", aux="a", b="accendere"),
    V("leggere", "读", aux="a", b="leggere"),
    V("scrivere", "写", aux="a", b="scrivere"),
    V("vincere", "赢", aux="a", b="vincere"),
    V("correre", "跑", aux="e", b="correre"),
    V("perdere", "失去", aux="a", b="perdere"),
    V("mettere", "放", aux="a", b="mettere"),
    V("vivere", "生活", aux="a", b="vivere"),
    V("nascere", "出生", aux="e", b="nascere"),
    V("conoscere", "认识", aux="a", b="conoscere"),
    V("crescere", "生长", aux="e", b="crescere"),
    V("decidere", "决定", aux="a", b="decidere"),
    V("dividere", "分割", aux="a", b="dividere"),
    V("ridere", "笑", aux="a", b="ridere"),
    V("rompere", "打破", aux="a", b="rompere"),
    V("chiudere", "关闭", aux="a", b="chiudere"),
    V("aprire", "打开", aux="a", b="aprire"),
    V("offrire", "提供", aux="a", b="offrire"),
    V("soffrire", "忍受", aux="a", b="soffrire"),
    V("coprire", "覆盖", aux="a", b="coprire"),
    V("scoprire", "发现", aux="a", b="scoprire"),
    V("cuocere", "烹饪", aux="a", b="cuocere"),
    V("scuotere", "摇动", aux="a", b="scuotere"),
    V("discutere", "讨论", aux="a", b="discutere"),
    V("succedere", "发生", aux="e", b="succedere"),
    V("accadere", "发生", aux="e", b="accadere"),
    V("cadere", "落下", aux="e", b="cadere"),
    V("esprimere", "表达", aux="a", b="esprimere"),
    V("spingere", "推", aux="a", b="spingere"),
    V("stringere", "握紧", aux="a", b="stringere"),
    V("aggiungere", "添加", aux="a", b="aggiungere"),
    V("giungere", "到达", aux="e", b="giungere"),
    V("muovere", "移动", aux="a", b="muovere"),
    V("piangere", "哭", aux="a", b="piangere"),
    V("dipingere", "画", aux="a", b="dipingere"),
    V("fingere", "假装", aux="a", b="fingere"),
    V("dipendere", "依赖", aux="e", b="dipendere"),
    V("difendere", "保卫", aux="a", b="difendere"),
    V("offendere", "冒犯", aux="a", b="offendere"),
    V("tendere", "展开/倾向", aux="a", b="tendere"),
    V("fondere", "熔化", aux="a", b="fondere"),
    V("nascondere", "隐藏", aux="a", b="nascondere"),
)

# --- 规则 -are ---
add(*[V(w[0], w[1], "a", w[2] if len(w) > 2 else "") for w in [
    ("parlare", "说话"), ("amare", "爱"), ("ammobiliare", "布置家具/陈设"), ("cantare", "唱歌"), ("ballare", "跳舞"), ("lavorare", "工作"),
    ("studiare", "学习"), ("comprare", "买"), ("camminare", "走路"), ("guardare", "看"), ("ascoltare", "听"),
    ("copiare", "复制"),
    ("chiamare", "叫/打电话"), ("domandare", "问"), ("aiutare", "帮助"), ("portare", "带"), ("usare", "使用"),
    ("aspettare", "等待"), ("trovare", "找到"), ("pagare", "付钱", "gare"), ("arrivare", "到达", "", "e"),
    ("nuotare", "游泳"), ("viaggiare", "旅行"), ("cucinare", "做饭"), ("insegnare", "教"), ("cenare", "吃晚饭"),
    ("visitare", "参观"), ("preparare", "准备"), ("festeggiare", "庆祝", "giare"), ("salvare", "拯救"), ("lavare", "洗"),
    ("mandare", "寄"), ("passare", "经过", "", "e"), ("saltare", "跳"), ("trattare", "处理"), ("accompagnare", "陪伴"),
    ("abbassare", "降低"), ("baciare", "吻", "ciare"), ("cancellare", "取消"), ("brillare", "发光"), ("cambiare", "改变"),
    ("chiacchierare", "聊天"), ("commentare", "评论"), ("creare", "创造"), ("coltivare", "耕种"), ("lasciare", "留下", "sciare"),
    ("disegnare", "画"), ("entrare", "进入", "", "e"), ("spiegare", "解释", "gare"), ("firmare", "签名"),
    ("galleggiare", "漂浮", "giare"), ("formare", "形成"), ("funzionare", "运转"), ("gridare", "喊叫"), ("abitare", "居住"),
    ("ignorare", "忽视"), ("tentare", "试图"), ("inventare", "发明"), ("limitare", "限制"), ("riempire", "填满", "isc"),
    ("lottare", "斗争"), ("segnare", "标记"), ("migliorare", "改善"), ("mescolare", "混合"), ("raccontare", "讲述"),
    ("notare", "注意"), ("occupare", "占据"), ("dimenticare", "忘记", "care"), ("operare", "操作"), ("fermare", "停"),
    ("pettinare", "梳"), ("bruciare", "燃烧", "ciare"), ("pregare", "祈祷", "gare"), ("ruotare", "旋转"), ("separare", "分开"),
    ("soffiare", "吹"), ("sudare", "出汗"), ("tardare", "延迟"), ("buttare", "扔"), ("trasportare", "运输"),
    ("abbracciare", "拥抱", "ciare"), ("minacciare", "威胁", "ciare"), ("analizzare", "分析"), ("atterrare", "着陆", "", "e"),
    ("avanzare", "前进"), ("attraversare", "穿越"), ("completare", "完成"), ("lanciare", "扔", "ciare"), ("organizzare", "组织"),
    ("realizzare", "实现"), ("rifiutare", "拒绝"), ("utilizzare", "利用"), ("valutare", "评价"), ("avvicinare", "靠近"),
    ("agitare", "摇动"), ("lodare", "赞美"), ("animare", "鼓励"), ("annotare", "记录"), ("sistemare", "整理"),
    ("spaventare", "惊吓"), ("avvisare", "通知"), ("bloccare", "封锁", "care"), ("ricamare", "刺绣"), ("cavalcare", "骑马", "care"),
    ("calmare", "使平静"), ("stancare", "使累", "care"), ("catturare", "捕捉"), ("confrontare", "比较"), ("continuare", "继续"),
    ("urtare", "碰撞"), ("provare", "尝试"), ("riposare", "休息"), ("esaminare", "检查"), ("scavare", "挖"),
    ("mancare", "缺少", "care", "e"), ("fabbricare", "制造", "care"), ("facilitare", "促进"), ("frenare", "刹车"),
    ("immaginare", "想象"), ("importare", "重要"), ("indicare", "指示", "care"), ("gonfiare", "充气"), ("informare", "通知"),
    ("iniziare", "开始"), ("insultare", "侮辱"), ("invitare", "邀请"), ("irritare", "激怒"), ("giurare", "发誓"),
    ("giustificare", "证明", "care"), ("localizzare", "定位"), ("alzare", "抬起"), ("guidare", "驾驶"), ("manipolare", "操纵"),
    ("marciare", "行进", "ciare"), ("menzionare", "提及"), ("bagnare", "弄湿"), ("disturbare", "打扰"),
    ("moltiplicare", "乘", "care"), ("mormorare", "低语"), ("navigare", "航行", "gare"), ("notificare", "通知", "care"),
    ("numerare", "编号"), ("ordinare", "命令"), ("originare", "产生"), ("oscillare", "摆动"),
    ("peccare", "犯罪", "care"), ("pelare", "剥皮"), ("calpestare", "踩"), ("stirare", "熨烫"), ("premiare", "奖励"),
    ("provocare", "挑衅", "care"), ("pubblicare", "出版", "care"), ("purificare", "净化", "care"), ("raschiare", "刮"),
    ("graffiare", "划"), ("rimbalzare", "反弹"), ("ritagliare", "裁剪"), ("riformare", "改革"), ("contrattare", "讨价还价"),
    ("registrare", "登记"), ("regolare", "调节"), ("collegare", "联系", "gare"), ("ripassare", "复习"), ("scivolare", "滑倒", "", "e"),
    ("rispettare", "尊重"), ("sfidare", "挑战"), ("ritirare", "撤退"), ("rivelare", "揭示"), ("circondare", "环绕"),
    ("assaporare", "品尝"), ("salare", "加盐"), ("asciugare", "弄干", "gare"), ("segnalare", "指出"), ("fischiare", "吹口哨"),
    ("simboleggiare", "象征", "giare"), ("sottolineare", "下划线"), ("sospirare", "叹气"), ("tastare", "试探"), ("tatuare", "纹身"),
    ("esitare", "犹豫"), ("scontrare", "碰撞"), ("totalizzare", "总计"), ("ostacolare", "阻碍"), ("trasformare", "转变"),
    ("transitare", "通行", "", "e"), ("troncare", "截断", "care"), ("rovesciare", "推倒", "ciare"), ("unificare", "统一", "care"),
    ("svuotare", "清空"), ("convalidare", "验证"), ("vegliare", "守护"), ("vetare", "否决"),
    ("sorvegliare", "监视"), ("votare", "投票"), ("salpare", "起航", "", "e"), ("affondare", "沉没", "", "e"), ("ronzare", "嗡嗡响"),
    ("sognare", "做梦"), ("incontrare", "遇见"), ("mostrare", "展示"), ("ricordare", "记得"), ("tornare", "回来", "", "e"),
    ("restare", "留下", "", "e"), ("pensare", "思考"), ("mangiare", "吃", "giare"), ("giocare", "玩", "care"),
    ("cominciare", "开始", "ciare"), ("telefonare", "打电话"), ("suonare", "演奏"), ("volare", "飞"), ("svegliare", "唤醒"),
    ("cercare", "寻找", "care"), ("desiderare", "渴望"), ("salutare", "问候"), ("ringraziare", "感谢"), ("sposare", "结婚"),
    ("abbandonare", "放弃"), ("accettare", "接受"), ("adattare", "适应"), ("aggiustare", "修理"), ("affittare", "租"),
    ("allungare", "延长", "gare"), ("ammirare", "钦佩"), ("annunciare", "宣布", "ciare"), ("appoggiare", "支持", "giare"),
    ("approfittare", "利用"), ("arrabbiare", "生气"), ("assaggiare", "品尝", "giare"), ("attaccare", "攻击/粘贴", "care"),
    ("aumentare", "增加", "", "e"), ("avvicinare", "靠近"), ("bastare", "足够", "", "e"), ("causare", "导致"),
    ("celebrare", "庆祝"), ("certificare", "证明", "care"), ("collezionare", "收集"), ("comunicare", "沟通", "care"),
    ("consegnare", "交付"), ("contare", "数"), ("costare", "花费", "", "e"), ("curare", "照顾"), ("decorare", "装饰"),
    ("dedicare", "奉献", "care"), ("denunciare", "举报", "ciare"), ("descrivere", "描述"), ("disturbare", "打扰"),
    ("educare", "教育", "care"), ("eliminare", "消除"), ("emigrare", "移民", "", "e"), ("esagerare", "夸张"),
    ("evitare", "避免"), ("fiatare", "喘气"), ("fidare", "信任"), ("fotografare", "拍照"), ("frequentare", "经常去"),
    ("guidare", "驾驶"), ("identificare", "识别", "care"), ("illustrare", "说明"), ("imitare", "模仿"), ("implicare", "涉及", "care"),
    ("incollare", "粘贴"), ("indovinare", "猜中"), ("influenzare", "影响"), ("ingannare", "欺骗"), ("inquinare", "污染"),
    ("insegnare", "教"), ("intrecciare", "编织", "ciare"), ("inventare", "发明"), ("litigare", "争吵", "gare"), ("migliorare", "改善"),
    ("mostrare", "展示"), ("nominare", "任命"), ("osservare", "观察"), ("partecipare", "参加"), ("penetrare", "渗透", "", "e"),
    ("perdonare", "原谅"), ("pesare", "称重"), ("pianificare", "规划", "care"), ("picchiare", "打"), ("pilotare", "驾驶飞机"),
    ("pranzare", "吃午饭"), ("praticare", "练习", "care"), ("prenotare", "预订"), ("presentare", "介绍"),
    ("progettare", "设计"), ("promettere", "承诺"), ("pronunciare", "发音", "ciare"), ("protestare", "抗议"), ("pubblicare", "出版", "care"),
    ("raccomandare", "推荐"), ("raffreddare", "冷却"), ("ragionare", "推理"), ("respirare", "呼吸"),
    ("riparare", "修理"), ("rischiare", "冒险"), ("risparmiare", "节省"), ("ritornare", "返回", "", "e"), ("rubare", "偷"),
    ("sbarcare", "下船", "care", "", "e"), ("sbagliare", "弄错"), ("scambiare", "交换"), ("scappare", "逃跑", "", "e"),
    ("scherzare", "开玩笑"), ("scopare", "扫"), ("scusare", "原谅"), ("sembrare", "似乎", "", "e"),
    ("significare", "意味着", "care"), ("sperare", "希望"), ("spiegare", "解释", "gare"), ("sposare", "结婚"), ("squillare", "响铃"),
    ("stampare", "印刷"), ("superare", "超过"), ("svegliare", "唤醒"), ("sviluppare", "发展"), ("tagliare", "切"),
    ("tirare", "拉"), ("toccare", "碰", "care"), ("trapiantare", "移植"), ("trascinare", "拖"), ("trascurare", "忽视"),
    ("truccare", "化妆", "care"), ("urlare", "喊"), ("usare", "使用"), ("valicare", "翻越", "care"),
    ("versare", "倒"), ("viaggiare", "旅行"), ("visitare", "参观"), ("viziare", "宠坏"), ("volare", "飞"),
    ("affermare", "断言/声明"), ("agevolare", "使便利/促进"), ("optare", "选择/抉择"), ("perfezionare", "使完善/改进"), ("scongiurare", "恳求/祈祷"),
    ("inviare", "发送", "iare_t"), ("avviare", "启动", "iare_t"), ("rinviare", "推迟", "iare_t"), ("spiare", "监视", "iare_t"),
    # --- 稀有字母补充（H/J/K/Q/W/X/Y）---
    ("quadrare", "使成方形/使对齐"), ("qualificare", "使合格/具有资格", "care"),
    ("quantificare", "量化", "care"), ("querelare", "控告/起诉"), ("quietare", "使安静/平息"),
    ("quotare", "报价/作价"), ("quadruplicare", "使成四倍", "care"), ("questuare", "乞讨/行乞"),
    ("quagliare", "使凝结/（云）消散"), ("quarantennare", "隔离/检疫"),
    ("hostare", "托管/作为主机"), ("hackerare", "黑客攻击"),
    ("jazzare", "演奏爵士乐"),
    ("kilometrare", "按公里计量"), ("kickare", "踢（球）"),
    ("weekendare", "度周末"),
    ("xilografare", "木刻/木版印刷"), ("xerocopiare", "复印"), ("xerografare", "静电复印"),
    ("yogare", "练瑜伽"),
]])
# --- -iare 混合型（1-3 单数双 i，3 复数去 i）需显式模型 ---
add(V("odiare", "憎恨", aux="a", b="odiare"),
    V("variare", "变化", aux="a", b="variare"))

# --- 规则 -ere ---
add(*[V(w[0], w[1], w[3] if len(w) > 3 else "a", w[2] if len(w) > 2 else "", b=w[4] if len(w) > 4 else "") for w in [
    ("temere", "害怕"), ("credere", "相信"), ("ricevere", "收到"), ("vendere", "卖"), ("battere", "击打"),
    ("ripetere", "重复"), ("tessere", "编织"), ("premere", "按压"), ("cedere", "让步"), ("splendere", "发光"),
    ("pendere", "悬挂", "", "a", "pendere"), ("assistere", "出席"), ("esistere", "存在", "", "e"), ("consistere", "在于", "", "e"),
    ("insistere", "坚持"), ("resistere", "抵抗"), ("sorridere", "微笑", "", "a", "sorridere"), ("mietere", "收割"), ("concedere", "授予", "", "a", "concedere"),
    ("procedere", "进行", "", "e"), ("eccedere", "超过"), ("possedere", "拥有", "", "a", "possedere"), ("ardere", "燃烧", "", "a", "ardere"), ("riflettere", "反射/思考", "", "a", "riflettere"),
    ("smettere", "停止", "", "a", "smettere"), ("emettere", "发出", "", "a", "emettere"), ("soccombere", "屈服"), ("prescindere", "撇开", "", "a", "prescindere"), ("evolvere", "进化", "", "a", "evolvere"),
    ("assistere", "协助"), ("consistere", "在于"), ("desistere", "放弃"), ("esistere", "存在"), ("insistere", "坚持"),
    ("persistere", "坚持", "", "e"), ("resistere", "抵抗"), ("sussistere", "存在", "", "e"), ("bere", "喝"),
]])

# --- 规则 -ire（无 -isc）---
add(*[V(w[0], w[1], "a") for w in [
    ("dormire", "睡觉"), ("partire", "出发", "", "e"), ("sentire", "感觉/听"), ("servire", "服务"), ("seguire", "跟随"),
    ("fuggire", "逃跑", "", "e"), ("vestire", "穿衣"), ("bollire", "煮沸"), ("divertire", "使娱乐"), ("avvertire", "警告"),
    ("consentire", "同意"), ("dissentire", "不同意"), ("assentire", "赞同"), ("presentire", "预感"), ("risentire", "怨恨"),
    ("convertire", "转换"), ("invertire", "颠倒"), ("pervertire", "败坏"), ("sovvertire", "颠覆"), ("inseguire", "追赶"),
    ("conseguire", "获得"), ("perseguire", "追求"), ("proseguire", "继续"), ("mentire", "撒谎"), ("pentire", "使后悔"),
    ("nutrire", "喂养"), ("avvertire", "告知"), ("divertire", "娱乐"), ("seguire", "跟随"),
]])

# --- 规则 -ire（-isc 插入）---
add(*[V(w[0], w[1], "a", "isc") for w in [
    ("finire", "结束"), ("capire", "理解"), ("preferire", "更喜欢"), ("pulire", "清洁"), ("spedire", "寄送"),
    ("costruire", "建造"), ("fornire", "提供"), ("garantire", "保证"), ("colpire", "击中"), ("unire", "联合"),
    ("riunire", "聚集"), ("punire", "惩罚"), ("sparire", "消失", "", "e"), ("arricchire", "使富裕"), ("impoverire", "使贫穷"),
    ("ingrandire", "扩大"), ("diminuire", "减少"), ("contribuire", "贡献"), ("distribuire", "分配"), ("attribuire", "归因"),
    ("eseguire", "执行"), ("stupire", "使惊讶"), ("fiorire", "开花", "", "e"), ("trasferire", "转移"), ("riferire", "报告"),
    ("suggerire", "建议"), ("inserire", "插入"), ("ferire", "伤害"), ("assorbire", "吸收"), ("favorire", "有利于"),
    ("approfondire", "深化"), ("inghiottire", "吞"), ("istruire", "教导"), ("costituire", "构成"), ("sostituire", "替代"),
    ("restituire", "归还"), ("proibire", "禁止"), ("reagire", "反应"), ("guarire", "痊愈", "", "e"), ("impedire", "阻止"),
    ("patire", "遭受"), ("gradire", "乐意"), ("marcire", "腐烂"), ("abbellire", "美化"), ("ingiallire", "变黄"),
    ("imbianchire", "变白"), ("arrossire", "脸红"), ("impallidire", "变苍白"), ("obbedire", "服从"), ("disubbidire", "违抗"),
    ("zittire", "使安静"), ("fallire", "失败"), ("custodire", "看守"), ("ammonire", "警告"), ("condire", "调味"),
    ("tossire", "咳嗽"), ("smaltire", "消化"), ("seppellire", "埋葬"), ("appassire", "枯萎", "", "e"), ("inibire", "抑制"),
    ("concepire", "构思"), ("rapire", "绑架"), ("gioire", "欢欣"), ("muggire", "哞叫"), ("rugire", "咆哮"),
    ("chiarire", "澄清"), ("stabilire", "建立"), ("definire", "定义"), ("gestire", "管理"), ("sparire", "消失"),
    ("unire", "联合"), ("arricchire", "致富"), ("approfondire", "深化"), ("preferire", "偏好"), ("finire", "完成"),
    ("obbedire", "服从"), ("esibire", "展示"), ("impazzire", "发疯", "", "e"), ("rinfrescire", "使清新"), ("sminuire", "贬低"),
    ("trasferire", "转移"), ("diminuire", "减少"), ("spedire", "寄"), ("colpire", "击中"), ("fornire", "提供"),
]])

# --- apparire 家族（不完全规则，模型已定义）---
add(V("apparire", "出现", aux="e", b="apparire"),
    V("comparire", "出现/相比", aux="e", b="comparire"),
    V("scomparire", "消失", aux="e", b="scomparire"))

# ---------------------------------------------------------------------------
# 去重（保留第一个）
# ---------------------------------------------------------------------------
seen = set()
FINAL = []
for v in VERBS:
    if v["i"] in seen:
        continue
    seen.add(v["i"])
    FINAL.append(v)
VERBS = FINAL

# 现在分词/过去分词 个别修正（引擎默认规则生成的错误形）
_PPR_PP_FIX = {
    "sentire": dict(ppr="senziente"),
    "riempire": dict(ppr="riempiente"),   # the-conjugation.com 对 -isc 现分多为 -ente，但 riempire 标 -iente，跟随参考站
    "assentire": dict(ppr="assenziente"),
    "consentire": dict(ppr="consenziente"),
    "dissentire": dict(ppr="dissenziente"),
    "presentire": dict(ppr="presenziente"),
    "sapere": dict(ppr="-"),           # sapere 无现在分词（参考站标 -）
    "assistere": dict(pp="assistito"),
    "esistere": dict(pp="esistito"),
    "insistere": dict(pp="insistito"),
    "consistere": dict(pp="consistito"),
    "desistere": dict(pp="desistito"),
    "persistere": dict(pp="persistito"),
    "resistere": dict(pp="resistito"),
    "sussistere": dict(pp="sussistito"),
    "evolvere": dict(pp="evoluto"),
    "godere": dict(ppr="gaudente"),
    "intravedere": dict(pp="veduto"),   # 前缀 intra 由 x 自动计算，pp 这里只填词根 veduto
    "pervertire": dict(ppr="perverziente"),
    "sovvertire": dict(ppr="sovverziente"),
    "splendere": dict(pp="-"),         # splendere 分词罕见（参考站标 -）
    "dovere": dict(ppr="-"),           # dovere 无现在分词
}
for _v in VERBS:
    if _v["i"] in _PPR_PP_FIX:
        _v.update(_PPR_PP_FIX[_v["i"]])

# 前缀自动计算（base 派生）
for v in VERBS:
    if v["b"] and not v["x"]:
        base = v["b"]
        pre = v["i"][:-len(base)]
        if pre + base != v["i"]:
            pre = v["i"][:-len(base)]
        v["x"] = pre

# ---------------------------------------------------------------------------
# 自反动词（独立呈现：mi/ti/si/ci/vi/si + essere + 分词性数一致）
# ---------------------------------------------------------------------------
def lookup(base):
    for v in VERBS:
        if v["i"] == base:
            return v
    return None

REFL_BASES = [
    ("lavare", "洗(自己)"), ("alzare", "起床"), ("vestire", "穿衣服"), ("svegliare", "醒来"),
    ("chiamare", "名叫"), ("mettere", "穿上"), ("trovare", "感到/位于"), ("sentire", "感觉"),
    ("divertire", "玩得开心"), ("sedere", "坐下"), ("riposare", "休息"), ("fermare", "停下"),
    ("muovere", "移动/动身"), ("preparare", "准备(自己)"), ("pettinare", "梳头"), ("radere", "刮胡子"),
    ("nascondere", "躲藏"), ("ricordare", "记得"), ("dimenticare", "忘记"), ("sbagliare", "弄错"),
    ("arrabbiare", "生气"), ("annoiare", "厌烦"), ("abituare", "习惯"), ("laureare", "毕业"),
    ("sposare", "结婚"), ("lamentare", "抱怨"), ("informare", "了解"), ("iscrivere", "报名"),
    ("rilassare", "放松"), ("sforzare", "努力"), ("impegnare", "致力于"), ("innamorare", "爱上"),
    ("accorgere", "察觉"), ("pentire", "后悔"), ("comportare", "表现"), ("sbrigare", "赶紧"),
    ("preoccupare", "担心"), ("vergognare", "羞愧"), ("addormentare", "入睡"), ("ammalare", "生病"),
    ("sbagliare", "犯错"), ("affrettare", "赶快"), ("ritirare", "撤退"), ("allenare", "训练"),
    ("diffidare", "提防"), ("accontentare", "满足于"), ("dedicare", "致力于", "care"), ("ferire", "伤到自己"),
    ("fidare", "信任"),
    ("sedere", "就座"), ("muovere", "起身"), ("svegliare", "醒"), ("alzare", "起身"), ("vestire", "穿衣"),
]

reflexive_entries = []
for item in REFL_BASES:
    base, cn = item[0], item[1]
    ch_override = item[2] if len(item) > 2 else None
    basev = lookup(base)
    if basev is None:
        continue
    refl_i = base[:-1] + "si"   # lavare -> lavarsi (去掉末尾 e 换 si；引擎 slice(0,-2) 期望 lava+si)
    if refl_i in seen:
        continue
    refl_v = V(refl_i, cn, aux="e",
               ch=(ch_override if ch_override is not None else basev["ch"]),
               pp=basev["pp"], b=basev["b"],
               x=basev["x"], rem=list(basev["rem"]), fut=basev["fut"], ppr=basev["ppr"],
               bi=base)
    reflexive_entries.append(refl_v)
    seen.add(refl_i)

VERBS += reflexive_entries

# 按原形排序
VERBS.sort(key=lambda v: v["i"])

print("Total verbos únicos:", len(VERBS))

# ---------------------------------------------------------------------------
# 变位引擎 (JS)
# ---------------------------------------------------------------------------
ENGINE_JS = r"""
// ===== Motore di coniugazione italiano =====
var PRON=["io","tu","lui/lei","noi","voi","loro"];
var REFL=["mi","ti","si","ci","vi","si"];
var VOWELS="aeiouàèéìòóù";
var END={
 'are':{pres:['o','i','a','iamo','ate','ano'],imperf:['avo','avi','ava','avamo','avate','avano'],remoto:['ai','asti','ò','ammo','aste','arono'],subj_pres:['i','i','i','iamo','iate','ino'],subj_imperf:['assi','assi','asse','assimo','aste','assero']},
 'ere':{pres:['o','i','e','iamo','ete','ono'],imperf:['evo','evi','eva','evamo','evate','evano'],remoto:['etti','esti','ette','emmo','este','ettero'],subj_pres:['a','a','a','iamo','iate','ano'],subj_imperf:['essi','essi','esse','essimo','este','essero']},
 'ire':{pres:['o','i','e','iamo','ite','ono'],imperf:['ivo','ivi','iva','ivamo','ivate','ivano'],remoto:['ii','isti','ì','immo','iste','irono'],subj_pres:['a','a','a','iamo','iate','ano'],subj_imperf:['issi','issi','isse','issimo','iste','issero']}
};
function isArr(x){return Object.prototype.toString.call(x)==='[object Array]';}
function pre(x,f){if(f===undefined||f==='')return f;if(!x)return f;return x+f;}
function r0(s){return s.slice(0,-1);}

// 拼写修正：-care/-gare 前 i/e 加 h；-ciare/-giare/-sciare 前 i 结尾去 i；-iare_t 保留 i
function fixSpell(ch, stem, ending){
  if(ch==='care'||ch==='gare'){
    if(ending.charAt(0)==='i'||ending.charAt(0)==='e')return stem+'h'+ending;
    return stem+ending;
  }
  if(ch==='ciare'||ch==='giare'||ch==='sciare'){
    if(ending.charAt(0)==='i')return stem.slice(0,-1)+ending;
    return stem+ending;
  }
  return stem+ending;
}

function buildPres(spec){
  var t=spec.type,ch=spec.ch,stem=spec.stem,out=[];
  for(var i=0;i<6;i++){
    if(ch==='isc'){
      out.push(i<3||i===5 ? stem+['isco','isci','isce','','','iscono'][i] : stem+['','','','iamo','ite',''][i]);
    } else if(spec.iare){
      if(i<3){
        if(ch==='iare_t') out.push(stem+['o','i','a'][i]);                       // 重读 -iare：inviare→invio/invii/invia
        else if(i===0) out.push(stem+'o');                                       // 非重读：studiare→studio
        else if(i===1) out.push(stem.slice(0,-1)+'i');                           //                 → studi
        else out.push(stem+'a');                                                 //                 → studia
      } else {
        out.push(stem.slice(0,-1)+['iamo','iate','iano'][i-3]);
      }
    } else {
      out.push(fixSpell(ch,stem,END[t].pres[i]));
    }
  }
  return out;
}
function buildSubjPres(spec){
  var t=spec.type,ch=spec.ch,stem=spec.stem,out=[];
  for(var i=0;i<6;i++){
    if(ch==='isc'){
      out.push(i<3||i===5 ? stem+['isca','isca','isca','','','iscano'][i] : stem+['','','','iamo','iate',''][i]);
    } else if(spec.iare){
      if(i<3){
        if(ch==='iare_t') out.push(stem+'i');          // 重读：inviare→che io invii / odiare→che io odii / variare→che io varii
        else out.push(stem.slice(0,-1)+'i');            // 非重读：studiare→che io studi
      } else {
        // 3 复数：重读 -iare 保留 i（avviino/inviino/odiino），非重读 -iare 去掉 i（studino/cambino/inizino/varino/ammobilino）
        if(i===5) out.push((ch==='iare_t')?stem+'ino':stem.slice(0,-1)+'ino');
        else out.push(stem.slice(0,-1)+['iamo','iate','ino'][i-3]);
      }
    } else {
      out.push(fixSpell(ch,stem,END[t].subj_pres[i]));
    }
  }
  return out;
}
function buildImperf(spec){
  var t=spec.type,stem=spec.stem;
  return END[t].imperf.map(function(e){return stem+e;});
}
function buildRemoto(spec){
  var t=spec.type,stem=spec.stem;
  return END[t].remoto.map(function(e){return stem+e;});
}
function buildFutCond(spec,which){
  var t=spec.type,stem=spec.stem,ch=spec.ch;
  var base;
  if(t==='ire')base=stem+'ir';
  else if(ch==='care'||ch==='gare')base=stem+'her';
  else if(ch==='ciare'||ch==='giare'||ch==='sciare')base=stem.slice(0,-1)+'er';
  else if(spec.iare)base=(stem.slice(-1)==='i'||/(sc|cc|gg|[cg])$/.test(stem))?stem+'er':stem+'i'+'er';   // -iare 未来/条件式：词干以 c/g/sc/cc/gg 结尾去主题 i（viaggiare→viaggerò / mangiare→mangerò / lasciare→lascerò），其余保留 i（studiare→studierò / raschiare→raschierò）   // 纯 -iare：iniziare(词干inizi)→inizierò / viaggiare→viaggierò / odiare(odi)→odierò / studiare→studierò
  else base=stem+'er';
  var ends = which==='fut' ? ['ò','ai','à','emo','ete','anno'] : ['ei','esti','ebbe','emmo','este','ebbero'];
  return ends.map(function(e){return base+e;});
}
function buildSubjImperf(spec){
  var t=spec.type,stem=spec.stem;
  return END[t].subj_imperf.map(function(e){return stem+e;});
}
function buildImp(spec,pres,subj){
  var t=spec.type,ch=spec.ch,stem=spec.stem;
  var tu,lei,noi,voi,loro;
  if(ch==='isc'){
    tu=stem+'isci'; lei=stem+'isca'; noi=stem+'iamo'; voi=stem+'ite'; loro=stem+'iscano';
  } else if(spec.iare){
    tu=stem.slice(0,-1)+'ia';
    lei = (ch==='iare_t') ? stem.slice(0,-1)+'ii' : stem.slice(0,-1)+'i';   // 重读 invii / 非重读 studi
    noi=stem.slice(0,-1)+'iamo'; voi=stem.slice(0,-1)+'iate'; loro=(ch==='iare_t')?stem+'ino':stem.slice(0,-1)+'ino';   // 重读 -iare 保留 i（avviino/inviino），非重读去掉 i（studino/varino）
  } else {
    // 命令式 tu：仅 -are 用 'a'（parla），-ere/-ire 与虚拟式 tu 同形（credi/finisci）
    tu = (t==='are') ? stem+'a' : fixSpell(ch,stem,END[t].pres[1]);
    lei=subj[2]; noi=subj[3]; voi=fixSpell(ch,stem,END[t].pres[4]); loro=subj[5];
  }
  return ['',tu,lei,noi,voi,loro];
}
function buildGerPPRPP(spec){
  var t=spec.type,stem=spec.stem,ch=spec.ch;
  var ger,pp,ppr;
  if(t==='are'){ger=stem+'ando';pp=stem+'ato';ppr=stem+'ante';}
  else if(t==='ere'){ger=stem+'endo';pp=stem+'uto';ppr=stem+'ente';}
  else {ger=stem+'endo';pp=stem+'ito';ppr=stem+'ente';}
  return {ger:ger,pp:pp,ppr:ppr};
}

// 解析基础变位（支持完全模型 + 半不规则部分模型 + 前缀派生）
function buildBase(v){
  var refl = v.i.slice(-2)==='si';
  var m = v.b ? MODELS[v.b] : null;
  // 自反动词 v.i 形如 lavarsi，基数原形存于 v.bi（lavare）。派生动词（v.b 为去前缀基形，如 ac+correre→correre）须用 v.b 作基数，避免前缀叠加成 acaccorro。
  var baseInf = refl ? (v.bi || v.i.slice(0,-2)) : (v.b ? v.b : v.i);
  // 确定类型与词干：意大利语后缀为 3 字符（-are/-ere/-ire）
  var type = baseInf.slice(-3);
  var stem = baseInf.slice(0,-3);
  var ch = v.ch;
  var isIare = baseInf.slice(-4)==='iare' && !(ch==='ciare'||ch==='giare'||ch==='sciare');   // 纯 -iare（studiare/inviare…），排除 -ciare/-giare/-sciare
  var spec = {type:type, stem:stem, ch:ch, iare:isIare};
  var x = v.x||'';
  function fill(field, fn){
    var val;
    if(m && m[field]!==undefined){ val = m[field]; }
    else { val = fn(); }
    if(isArr(val)) return val.map(function(s){return pre(x,s);});
    return pre(x,val);
  }
  var pres = fill('pres', function(){return buildPres(spec);});
  var imperf = fill('imperf', function(){return buildImperf(spec);});
  var remoto = fill('remoto', function(){return buildRemoto(spec);});
  var fut = fill('fut', function(){return buildFutCond(spec,'fut');});
  var cond = fill('cond', function(){return buildFutCond(spec,'cond');});
  var base_subj_pres = (m && m.subj_pres!==undefined) ? m.subj_pres : buildSubjPres(spec);
  var subj_pres = fill('subj_pres', function(){return base_subj_pres;});
  var subj_imperf = fill('subj_imperf', function(){return buildSubjImperf(spec);});
  var gp = buildGerPPRPP(spec);
  var ger = pre(x, (m&&m.ger)?m.ger:gp.ger);
  var ppr = pre(x, v.ppr ? v.ppr : (m&&m.ppr)?m.ppr:gp.ppr);
  var pp = v.pp ? pre(x,v.pp) : pre(x,(m&&m.pp)?m.pp:gp.pp);
  // 命令式的 lei/loro 取自 subj_pres；此处传【未前缀化】的 base_subj_pres，
  // 由 fill 统一前缀化一次，避免前缀动词（基形模型缺 imp 时）出现双重前缀（acaccorra）。
  var imp = fill('imp', function(){return buildImp(spec, pres, base_subj_pres);});
  return {pres:pres,imperf:imperf,remoto:remoto,fut:fut,cond:cond,
          subj_pres:subj_pres,subj_imperf:subj_imperf,imp:imp,
          ger:ger,ppr:ppr,pp:pp,inf:baseInf,aux:v.aux};
}

function buildFull(v){
  var refl = v.i.slice(-2)==='si';
  var b = buildBase(v);
  var aux = refl ? 'e' : b.aux;         // 自反一律 essere
  var A = aux==='e' ? ESSERE : AVERE;
  var pp = b.pp;

  // 复合时态（essere/自反 → 分词性数一致：noi/voi/loro 用复数 -i）
  function compound(AUX){
    var ppPl = pp.slice(0,-1)+'i';
    return AUX.map(function(h,idx){
      var p = (aux==='e' && idx>=3) ? ppPl : pp;
      return h+' '+p;
    });
  }
  function reflCompound(AUX){
    var ppPl = pp.slice(0,-1)+'i';
    return AUX.map(function(h,idx){
      var p = (idx>=3) ? ppPl : pp;
      return REFL[idx]+' '+h+' '+p;
    });
  }

  // 简单时态（自反 → 加反身代词）
  function simple(arr){ return refl ? arr.map(function(f,i){return REFL[i]+' '+f;}) : arr; }

  var ind_pres = simple(b.pres);
  var ind_imperf = simple(b.imperf);
  var ind_remoto = simple(b.remoto);
  var ind_fut = simple(b.fut);
  var ind_cond = simple(b.cond);
  var subj_pres = simple(b.subj_pres);
  var subj_imperf = simple(b.subj_imperf);

  var ind_perf = refl ? reflCompound(A.pres) : compound(A.pres);
  var ind_plus = refl ? reflCompound(A.imperf) : compound(A.imperf);
  var ind_remoto_ant = refl ? reflCompound(A.remoto) : compound(A.remoto);
  var ind_fut_perf = refl ? reflCompound(A.fut) : compound(A.fut);
  var subj_perf = refl ? reflCompound(A.subj_pres) : compound(A.subj_pres);
  var subj_plus = refl ? reflCompound(A.subj_imperf) : compound(A.subj_imperf);
  var cond_perf = refl ? reflCompound(A.cond) : compound(A.cond);

  var imp;
  if(refl){
    var baseImp = b.imp;
    imp = ['',
      baseImp[1]+'ti',          // lavati
      'si '+baseImp[2],         // si lavi
      baseImp[3].slice(0,-1)+'ci', // laviamoci
      baseImp[4]+'vi',          // lavatevi
      'si '+baseImp[5]          // si lavino
    ];
  } else {
    imp = b.imp;
  }

  // 否定命令式 Imperativo negativo
  // 非自反：tu = non + 原形；noi/voi = non + 现在时；Lei/Loro = non + 虚拟式现在时
  // 自反：tu = non ti + 原形（b.inf 已是去 si 基数）；noi/voi 复用带代词的现在时；Lei/Loro = non si + 虚拟式
  var sp2 = b.subj_pres[2], sp5 = b.subj_pres[5];
  var simp = simple(b.pres);          // 自反时已带 mi/ti/ci/vi/si 代词
  var imp_neg;
  if(refl){
    imp_neg = ['',
      'non ti '+b.inf,      // non ti lavare
      'non si '+sp2,        // non si lavi
      'non '+simp[3],       // non ci laviamo
      'non '+simp[4],       // non vi lavate
      'non si '+sp5         // non si lavino
    ];
  } else {
    imp_neg = ['',
      'non '+b.inf,         // non parlare
      'non '+sp2,           // non parli
      'non '+simp[3],       // non parliamo
      'non '+simp[4],       // non parlate
      'non '+sp5            // non parlino
    ];
  }

  var inf = refl ? b.inf.slice(0,-1)+'si' : b.inf;   // lavare -> lavarsi（去 e 换 si）
  var inf_comp = (refl ? 'essersi' : A.inf) + ' ' + pp;
  var ger = refl ? b.ger+'si' : b.ger;                // lavando -> lavandosi（直接加 si）
  var ger_comp = (refl ? 'essendosi' : A.ger) + ' ' + pp;

  // 过去分词性数一致（m.sg / f.sg / m.pl / f.pl）：意语过去分词阳单恒以 -o 结尾
  var ppAgree;
  if(pp.charAt(pp.length-1)==='o'){
    ppAgree=[pp, pp.slice(0,-1)+'a', pp.slice(0,-1)+'i', pp.slice(0,-1)+'e'];
  } else {
    ppAgree=[pp,pp,pp,pp];
  }

  return {
    ind_pres:ind_pres, ind_perf:ind_perf, ind_imperf:ind_imperf, ind_plus:ind_plus,
    ind_remoto:ind_remoto, ind_remoto_ant:ind_remoto_ant, ind_fut:ind_fut, ind_fut_perf:ind_fut_perf,
    subj_pres:subj_pres, subj_perf:subj_perf, subj_imperf:subj_imperf, subj_plus:subj_plus,
    cond_pres:ind_cond, cond_perf:cond_perf,
    imp:imp, imp_neg:imp_neg,
    inf:inf, inf_comp:inf_comp, ger:ger, ger_comp:ger_comp, ppr:b.ppr, pp:pp, pp4:ppAgree,
    aux:aux, refl:refl
  };
}
"""
print("引擎已就绪")
