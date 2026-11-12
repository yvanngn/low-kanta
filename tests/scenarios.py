#!/usr/bin/env python3
"""Tests de Low Kanta : python3 tests/scenarios.py [intro] [galerie] [c1] [contenu]  (sans argument : tout)."""
import sys, os, re
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL='file://'+os.path.join(ROOT,'low-kanta.html')
ok=0; ko=[]
def check(cond,msg):
    global ok
    if cond: ok+=1
    else: ko.append(msg); print('ÉCHEC :',msg)

HOOK="""()=>{window.__lignes=[];window.__vg=[];const s0=say;window.say=say=(t,g,w)=>{__lignes.push([w||'browny',t]);return s0(t,g,w);};
 const v0=vignette;window.vignette=vignette=(v,l)=>{__vg.push(v.type+(v.eq?':'+v.eq.nom:''));return v0(v,l);};}"""
def page(pw):
    b=pw.chromium.launch(); p=b.new_page(viewport={'width':960,'height':600})
    p.errs=[]; p.on('pageerror',lambda e:p.errs.append(str(e)))
    p.goto(URL); p.evaluate(HOOK); return b,p
def avancer(p,cond,max_s=60):
    """Clique sur la scène (passe les répliques) jusqu'à ce que cond (JS) soit vrai."""
    for _ in range(int(max_s*10)):
        if p.evaluate(cond): return True
        p.evaluate("()=>{ if(cur) fin(); else if(mode==='c1'&&vg.type==='planche') rapide=true; }"); p.wait_for_timeout(100)
    return False
def ecran(p): return p.evaluate("()=>$('screen').style.display==='flex'?$('screen').innerText:''")

def t_intro(pw):
    b,p=page(pw)
    check(p.evaluate("()=>mode")=='menu','au chargement : menu')
    p.click('#mNew')
    check(avancer(p,"()=>mode==='titre'"),"l'intro se termine sur l'écran titre")
    L=p.evaluate("()=>__lignes")
    check(len(L)==len(p.evaluate("()=>LIGNES")),'toutes les répliques de l’intro sont dites')
    check(all(w=='browny' for w,_ in L),'l’intro est dite par Browny')
    check(L and L[0][1].startswith('Bonsoir'),'première réplique : Bonsoir…')
    check(L and 'C’est parti' in L[-1][1],'dernière réplique : C’est parti !')
    check('LOW' in ecran(p) and 'KANTA' in ecran(p),'écran titre LOW KANTA')
    # bulle : nom et portrait
    p.evaluate("()=>{say('test',0);}")
    check(p.evaluate("()=>bubble.querySelector('.nom').textContent")=='Browny Grognard','la bulle affiche le nom de Browny')
    check(p.evaluate("()=>!!bubble.querySelector('canvas.por')"),'la bulle affiche un portrait')
    p.evaluate("()=>fin()")
    p.evaluate("()=>{lancer(MDP['0']);}"); p.wait_for_timeout(200)
    # Passer pendant l'intro
    p.click('#bSkip'); p.wait_for_timeout(200)
    check(p.evaluate("()=>mode")=='titre','Passer pendant l’intro mène à l’écran titre')
    # Son
    p.click('#bSound'); check(p.inner_text('#bSound')=='Son : non','bouton Son : coupe le son')
    p.click('#bSound'); check(p.inner_text('#bSound')=='Son : oui','bouton Son : remet le son')
    check(not p.errs,'aucune erreur JS (intro) '+str(p.errs)); b.close()

