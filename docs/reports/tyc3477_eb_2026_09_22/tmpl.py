import subprocess,urllib.parse,csv,io
def tap(q):
    u="http://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync?request=doQuery&lang=adql&format=csv&query="+urllib.parse.quote(q)
    p=subprocess.run(["curl","-sL","--max-time","300",u],capture_output=True,text=True); return p.stdout
T='"III/286/catalog"'
cols=tap(f"SELECT TOP 1 * FROM {T}").splitlines()[0]; print("columns:",cols[:700])
