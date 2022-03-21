#!/usr/bin/env python3
import requests
import pprint
import json
import os.path
#from fake_useragent import UserAgent
#from requests.exceptions import ConnectionError



target_websites = {
  #"https://www.letemps.ch": "Le Temps",
  "https://www.lemonde.fr": "Le Monde", 
  #"https://www.blick.ch": "Blick",
  #"https://wikistrike.com": "Wikistrike",  
  #"https://www.usinenouvelle.com/": "Usine nouvelle"
}

cache_directory = "sellers_json/"   # where to put sellers.json files

# Sellers that do not give sellers.json files
black_list = ['ligadx.com', 'coxmt.com', 'tidaltv.com', 'aolcloud.net', 'adtech.com', 'adtech.com', '4aolcloud.net', 'advertising.com', 'somoaudience.com', 'mediamath.com', 'memevideoad.com', 'yldbt.com', 'yume.com', 'Freewheel.tv', 'aniview.com', 'sovrn.com', 'exponential.com', 'tribalfusion.com', 'sublime.xyz', 'facebook.com', 'tech.convergd.com', 'valueclickmedia.com', 'dyntrk.com', 'Advertising.com', 'aerserv.com', 'vindicosuite.com', 'ssp.ynxs.io', 'mobileadtrading.com', 'streamrail.net', '360yield.com', 'ad6media.fr', 'adleave.com', 'adnx.com', 'adrock.tv', 'advangelists.com', 'adwidecenter.com', 'amazon-adsystem.com', 'atemda.com', 'ayads.co', 'bidtellect.com', 'bizzclick.com', 'bizzclick.net', 'brightroll.com', 'btrll.com', 'c1exchange.com', 'carambo.la', 'cmcm.com', 'emodoinc.com', 'imonomy.com', 'inner-active.com', 'ividence.com', 'kumma.com', 'motionspots.com', 'natiiveads.com', 'nativeads.com', 'onepath.ai', 'optimatic.com', 'playtem.com', 'powerlinks.com', 'purch.com', 'rtbdemand.com', 'rubicon.com', 'sabio.us', 'servebom.com', 'smartyads.com', 'switch.com', 'technorati.com', 'truex.com', 'truvidplayer.com', 'ucfunnel.com', 'videoflare.com', 'webeyemob.com', 'xapads.com', 'dailymotion.com', 'azeriondigital.com', 'ads.adasiaholdings.com', 'rtk.io', 'runative-syndicate.com', 'Contextweb.com ', 'vdopia.com']

#-------------------------------------------------------
# get a list of a sellers from an ads.txt
def get_ads_txt(url):
    f = requests.get(url)
    ads_list = []
    for line in f.text.splitlines(): 
        if not line.strip(): continue
        elif line[0] == "#": continue
        elif line.startswith('subdomain'): continue     # ignore "subdomain" clauses.
        else:
            cleanded_line = line.split("#")[0].strip()
            ads_list.append(cleanded_line.split(","))
    return ads_list
#print(get_ads_txt("https://www.lemonde.fr/ads.txt"))
#-------------------------------------------------------
def generate_site_ads_dict(sites):
    site_ads_dict = {}
    #for site in sites: site_ads_dict[site] = get_ads_txt(site+"/ads.txt") + get_ads_txt(site+"/app-ads.txt")
    for site in sites: site_ads_dict[site] = get_ads_txt(site+"/ads.txt")
    return site_ads_dict
#-------------------------------------------------------
def get_seller_json_file(seller):
    fname = cache_directory + seller
    if os.path.isfile(fname):
        return 0
    
    #ua = UserAgent()
    try:
        url     = 'https://'+seller+'/sellers.json'        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        # headers = {'User-Agent': ua.random}
        r = requests.get(url, allow_redirects=True, headers=headers) 
        if r.status_code > 400: return 1
        open(fname, 'wb').write(r.content)
        return 0
    except requests.exceptions.ConnectionError as e:
        #print("requests.exceptions.ConnectionError")
        return 1

#-------------------------------------------------------
def get_seller_json(seller):
    if get_seller_json_file(seller) == 1: return None
    with open(cache_directory+seller) as json_file:
        if not json_file.read().strip()[0] == '{': return None
    with open(cache_directory+seller) as json_file:
        data = json.load(json_file)
        return data
    #url = 'https://'+seller+'/sellers.json'
    #params=''
    #try:
        #resp = requests.get(url=url, params=params)
        #if resp.status_code > 400: return None
        #data = resp.json()
        #return(data)
    ##except requests.exceptions.ConnectionRefusedError as e:
    #except requests.exceptions.ConnectionError as e:
        #pass
#-------------------------------------------------------
def get_seller_dict(seller):
    data = get_seller_json(seller)
    if data is None: return None
    seller_dict = {}
    for i in data["sellers"]:
        if 'name' in i and 'seller_id' in i:
            seller_dict[str(i["seller_id"])] = i["name"]
        elif 'name' in i and 'seller-id' in i:
            seller_dict[str(i["seller-id"])] = i["name"]

    #seller_dict = {i["seller_id"]: i["name"] for i in get_seller_json(seller)["sellers"]}
    return seller_dict
#-------------------------------------------------------
def get_reseller(seller, seller_id):
    seller_dict = get_seller_dict(seller)
    if seller_dict is None: 
        black_list.append(seller)
        return ">>> NO sellers.json RETURNED BY PROVIDER"
    if str(seller_id) in seller_dict:
        return seller_dict[str(seller_id)]
    return ">>> UNKNOWN SELLER ID"
        
#-------------------------------------------------------
def get_resellers(target_websites):
    site_ads_dict = generate_site_ads_dict(target_websites)
    for target_website in target_websites:
        print (target_website)
        sellers = site_ads_dict[target_website]
        #print('sellers to study:', sellers)
        for seller in sellers:
            #print('--', seller, '--')
            if len(seller) < 2: continue
            seller_name                   = seller[0]
            seller_id_for_target_websites = seller[1].strip()
            seller_type                   = seller[2].strip()
            if seller_name in black_list: continue
            reseller = get_reseller(seller_name, seller_id_for_target_websites)
            print("\t"+'{0:<20} {1:<40} {2:<10} {3:>30}'.format(seller_name, seller_id_for_target_websites, seller_type, reseller))
            #if(seller_type == "RESELLER"): print(get_reseller(reseller))
            

#-------------------------------------------------------
def main():
    #pprint.pprint(generate_site_ads_dict(target_websites))
    #pprint.pprint(get_seller_dict("improvedigital.com") )
    #print( get_reseller("improvedigital.com", 1939) )  # normal sellers.json
    #print( get_reseller("spotxchange.com", 262124) )   # no sellers.json data
    #for i in [745378, 745362, 745378, 1142945, 1143393, 67945]:  print("freewheel.tv", i, '-->',  get_reseller("freewheel.tv", i ))
    #for i in [101760, 100600, 101760]:  print("districtm.io", i, '-->',  get_reseller("districtm.io", i ))
    #print( get_reseller("nsightvideo.com", 31894684) ) # seller-id instead of seller_id in sellers.json
    #print( get_reseller("xad.com", 958) )             # 403
    #print( get_reseller("ayads.co", 1389) )   # redirects to a login page    
    
    get_resellers(target_websites)
    print('Blacklist\n', black_list)
#-------------------------------------------------------

if __name__ == "__main__":
    main()