def t_galerie(pw):
    b,p=page(pw)
    p.evaluate("()=>{started=true;titre();}"); p.click('#scene')
    check(p.evaluate("()=>mode")=='bande','clic sur le titre : bande-annonce')
    noms=[]
    for _ in range(200):
        if p.evaluate("()=>mode")!='bande': break
        n=p.evaluate("()=>$('bande').querySelector('b')?$('bande').querySelector('b').textContent:''")
        if n and (not noms or noms[-1]!=n): noms.append(n)
        p.evaluate("()=>{renderBande(performance.now());}"); p.wait_for_timeout(250)
        if len(noms)>=3: p.click('#scene'); p.wait_for_timeout(50)
    check(len(noms)==15,'bande-annonce : les 15 aventuriers défilent (%d)'%len(noms))
    check(p.evaluate("()=>mode")=='fin' and 'Chapitre 1' in ecran(p),'après la bande-annonce : écran Chapitre 1')
    p.evaluate("()=>{menu();}"); p.click('#mCast'); p.wait_for_timeout(200)
    check(p.evaluate("()=>mode")=='troupe','menu : Les aventuriers affiche toute la troupe')
    box=p.locator('#cv').bounding_box()
    for i in [3,14]:
        cx,cy=p.evaluate("i=>troupeCase(i)",i); p.mouse.move(box['x']+(cx+12)/320*box['width'],box['y']+(cy+20)/144*box['height']); p.wait_for_timeout(80)
        nom,txt=p.evaluate("i=>[CAST[i].nom,PRESENTE[CAST[i].id]]",i)
        check(nom in p.inner_text('#troupeFiche') and txt[:25] in p.inner_text('#troupeFiche'),'survol : présentation de '+nom)
    cx,cy=p.evaluate("()=>troupeCase(7)"); p.mouse.click(box['x']+(cx+12)/320*box['width'],box['y']+(cy+20)/144*box['height'])
    check(p.evaluate("()=>troupeSel")==7,'clic : présentation de l’aventurier cliqué')
    p.evaluate("()=>{setV2(true);renderTroupe(500);setV2(false);renderTroupe(500);}")
    check(not p.errs,'portraits de la troupe en V1 et en V2')
    p.evaluate("()=>{lancer(MDP['0']);}"); p.wait_for_timeout(200)
    check(not p.is_visible('#troupeFiche') and not p.is_visible('#bTroupeMenu'),'en quittant Les aventuriers, le panneau disparaît')
    p.evaluate("()=>{troupe();}")
    p.click('#bTroupeMenu'); check(p.evaluate("()=>mode")=='menu' and not p.is_visible('#troupeFiche'),'Retour au menu')
    # Passer pendant la bande-annonce
    p.evaluate("()=>{titre();}"); p.click('#scene'); p.wait_for_timeout(200); p.wait_for_timeout(100)
    check(p.is_visible('#bPasseBande'),'bouton Passer le générique visible'); p.click('#bPasseBande'); p.wait_for_timeout(200)
    check(p.evaluate("()=>mode")=='fin' and not p.is_visible('#bPasseBande'),'Passer le générique mène à l’écran Chapitre 1')
    check(not p.errs,'aucune erreur JS (galerie) '+str(p.errs)); b.close()

