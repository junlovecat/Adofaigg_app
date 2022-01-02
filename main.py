from tkinter import *
from tkinter import font
import pyglet
import clipboard
import requests
import json
import math


def returnartistlist():
    names=[]
    mainlink=[]
    status=[]
    disclaimer=[]
    artist_id=[]
    nd='Not Found'
    link='https://7thbeat.sgp1.digitaloceanspaces.com/adofai_dump/adofai_artists.json'
    info=requests.get(link).text
    a=json.loads(info)
    for x in range(len(a)):
        names.append(a[x]['name'])
        mainlink.append(a[x]['link_1'])
        status.append(a[x]['status'])
        if(len(a[x]['adofai_artist_disclaimers'])==0):
            disclaimer.append(nd)
            artist_id.append('')
        else:
            disclaimer.append(a[x]['adofai_artist_disclaimers'][0]['text'])
            artist_id.append(a[x]['adofai_artist_disclaimers'][0]['adofai_artist_id'])
    return names,mainlink,status,disclaimer,artist_id,True

def checkstring(upperr:str,lowerr:str):
    upperr=upperr.lower()
    lowerr=lowerr.lower()
    if(upperr==lowerr):
        return True
    elif(lowerr in upperr):
        return True
    else:
        return False

def is_digit(a:str):
    if(str(a).isdigit()):
        return True
    else:
        try:
            a=int(a)
        except ValueError:
            return False
        return True

def findid_adofai(query,amount=1000):
    '''
    This gives the ids of the level.\n
    It returns -1 if there is no level.\n
    RETURN:List(id)
    '''
    response=requests.get(
        "https://api.adofai.gg:9200/api/v1/levels",
        params={'offset':'0','amount':amount,'query':query},
        verify=False
    ).text
    
    e=json.loads(str(response))
    if len(e['results'])==0:return -1
    ids=[]
    for x in e['results']:ids.append(x['id'])
    return ids

def showid_adofai(query:str):
    '''
    This shows the information of the id.\n
    It returns -1 if there is no level.\n
    RETURN:Dict(songname,adofaigg,creator,difficulty,BPM,tiles,\n
    EW,download,video,workshop)
    '''
    response=response=requests.get(
        f"https://api.adofai.gg:9200/api/v1/levels/{query}",
        verify=False
    ).text
    if not response:
        return {'text':"Unknown"},{'text':"oof"}
    info=json.loads(str(response))
    map={}
    links={}
    if(info.get('error')):
        return {'text':"Unknown"},{'text':"oof"}
    map['songname']=str(f"{', '.join(list(info['artists']))} - {info['title']}")
    map['adofaigg']=str('https://adofai.gg/levels/'+str(info['id']))
    map['creator']=str(', '.join(list(info['creators'])))
    map['difficulty']=str(info['difficulty'])
    map['BPM']=str(float(float(info['minBpm'])+float(info['maxBpm']))/2)
    map['tiles']=str(info['tiles'])
    map['EW']=str(info['epilepsyWarning'])
    links['download']=str(info['download'])
    links['video']=str(info['video'])
    links['workshop']=str(info['workshop'])
    return map,links

def artist_adofai(artistname:str):
    '''
    This gives the information of the artist.\n
    It returns -1 if there is no artist.\n
    RETURN:Dict(name,url,status,link,disclaimer)
    '''
    names,links,statuses,disclaimers,artistids,dones=returnartistlist()
    if not dones:return None
    cur=-1
    for x in range(len(names)):
        if checkstring(names[x],artistname):
            cur=x
            break
    if cur==-1:return -1
    thelist={}
    thelist['name']=names[x]
    thelist['url']=f'https://7thbe.at/verified-artists/adofai/artist/{artistids[x]}' if artistids[x]!='' and is_digit(artistids[x]) else 'https://7thbe.at/verified-artists/'
    status=statuses[x]
    statustexts=['pending','Allowed','Mostly Disallowed','Disallowed','Mostly Allowed']
    thelist['status']=statustexts[status]
    thelist['link']=links[x]
    thelist['disclaimer']=disclaimers[x]
    return thelist

