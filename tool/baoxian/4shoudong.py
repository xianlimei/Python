'''
采集手动和自动
'''
import kl_http,kl_db,os,json,kl_log
from postdata import postdata
http=kl_http.kl_http()
log=kl_log.kl_log('brand')
db=kl_db.mysql({
            'host':'localhost',
            'user':'root',
            'passwd':'adminrootkl',
            'db':'qiche',
            'prefix':'kl_',
            'charset':'utf8'
        })
http.autoUserAgent=True
http.setheaders('''\
Host:www.epicc.com.cn
Origin:http://www.epicc.com.cn
Referer:http://www.epicc.com.cn/ecar/proposal/normalProposal
User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36
X-Requested-With:XMLHttpRequestContent-Type: application/x-www-form-urlencoded\
''')
try:
    #查询手动/自动
    url='http://www.epicc.com.cn/ecar/car/carModel/getCarModelFromJYDB'
    brandlist=db.table('3paiqiliang').where({'status':0}).order('id asc').select()
    brandlist=brandlist.fetchall()
    for i in brandlist:
        #查询排气量
        tjdata=postdata['shoudong'].replace('[GROUPID]',i['groupId'])
        r=http.posturl(url,tjdata)
        content=''
        if not http.lasterror:
            content=r.read().decode()
        else:
            print(http.lasterror)
        if content:
            try:
                info=json.loads(content)
                if info['head']['errorCode']=='91':
                    db.table('3paiqiliang').where({'id':i['id']}).save({'status':2})
                    print('%s not result!'%i['groupId'])
                else:
                    xhlist=info['body']['Element']['parents']['FcParent']
                    addres=True
                    for a in xhlist:
                        a['brandId']=i['brandId']
                        a['familyId']=i['familyId']
                        a['groupId']=i['groupId']
                        a['engineDesc']=i['engineDesc']
                        result=db.table('4shoudong').where(a).count()
                        if result<=0:
                            res=db.table('4shoudong').add(a)
                            if res<=0:
                                addres=False
                            else:
                                print('adding %s'%a)
                    if addres:
                        db.table('3paiqiliang').where({'id':i['id']}).save({'status':1})
            except Exception as e:
                log.write('add %s  error!'%(i['groupId']))
                print(e)
except Exception as e:
    print(e)
os.system('pause')