def t_c1(pw):
    b,p=page(pw)
    p.evaluate("()=>{started=true;finGalerie();}"); p.click('#scene')
    check(p.evaluate("()=>mode")=='c1','clic sur Chapitre 1 : lance le chapitre')
    # équipes
    E=p.evaluate("()=>EQUIPES"); ids=p.evaluate("()=>CAST.map(c=>c.id)")
    R,J=E['rouge']['ids'],E['jaune']['ids']
    check(len(R)==7 and len(J)==7,'deux équipes de 7')
    check(not set(R)&set(J),'personne dans les deux équipes')
    check('geoffrey' not in R+J,'Geoffrey sans équipe')
    check(sorted(R+J+['geoffrey'])==sorted(ids),'tout le monde est tiré (sauf Geoffrey)')
    check(E['rouge']['nom']=='Les Nemopor' and E['jaune']['nom']=='Les Bobun','noms des équipes')
    # planche BD : les cases apparaissent une par une
    check(avancer(p,"()=>vg.type==='planche'"),'planche du tirage affichée')
    n1=p.evaluate("()=>vg.n"); p.wait_for_timeout(700); n2=p.evaluate("()=>vg.n")
    check(0<=n1<n2<14,'les cases apparaissent une par une (%s → %s)'%(n1,n2))
    p.click('#scene'); p.wait_for_timeout(1200)
    check(p.evaluate("()=>vg.n===14||vg.type!=='planche'"),'un clic affiche toutes les cases')
    check(avancer(p,"()=>mode==='finC1'"),'le chapitre 1 se termine')
    V=p.evaluate("()=>__vg")
    attendu=['large','presentateur','planche','equipe:Les Nemopor','equipe:Les Bobun','geoffrey','presentateur','ile']
    check(V==attendu,'ordre des vignettes '+str(V))
    L=p.evaluate("()=>__lignes")
    check({w for w,_ in L}<= {'browny','geoffrey'},'seuls Browny et Geoffrey parlent')
    check(any(w=='geoffrey' for w,_ in L),'Geoffrey réagit')
    T=' '.join(t for _,t in L)
    check('île déserte' in T and 'spéciale' in T,'annonce de la saison spéciale et de l’île déserte')
    check('Seul sur l’île' in ecran(p),'écran Chapitre 1 : Seul sur l’île')
    # Passer pendant le chapitre
    p.evaluate("()=>{finGalerie();}"); p.click('#scene'); p.wait_for_timeout(200); p.click('#bSkip'); p.wait_for_timeout(200)
    check(p.evaluate("()=>mode")=='finC1','Passer pendant le chapitre 1 mène à la fin')
    # chaque vignette se dessine sans erreur
    p.evaluate("""()=>{const o=[];for(let i=0;i<7;i++){o.push(['rouge',EQUIPES.rouge.ids[i]]);o.push(['jaune',EQUIPES.jaune.ids[i]]);}
      mode='c1';[{type:'large'},{type:'presentateur'},{type:'planche',ordre:o,n:14},{type:'equipe',eq:EQUIPES.rouge},{type:'geoffrey'},{type:'ile'}].forEach(v=>{vg=v;renderC1(0);});}""")
    check(not p.errs,'aucune erreur JS (chapitre 1) '+str(p.errs)); b.close()