def calculatepp_adofai(id:int,realacc:float,realpitch:float):
    '''
    This gives the expected pp based on\n
    https://adofai.gg\n
    returns -1 if there is no map.\n
    RETURN:Str(pp)
    '''

    response=requests.get(
        f"https://api.adofai.gg:9200/api/v1/levels/{str(int(id))}",
        verify=False
    ).text
    if not response:return -1
    info=json.loads(str(response))
    pitch=realpitch/100
    difficulty=float(info['difficulty'])
    tile=int(info['tiles'])
    acc=(realacc)/(100+0.01*tile)
    levelbasicrate=float(1600/(1+math.exp(-0.42*float(difficulty)+7.4)))
    accrate=float(0.013/(acc*(-1)+1.0125)+0.2)
    pitchrate=float(math.pow(((1+pitch))/2,(min((0.1+math.pow(tile,0.5)/(math.pow(2000,0.5))),1.1)))) if pitch>=1 else math.pow(pitch,1.8)
    tilerate=float(0.84+tile/12500 if tile>2000 else math.pow((tile/2000),0.1))
    pp=math.pow(float(levelbasicrate*accrate*pitchrate*tilerate),1.01)
    return str(pp)


def findid():
    pyglet.font.add_file('oldphoto.TTF')
    def showsearchaction(test='BIND'):
        query=textbox.get()
        result=findid_adofai(query,5)
        if type(result)==list:
            resulttext=','.join(list(map(str,result)))
        else:resulttext='None'
        resultlabel=Label(window_findid,text=str(resulttext),font=font.Font(size=20,font='a옛날사진관3'))
        resultlabel.place_configure(height=100,width=400,x=0,y=50)
    window_findid=Tk()
    window_findid.wm_iconbitmap('favicon.ico')
    window_findid.wm_title('Find ID')
    window_findid.wm_geometry('400x322')
    exitbutton=Button(window_findid,text='X',command=window_findid.destroy,width=2,height=1,font=font.Font(size=10,font='a옛날사진관3'))
    exitbutton.grid_configure(row=0,column=0)
    textbox=Entry(window_findid,width=25,textvariable=str,font=font.Font(size=30))
    textbox.place_configure(height=40,x=30,y=0)
    searchButton=Button(window_findid,text='🔍',command=showsearchaction,width=4,height=2,font=font.Font(size=10))
    searchButton.place_configure(height=40,width=40,x=270,y=0)
    window_findid.bind('<Key>',showsearchaction)
    window_findid.mainloop()
    return
