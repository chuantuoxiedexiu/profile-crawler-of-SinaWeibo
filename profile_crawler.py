
import requests
import time
import json
import re
import os
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def get_profile_page():
    #content contains ID list
    content=['1000010000','1000010003']
    user_agent={'User-agent':'spider'}
    s = requests.Session()
    for i in range(0,len(content)):
        ID=content[i].strip('\n')
        url='http://www.weibo.com/u/'+ID
        print i,'/',len(content),ID
        #SUB is one key in cookie
        try:
            res=s.get(url,cookies={'SUB':'_2AkMvnYHZdcPhrAZXnPkQzGnhaYRH-jycSOgvAne4JhMyAxgv7nExqSVFXD9BUcx5oZy01um07nYYpXXqrg..'})
        except Exception:
            time.sleep(10)
            res=s.get(url,cookies={'SUB':'_2AkMvnYHZdcPhrAZXnPkQzGnhaYRH-jycSOgvAng67JhMyAxgv7nExqSVFXD9BUcx5oZy01um07nYYpXXqrg..'})
        con=res.text.encode('utf8')
        f=open(base_dir+'main_page/'+ID+'.html','w')
        f.write(con)
        f.close()
        b=re.findall("\['page_id'\]='(\d+)'",con)
        try:
            page_id=b[0]
        except IndexError:
            f=open(base_dir+'unvalid_url_list.txt','a')
            f.write(ID+'\n')
            f.close()
            continue
        con=con.replace('\\"','"').replace('\\/','/')
        a=re.findall('(<div class="pf_photo".+?</div>)',con)
        b=re.findall('(bluev/verify/index)',a[0])
        if len(b)==1:
            url='http://www.weibo.com/'+ID+'/about'
        else:
            url='http://www.weibo.com/p/'+page_id+'/info?mod=pedit_more'
        try
            res=s.get(url,cookies={'SUB':'_2A251acXQDeRxGeNI71MU8CzPzjWIHXVWwsAYrDV8PUNbmtBeLUv6kW8OEDjwFv_wTd-MNjw7-qdqQuiVkA..'})
        except requests.ConnectionError:
            time.sleep(3)
            res=s.get(url,cookies={'SUB':'_2A2511M-ADeRxGeNI71MU8CzPzjWIHXVWddZIrDV8PUNbmtBeLXTdkW-ghVQdQhSAO90M1mj4A0oNM7ur2g..'})
        con=res.text.encode('utf8')
        if len(b)==0 and not re.findall('(基本信息)',con):
            print 'cookie is failure'
            break
        f=open(base_dir+'profile_page/'+ID+'.html','w')
        f.write(con)
        f.close()
        time.sleep(1)

def all_profile():
    filenames=os.listdir('./profile_page/')
    #filenames=['5694223296.html']
    total=len(filenames)
    for each in range(0,total):
        print each,'/',total
        ID=filenames[each].strip('.html')
        get_profile(ID)