def t_jeu(pw):
    b,p=page(pw)
    p.evaluate("()=>{started=true;finC1();}"); p.click('#scene')
    check(p.evaluate("()=>mode")=='jeu' and p.evaluate("()=>G.room")=='plage','clic : on joue G sur la plage')
    check(p.is_visible('#verbs') and p.is_visible('#inv'),'verbes et inventaire visibles')
    p.evaluate("()=>fin()"); p.wait_for_timeout(100)
    A=lambda v,id: p.evaluate("""async([v,id])=>{occupe=false;verbe=v;const s=ROOMS[G.room].spots.find(x=>x.id===id);const pr=clicJeu(s.r[0]+s.r[2]/2-Math.round(camX),s.r[1]+s.r[3]/2);
       for(let i=0;i<200&&!cur;i++)await wait(20);const t=__lignes.length?__lignes[__lignes.length-1][1]:'';if(cur)fin();await pr;return t;}""",[v,id])
    O=lambda v,id: p.evaluate("""async([v,id])=>{occupe=false;verbe=v;const pr=clicObjet(id);for(let i=0;i<50&&!cur;i++)await wait(20);const t=cur?__lignes[__lignes.length-1][1]:'';if(cur)fin();await pr;return t;}""",[v,id])
    check('poisson' in A('examiner','poisson').lower(),'examiner le poisson')
    A('prendre','poisson'); check(p.evaluate("()=>G.inv.includes('poisson')"),'prendre le poisson')
    check(p.evaluate("()=>!spotsVisibles().some(s=>s.id==='poisson')"),'le poisson n’est plus sur la plage')
    p.evaluate("()=>{verbe='utiliser';sel=null;}"); p.evaluate("()=>clicObjet('poisson')")
    check(p.evaluate("()=>sel")=='poisson','Utiliser + poisson : poisson sélectionné')
    check('pue' in O('utiliser','poisson'),'manger le poisson : ça pue trop')
    check('corde' in A('examiner','bateau').lower(),'examiner le bateau : il reste de la corde')
    A('prendre','mat'); check(p.evaluate("()=>G.inv.includes('corde')&&G.f.corde"),'prendre la corde du mât')
    check('déjà' in A('prendre','mat'),'pas de deuxième corde')
    check(A('ouvrir','bateau')==p.evaluate("()=>DEF.ouvrir"),'réponse par défaut')
    check(p.evaluate("()=>[...document.querySelectorAll('#verbs .vb')].map(b=>b.textContent).join()")=='Ouvrir,Examiner,Prendre,Utiliser,Parler,Donner','les 6 verbes du moteur')
    check(A('parler','bateau')==p.evaluate("()=>DEF.parler"),'Parler : personne à qui parler')
    check(A('donner','bateau')==p.evaluate("()=>DEF.donnerSansObjet"),'Donner sans objet : choisir un objet')
    p.evaluate("()=>{verbe='donner';sel=null;clicObjet('corde');}"); check(p.evaluate("()=>sel")=='corde','Donner + objet : objet sélectionné')
    t=p.evaluate("async()=>{const s=ROOMS.plage.spots.find(x=>x.id==='bateau');occupe=false;const pr=clicJeu(s.r[0]+5-Math.round(camX),s.r[1]+5);for(let i=0;i<200&&!cur;i++)await wait(20);const t=__lignes[__lignes.length-1][1];fin();await pr;return t;}")
    check(t==p.evaluate("()=>DEF.donner"),'Donner un objet : personne sur l’île')
    A(None,'acces_bois'); p.wait_for_timeout(500)
    check(p.evaluate("()=>G.room")=='bois','l’accès au bois mène au bois')
    A('prendre','branches'); check(p.evaluate("()=>G.inv.includes('bois')&&G.taches.bois"),'prendre du bois : tâche bois faite')
    A(None,'plus_loin'); p.wait_for_timeout(500)
    check(p.evaluate("()=>G.room")=='source','plus loin dans les bois : la source')
    check(not p.evaluate("()=>G.taches.eau"),'eau pas encore trouvée avant de l’examiner')
    A('examiner','eau'); check(p.evaluate("()=>G.taches.eau"),'trouver l’eau : tâche eau faite')
    check(p.inner_text('#bListe')=='Liste 2/2','liste 2/2')
    A(None,'retour_bois'); p.wait_for_timeout(500); A(None,'retour_plage'); p.wait_for_timeout(500)
    check(p.evaluate("()=>G.room")=='plage','retour à la plage')
    check(p.evaluate("()=>G.inv.length")==3,'inventaire : poisson, corde, bois')
    check(p.evaluate("()=>ROOMS.plage.w")==640,'la plage est plus large que l’écran')
    p.evaluate("()=>{heros.x=heros.tx=620;}"); p.wait_for_timeout(1500)
    check(p.evaluate("()=>Math.round(camX)")==320,'la caméra suit Geoffrey jusqu’au bout de la plage')
    p.evaluate("()=>{heros.x=heros.tx=20;}"); p.wait_for_timeout(1500)
    check(p.evaluate("()=>Math.round(camX)")==0,'la caméra revient au début de la plage')
    p.click('#bListe'); check('Trouver du bois' in ecran(p),'la liste s’affiche'); p.click('#scene'); check(ecran(p)=='','un clic ferme la liste')
    for room in ['plage','bois','source']: p.evaluate("r=>{G.room=r;renderJeu(0);}",room)
    # mises à jour communes (skill interface-jeu)
    p.evaluate("()=>{G.room='plage';heros.x=heros.tx=300;heros.y=heros.ty=108;camX=camCible();allerA(200,108);}"); p.wait_for_timeout(300)
    check(p.evaluate("()=>vueHeros")=='profil' and p.evaluate("()=>heros.dir")==-1,'de profil, tourné à gauche quand il marche à gauche')
    p.evaluate("()=>{allerA(320,108);}"); p.wait_for_timeout(400)
    check(p.evaluate("()=>vueHeros")=='profil' and p.evaluate("()=>heros.dir")==1,'de profil, tourné à droite quand il marche à droite')
    p.evaluate("()=>{heros.x=heros.tx;heros.y=heros.ty;heros.marche=false;}"); p.wait_for_timeout(150)
    check(p.evaluate("()=>vueHeros")=='face','de face à l’arrêt')
    box=p.locator('#cv').bounding_box()
    def survol(wx,wy):
        sx=(wx-p.evaluate("()=>Math.round(camX)"))/320*box['width']+box['x']; sy=wy/144*box['height']+box['y']; p.mouse.move(sx,sy); p.wait_for_timeout(50)
        return p.evaluate("()=>$('cur').className")
    p.evaluate("()=>{verbe=null;sel=null;}")
    check('exit' in survol(302,50),'curseur vert sur une sortie')
    check(survol(160,100)=='','curseur simple sur le sable')
    p.evaluate("()=>{verbe='utiliser';sel='corde';}")
    c=survol(160,100); check(p.evaluate("()=>!!$('cur').querySelector('canvas')"),'icône de l’objet choisi près du curseur')
    p.evaluate("()=>{verbe=null;sel=null;}")
    p.evaluate("()=>{say('Un texte assez long pour s’écrire lettre à lettre.',0,'geoffrey');}"); p.wait_for_timeout(100)
    n1=p.evaluate("()=>bubble.querySelector('span').textContent.length")
    p.evaluate("()=>cliquerTexte()")
    check(p.evaluate("()=>!!cur&&bubble.querySelector('span').textContent.endsWith('lettre à lettre.')"),'un clic termine le texte qui s’écrit')
    p.evaluate("()=>cliquerTexte()"); check(p.evaluate("()=>!cur"),'le clic suivant ferme la bulle')
    check(n1<45,'le texte s’écrit lettre à lettre')
    check(not p.errs,'aucune erreur JS (jeu) '+str(p.errs)); b.close()