def showid():
    pyglet.font.add_file('oldphoto.TTF')
    def showsearchaction(test='BIND'):
        query=str(textbox.get())
        if query.isdigit()==False:
            pass
        result,links=showid_adofai(query)
        if(result.get('text')=='oof'):
            pass
        if type(result)==dict:
            resulttext='\n--------------------\n'.join(list(map(str,result.values())))
        else:resulttext='None'
        resultlabel=Label(window_showid,text=str(resulttext),font=font.Font(size=20,font='안동엄마까투리'))
        resultlabel.place_configure(height=450,width=500,x=0,y=50)
        try:
            downloadbutton=Button(window_showid,text='🔽',command=lambda:clipboard.copy(str(links['download'])),width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
            downloadbutton.place_configure(height=40,width=40,x=310,y=0)
            youtubebutton=Button(window_showid,text='📺',command=lambda:clipboard.copy(str(links['video'])),width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
            youtubebutton.place_configure(height=40,width=40,x=350,y=0)
            workshopbutton=Button(window_showid,text='📁',command=lambda:clipboard.copy(str(links['workshop'])) if links['workshop']!='None' else clipboard.copy('No Link :('),width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
            workshopbutton.place_configure(height=40,width=40,x=390,y=0)
        except:
            pass
        '''tkinter.messagebox.showinfo("LINKS",'\n'.join(links.values())+'\ncopied')
        clipboard.copy(str(links['download']))'''
    pyglet.font.add_file("KATURI.TTF")
    window_showid=Tk()
    window_showid.wm_iconbitmap('favicon.ico')
    window_showid.wm_title('Show ID')
    window_showid.wm_geometry('500x500')
    exitbutton=Button(window_showid,text='X',command=window_showid.destroy,width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
    exitbutton.grid_configure(row=0,column=0)
    textbox=Entry(window_showid,width=25,textvariable=str,font=font.Font(size=30))
    textbox.place_configure(height=40,x=30,y=0)
    searchButton=Button(window_showid,text='🔍',command=showsearchaction,width=4,height=2,font=font.Font(size=10))
    searchButton.place_configure(height=40,width=40,x=270,y=0)
    window_showid.bind('<Key>',showsearchaction)
    window_showid.mainloop()
    return
def findartist():
    def showsearchaction(test='BIND'):
        query=str(textbox.get())
        if query.isdigit()==False:
            pass
        result=artist_adofai(query)
        if type(result)==dict:
            resulttext='\n--------------------\n'.join(list(map(str,result.values())))
        else:resulttext='None'
        resultlabel=Label(window_findartist,text=str(resulttext),font=font.Font(size=15,font='안동엄마까투리'))
        resultlabel.place_configure(height=450,width=500,x=0,y=50)
        try:
            urlbutton=Button(window_findartist,text='1',command=lambda:clipboard.copy(str(result['url'])),width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
            urlbutton.place_configure(height=40,width=40,x=310,y=0)
            linkbutton=Button(window_findartist,text='2',command=lambda:clipboard.copy(str(result['link'])),width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
            linkbutton.place_configure(height=40,width=40,x=350,y=0)
            disbutton=Button(window_findartist,text='3',command=lambda:clipboard.copy(str(result['disclaimer'])) if result['disclaimer']!='None' else clipboard.copy('No disclaimer :('),width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
            disbutton.place_configure(height=40,width=40,x=390,y=0)
        except:
            pass
    pyglet.font.add_file("KATURI.TTF")
    window_findartist=Tk()
    window_findartist.wm_iconbitmap('favicon.ico')
    window_findartist.wm_title('Find ARTIST')
    window_findartist.wm_geometry('500x500')
    exitbutton=Button(window_findartist,text='X',command=window_findartist.destroy,width=2,height=1,font=font.Font(size=10,family='안동엄마까투리'))
    exitbutton.grid_configure(row=0,column=0)
    textbox=Entry(window_findartist,width=25,textvariable=str,font=font.Font(size=30))
    textbox.place_configure(height=40,x=30,y=0)
    searchButton=Button(window_findartist,text='🔍',command=showsearchaction,width=4,height=2,font=font.Font(size=10))
    searchButton.place_configure(height=40,width=40,x=270,y=0)
    window_findartist.bind('<Return>',showsearchaction)
    window_findartist.mainloop()
    return
def calpp():
    pyglet.font.add_file('oldphoto.TTF')
    def showsearchaction(test='BIND'):
        id=float(textbox1.get())
        realacc=float(textbox2.get())
        realpitch=float(textbox3.get())
        result=calculatepp_adofai(id,realacc,realpitch)
        resultlabel=Label(window_calpp,text=str(result),font=font.Font(size=50,font='a옛날사진관3'))
        resultlabel.place_configure(height=150,width=400,x=0,y=150)
    window_calpp=Tk()
    window_calpp.wm_iconbitmap('favicon.ico')
    window_calpp.wm_title('Calculate PP')
    window_calpp.wm_geometry('400x300')
    exitbutton=Button(window_calpp,text='X',command=window_calpp.destroy,width=2,height=1,font=font.Font(size=10,font='a옛날사진관3'))
    exitbutton.grid_configure(row=0,column=0)
    textbox1=Entry(window_calpp,width=25,textvariable=str,font=font.Font(size=30))
    textbox1.place_configure(height=40,x=30,y=0)
    textbox2=Entry(window_calpp,width=25,textvariable=str,font=font.Font(size=30))
    textbox2.place_configure(height=40,x=30,y=40)
    textbox3=Entry(window_calpp,width=25,textvariable=str,font=font.Font(size=30))
    textbox3.place_configure(height=40,x=30,y=80)
    searchButton=Button(window_calpp,text='🔍',command=showsearchaction,width=4,height=2,font=font.Font(size=10))
    searchButton.place_configure(height=40,width=40,x=270,y=0)
    window_calpp.bind('<Return>',showsearchaction)
    window_calpp.mainloop()
pyglet.font.add_file("KATURI.TTF")
window=Tk()
window.wm_iconbitmap('favicon.ico')
window.wm_title('Adofai.gg 1.0.0')
window.wm_geometry('340x322')
findidbutton=Button(window,text='ID 찾기',command=findid,width=10,height=5,font=font.Font(size=20,family='안동엄마까투리'))
findidbutton.grid_configure(row=0,column=0)
showidbutton=Button(window,text='ID 보기',command=showid,width=10,height=5,font=font.Font(size=20,family='안동엄마까투리'))
showidbutton.grid_configure(row=0,column=1)
findartistbutton=Button(window,text='작곡가 검색',command=findartist,width=10,height=5,font=font.Font(size=20,family='안동엄마까투리'))
findartistbutton.grid_configure(row=1,column=0)
ppbutton=Button(window,text='PP 계산기',command=calpp,width=10,height=5,font=font.Font(size=20,family='안동엄마까투리'))
ppbutton.grid_configure(row=1,column=1)
window.mainloop()