def get_profile(ID):
    f=open('./profile_page/'+ID+'.html')
    con=f.read()
    f.close()
    con=re.findall('<script>FM.view\((.+?)\)</script>',con)
    result=''
    for e in con:
        try:
            f=eval(e)['html']
            f=f.replace('\\"','"').replace('\\t','').replace('\\n','').replace('\\/','/').replace('\\r','')
            result+=f
        except KeyError:
            pass
    con='<html><head><meta charset="utf-8"></head><body>'+result+'</body></html>'
    con=con.encode('utf-8')
    tree=etree.HTML(con)
    profile={}
    profile['微博达人']='否'
    profile['微博会员']='否'
    profile['微博认证']='否'
    photo=tree.xpath('//div[@class="PCD_header"]//div[@class="pf_photo"]//img')[0].get('src')
    profile['头像']=photo
    #是否是微博达人
    daren=tree.xpath('//div[@class="PCD_header"]//div[@class="pf_photo"]//em[@class="W_icon icon_pf_club"]')
    if len(daren)==1:
        #print u'微博达人'
        profile['微博达人']='是'
    huiyuan=tree.xpath('//div[@class="PCD_header"]//div[@class="pf_username"]//a[@href="http://vip.weibo.com/personal?from=main"]')
    if len(huiyuan)==1:
        #print u'微博会员'
        profile['微博会员']='是'
    renzheng=tree.xpath('//div[@class="PCD_header"]//div[@class="pf_photo"]//a[@href="http://verified.weibo.com/verify"]')
    if len(renzheng)==1:
        #print u'微博认证'
        profile['微博认证']='是'
    head=tree.xpath('//div[@class="PCD_header"]//div[@class="pf_intro"]')[0].get('title')
    #print head_intro.encode('GBK','ignore')
    if head==None:
        profile['主页简介']='没有填写个人简介'
    else:
        profile['主页简介']=head
    #粉丝、微博、好友
    #div class="PCD_counter"
    a=tree.xpath('//div[@class="PCD_counter"]//td/a')
    #print len(a)
    for b in a:
        c=b.xpath('.//text()')
        #print c[0],c[1]
        profile[c[1]]=c[0]
    #勋章、等级、会员
    profile['勋章信息']=[]
    profile['等级信息']=''
    profile['会员信息']={}
    #div class="PCD_person_detail"
    a=tree.xpath('//div[@class="PCD_person_detail"]')
    for b in a:
        title=b.xpath('.//h2//text()')[0]
        #print '\n',title
        if title=='勋章信息':
            c=b.xpath('.//li[@class="bagde_item"]/a')
            for d in c:
                profile['勋章信息'].append(d.get('title'))
        if title=='等级信息':
            c=b.xpath('.//a')
            profile['等级信息']=c[1].get('title')
        if title=='会员信息':
            c=b.xpath('.//div[@class="vip_info line S_line1"]/p')
            for d in c:
                e=d.xpath('.//text()')
                f=''.join(e)
                g=f.split('：')
                #print g[0],g[1]
                profile['会员信息'][g[0]]=g[1]
    #基本信息、工作信息、标签信息
    profile['基本信息']={}
    profile['联系信息']={}
    profile['工作信息']=[]
    profile['教育信息']=[]
    profile['标签信息']=[]
    #div class="PCD_text_b PCD_text_b2"
    a=tree.xpath('//div[@class="PCD_text_b PCD_text_b2"]')
    for b in a:
        title=b.xpath('.//h2//text()')[0]
        #print title
        if title=='基本信息':
            c=b.xpath('.//ul[@class="clearfix"]/li[@class="li_1 clearfix"]')
            for d in c:
                name=d.xpath('.//text()')
                for ee in range(len(name)):
                    name[ee]=name[ee].strip()
                name=''.join(name)
                value=name.split('：')
                #print value[0],'-->',value[1]
                profile['基本信息'][value[0]]=value[1]
        if title=='联系信息':
            c=b.xpath('.//ul[@class="clearfix"]/li[@class="li_1 clearfix"]')
            for d in c:
                name=d.xpath('.//text()')
                for ee in range(len(name)):
                    name[ee]=name[ee].strip()
                name=''.join(name)
                value=name.split('：')
                #print value[0],'-->',value[1]
                profile['联系信息'][value[0]]=value[1]
        if title=='工作信息':
            c=b.xpath('.//ul[@class="clearfix"]/li[@class="li_1 clearfix"]')
            for d in c:
                profile['工作信息'].append([])
                edu=d.xpath('.//span[@class="pt_title S_txt2"]//text()')[0]
                edu=edu.strip('：')
                #print edu
                
                school=d.xpath('.//span[@class="pt_detail"]//text()')
                for ee in range(len(school)):
                    school[ee]=school[ee].strip()
                while '' in school:
                    school.remove('')
                for each in school:
                    #print each
                    profile['工作信息'][-1].append(each)
        if title=='教育信息':
            c=b.xpath('.//ul[@class="clearfix"]/li[@class="li_1 clearfix"]')
            for d in c:
                profile['教育信息'].append({})
                edu=d.xpath('.//span[@class="pt_title S_txt2"]//text()')[0]
                edu=edu.strip('：')
                #print edu
                profile['教育信息'][-1]['学历']=edu
                school=d.xpath('.//span[@class="pt_detail"]//text()')
                for ee in range(len(school)):
                    school[ee]=school[ee].strip()
                while '' in school:
                    school.remove('')
                profile['教育信息'][-1]['详情']=[]
                for each in school:
                    #print each
                    profile['教育信息'][-1]['详情'].append(each)
        if title=='标签信息':
            c=b.xpath('.//ul[@class="clearfix"]/li//span[@class="pt_detail"]//a//text()')
            for ee in range(len(c)):
                c[ee]=c[ee].strip()
            while '' in c:
                c.remove('')
            for ee in c:
                #print ee
                profile['标签信息'].append(ee)
    f=open('./profile/'+ID+'.txt','w')
    profile=json.dumps(profile,ensure_ascii=False,indent=4)  
    f.write(profile+'\n')
    f.close()

if __name__=='__main__':
    print 'begin'
    get_profile_page()
    all_profile()
    print 'end'





