def t_menu(pw):
    b,p=page(pw)
    check(p.evaluate("()=>mode")=='menu','le jeu s’ouvre sur le menu')
    check('LOW' in ecran(p) and 'KANTA' in ecran(p) and p.is_visible('.logo'),'logo LOW KANTA')
    check(p.is_visible('#mNew') and p.is_visible('#mPw'),'boutons Nouvelle partie et mot de passe')
    check(p.evaluate("()=>(()=>{ const els=[...document.querySelectorAll('#game, #game button, #game div')].slice(0,60); return els.length>1&&els.every(el=>{ const e=new MouseEvent('contextmenu',{bubbles:true,cancelable:true}); el.dispatchEvent(e); return e.defaultPrevented; }); })()"),'clic droit : jamais le menu du navigateur')
    p.click('#scene',position={'x':20,'y':20}); check(p.evaluate("()=>mode")=='menu','cliquer l’image ne quitte pas le menu')
    p.fill('#mPw','zzz'); p.click('#mOk'); check('inconnu' in p.inner_text('#mMsg'),'mauvais mot de passe : message')
    p.fill('#mPw','1'); p.click('#mOk'); p.wait_for_timeout(200); check(p.evaluate("()=>mode")=='c1','mot de passe 1 : chapitre 1')
    p.click('#bReplay'); p.wait_for_timeout(200); check(p.evaluate("()=>mode")=='menu','bouton Menu : retour au menu')
    p.fill('#mPw','0'); p.press('#mPw','Enter'); p.wait_for_timeout(200); check(p.evaluate("()=>mode")=='intro','mot de passe 0 (Entrée) : intro')
    p.evaluate("()=>{finGalerie();}"); check('Mot de passe : 1' in ecran(p),'l’écran du chapitre 1 donne son mot de passe')
    p.click('#bReplay'); p.click('#mNew'); p.wait_for_timeout(200); check(p.evaluate("()=>mode")=='intro','Nouvelle partie : intro')
    check(not p.errs,'aucune erreur JS (menu) '+str(p.errs)); b.close()

def t_contenu(pw):
    src=open(os.path.join(ROOT,'low-kanta.html'),encoding='utf8').read()+open(os.path.join(ROOT,'PERSONNAGES.md'),encoding='utf8').read()
    for mot in ['Koh','KOH','Denis','origine','asiatique','arabe','espagnol','Espagne']:
        check(mot not in src,'mot interdit absent : '+mot)

