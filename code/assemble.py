import re,sys,os
B=sys.argv[1]
s=open(f"{B}/main_src.tex").read()
s=re.sub(r"%%TABLE:(\w+)%%",lambda m:open(f"{B}/tables/{m.group(1)}.tex").read().rstrip(),s)
for a,b in [(r"Barab\'{a}si--Albert","Barab\\'{a}si-Albert"),("Watts--Strogatz","Watts-Strogatz"),(r"Erd\H{o}s--R\'{e}nyi","Erd\\H{o}s-R\\'{e}nyi"),("Mann--Whitney","Mann-Whitney")]:
    body,bib=s.split(r"\begin{thebibliography}")
    s=body.replace(a,b)+r"\begin{thebibliography}"+bib
open(f"{B}/manuscript_revised.tex","w").write(s)
body=s.split(r"\begin{thebibliography}")[0]
print("remaining -- in body:",[l.strip()[:70] for l in body.splitlines() if "--" in l and not l.strip().startswith("%")][:10])