def t_v2(pw):
    b,p=page(pw)
    check(p.is_visible('#mV2') and 'V1' in p.inner_text('#mV2'),'menu : bouton Graphismes (V1 par défaut)')
    p.click('#mV2'); check(p.evaluate("()=>V2&&document.body.classList.contains('v2')") and 'V2' in p.inner_text('#mV2'),'menu : passage en V2')
    p.wait_for_timeout(200)
    for m in ['menu','galerie','c1']: p.evaluate("m=>{mode=m;}",m); p.wait_for_timeout(120)
    p.evaluate("()=>{mode='c1';for(const v of [{type:'large'},{type:'pick',eq:EQUIPES.rouge,id:'ben'},{type:'ile'},{type:'planche',ordre:[['rouge','ben'],['jaune','yohan']],n:2}]){vg=v;renderC1(500);}}")
    p.evaluate("()=>{started=true;finC1();}"); p.click('#scene')
    check(p.is_visible('#tuto') and 'Clic gauche' in p.inner_text('#tuto'),'V2 : le tuto s’ouvre au début du jeu')
    for _ in range(4): p.click('#tuto')
    check(not p.is_visible('#tuto') and p.evaluate("()=>mode")=='jeu','V2 : après le tuto, on joue Geoffrey')
    check(not p.is_visible('#verbs') and p.is_visible('#inv'),'V2 : pas de barre de verbes, inventaire visible')
    p.evaluate("()=>fin()"); p.wait_for_timeout(100); p.evaluate("()=>{say('Test en bas.',0,'geoffrey');}")
    bb=p.locator('#bubble').bounding_box(); sc=p.locator('#scene').bounding_box()
    check(bb['y']>sc['y']+sc['height']/2,'V2 : les dialogues s’affichent en bas')
    p.evaluate("()=>{fin();occupe=false;}")
    box=p.locator('#cv').bounding_box()
    def pt(wx,wy): return ((wx-p.evaluate("()=>Math.round(camX)"))/320*box['width']+box['x'], wy/144*box['height']+box['y'])
    def ligne(): 
        for _ in range(150):
            if p.evaluate("()=>!!cur"): break
            p.wait_for_timeout(20)
        t=p.evaluate("()=>__lignes.length?__lignes[__lignes.length-1][1]:''"); p.evaluate("()=>{if(cur)fin();}")
        for _ in range(100):
            if not p.evaluate("()=>occupe"): break
            p.wait_for_timeout(20)
        return t
    x,y=pt(426,110); p.mouse.click(x,y); ligne()
    check(p.evaluate("()=>G.inv.includes('poisson')"),'V2 clic gauche : action évidente (prendre le poisson)')
    p.evaluate("()=>{heros.x=heros.tx=140;heros.y=heros.ty=110;camX=camCible();}")
    x,y=pt(80,104); p.mouse.click(x,y,button='right')
    check(p.evaluate("()=>roueOuverte()") and p.locator('#roue button').count()==6,'V2 clic droit : la roue des 6 actions')
    p.click('#roue button[data-v="examiner"]')
    check('corde' in ligne().lower(),'V2 roue : examiner le bateau')
    check(not p.evaluate("()=>roueOuverte()"),'V2 : la roue se ferme après le choix')
    p.click('#inv .it'); check(p.evaluate("()=>sel")=='poisson','V2 inventaire : clic gauche = objet en main')
    x,y=pt(80,104); p.mouse.click(x,y); check(ligne()==p.evaluate("()=>DEF.utiliser"),'V2 : objet en main + clic = utiliser avec')
    p.click('#inv .it',button='right'); check('poisson' in ligne().lower(),'V2 inventaire : clic droit = examiner')
    for room in ['plage','bois','source']: p.evaluate("r=>{G.room=r;renderJeu(900);}",room)
    p.click('#bAide'); check(p.is_visible('#tuto'),'V2 : le bouton ? rouvre le tuto')
    check(not p.errs,'aucune erreur JS (v2) '+str(p.errs)); b.close()

GROUPES={'menu':t_menu,'intro':t_intro,'galerie':t_galerie,'c1':t_c1,'jeu':t_jeu,'v2':t_v2,'contenu':t_contenu}
if __name__=='__main__':
    noms=sys.argv[1:] or list(GROUPES)
    with sync_playwright() as pw:
        for n in noms: GROUPES[n](pw)
    print('%d vérifications, %d échec(s)'%(ok+len(ko),len(ko))); sys.exit(1 if ko else 0)
