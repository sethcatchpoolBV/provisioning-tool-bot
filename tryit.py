from jira import JIRA
import json
import os
import time
import requests
import cgi
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

ldap_name  = 'ksiaulys'
ldap_pwd  = 'nesakysiu123!'
passkey = 'Xlf8G5108wADIS43a5irWi0y51Kv8Ph3' # for ICEBREAKER API

# locale lists of strings
us_list = ["NA", "US", "tryitsampling.com"]
uk_list = ["UK", "uk.tryitsampling.com"]
de_list = ["DE", "de.tryitsampling.com"]
fr_list = ["FR", "fr.tryitsampling.com"]

# globals
clientName = ""
apiKey = ""
encKey = ""
vendor = ""
locale = ""
portal = ""
cluster = ""

# jira session
options = {"server": "https://bits.bazaarvoice.com/jira"}
jira = JIRA(options,basic_auth=(ldap_name, ldap_pwd))

# Function to do all the necessary stuff in Jira, like assign to owner and add comment
def jiraEnd(issue):
    comment = "Hi, your ticket was processed by the bot. Have a good day!"
    jira.add_comment(issue, comment)
    owner = issue.fields.creator.key
    issue.update(assignee={'name': owner})
    jira.transition_issue(issue, '101')

# Function to reset global variables
def resetGlobals():
    global clientName
    global apiKey
    global encKey
    global vendor
    global locale
    global portal
    global cluster
    
    clientName = ""
    apiKey = ""
    encKey = ""
    vendor = ""
    locale = ""
    portal = ""
    cluster = ""

def getURL(locale):
    if locale == "en_US":
        return "https://tryitsampling.com"
    if locale == "en_GB":
        return "https://uk.tryitsampling.com"

# selenium script to check the checkbox
def tryItSampling(locale):
    flag = False
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(executable_path='C:/Users/karolis.siaulys/Desktop/Tadas tool/chromedriver_win32/chromedriver.exe',chrome_options=options)
        driver.get(getURL(locale))
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/section[1]/aside[1]/section/p/button')))
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/section[1]/aside[1]/section/p/button").click()
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_email')))
        driver.find_element(By.ID, "login_email").send_keys(ldap_name)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_password')))
        driver.find_element(By.ID, "login_password").send_keys(ldap_pwd)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_form"]/p/button')))
        driver.execute_script('arguments[0].click();',element)
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="nav"]/div[2]/ul/li[5]/a')))
        driver.execute_script('arguments[0].click();',element)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="nav"]/div[2]/ul/li[5]/ul/li[1]/a')))
        driver.execute_script('arguments[0].click();',element)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="item-list_filter"]/label/input')))
        print('"'+vendor+'"')
        driver.find_element(By.XPATH, '//*[@id="item-list_filter"]/label/input').send_keys(vendor)
        # element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="item-list_filter"]/span/button')))
        # driver.execute_script('arguments[0].click();',element)
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="item-list"]/tbody/tr/td[2]/a')))
        driver.execute_script('arguments[0].click();',element)
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@value='"+clientName+"']")))
        driver.execute_script('arguments[0].click();',element)
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="register_form"]/article[2]/section/div/div/button')))
        driver.execute_script('arguments[0].click();',element)
        driver.close()
        flag = True
    finally:
        return flag

# Function to run CMD command to upload new file
def uploadConfig(config):
    upload = 'goldrush-config -c '+config+' -e production -u '+config+'_config.json -n "'+clientName+': uploaded by bot."'
    os.system(upload)

#Function to form CV2 data
def appendNewDataCV2(locale, config):
    confNoBrands = '"brands": {'+clientName+': {"public_company_name": '+clientName+',"bv_client_id": '+clientName+',"deployment_zone": "ProductSampling","bv_api_prod": "//display.ugc.bazaarvoice.com/static/'+clientName+'/ProductSampling/'+locale+'/bvapi.js","bv_api_passkey_production": '+apiKey+',"encoding_key": '+encKey+'}}'
    confBrands = '{"'+clientName+'": {"public_company_name": "'+clientName+'","bv_client_id": "'+clientName+'","deployment_zone": "ProductSampling","bv_api_prod": "//display.ugc.bazaarvoice.com/static/'+clientName+'/ProductSampling/'+locale+'/bvapi.js","bv_api_passkey_production": "'+apiKey+'","encoding_key": "'+encKey+'"}}'
    with open("C:/Users/karolis.siaulys/Desktop/Tadas tool/"+config+"_config.json") as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
    if not data.get(clientName):
        if not data.get("brands"):
            y = json.loads(confNoBrands)
            data.update(y)
            with open('C:/Users/karolis.siaulys/Desktop/Tadas tool/'+config+'_config.json', 'w') as f:
                json.dump(data, f, indent=4)
        else:
            y = json.loads(confBrands, object_pairs_hook=OrderedDict)
            data["brands"].update(y)
            with open('C:/Users/karolis.siaulys/Desktop/Tadas tool/'+config+'_config.json', 'w') as f:
                json.dump(data, f, indent=4)

def getConfig(locale):
    if locale == "en_US":
        return "tryit"
    if locale == "en_GB":
        return "tryitemea"
    if locale == "de_DE":
        return "tryitde"
    if locale == "fr_FR":
        return "tryitfr"

# Function to run CMD command to donwload new file
def downloadConfig(config):
    os.system('goldrush-config -c '+config+' -e production -d '+config+'_config.json')
    try:
        f = open("C:/Users/karolis.siaulys/Desktop/Tadas tool/"+config+"_config.json")
    except IOError:
        return False
    finally:
        f.close()
    return True

# Function to process all the data that is parsed into config file
def processData():
    localeSplit = locale.split("&")
    i = 1
    ok = True
    while i < len(localeSplit): 
        print "Appending " + localeSplit[i] + " settings"
        config = getConfig(localeSplit[i])
        if downloadConfig(config):
            appendNewDataCV2(localeSplit[i], config)
            uploadConfig(config)
            if localeSplit[i] in ["en_GB","en_US"]:
                print "Portal checkbox checking"
                if not tryItSampling(localeSplit[i]):
                    ok = False
        i+=1
    return ok

# Function to do all the necessary stuff in Jira, like assign to me and start progress
def jiraStart(issue):
    issue.update(assignee={'name': ldap_name})

# Function to check the api key
def checkAPIKey():
    icebreaker = requests.get('https://prod-icebreaker.nexus.bazaarvoice.com/api/v1/keys/'+apiKey+'?passkey='+passkey+'&client.name='+clientName+'&application.name=Product Sampling')
    if icebreaker.status_code == 200:
        print "API Key Passed!"
        return True
    else:
        print "API Key Failed!"
        return False

def generateApiKey():
    global apiKey
    global displayCode
    global cluster
    print displayCode
    print cluster
    url = 'https://bazaar-icebreaker-external.nexus.bazaarvoice.com/api/v1/keys/'+ clientName +'?validateClient=false&passkey='+ passkey
    print(url)
    postObj = { "createdBy": "tpetrauskas",
            "internal": True,
            "developer": "karolis.siaulys@bazaarvoice.com",
            "access-prr": "READ_WRITE",
            "access-qa": "READ_WRITE",
            "access-stories": "READ_WRITE",
            "access-authors": "READ_WRITE",
            "ipAccessEnabled": False,
            "displayHiddenFieldsEnabled": True,
            "inappropriateAccessEnabled": False,
            "userEmailAccessEnabled": False,
            "syndicatedContentAccessEnabled": False,
            "nonApprovedContentAccess": "FULL",
            "comment": "Sampling API Key",
            "application": { "name": "Product Sampling",
                             "description": "Internal sampling API key"},
            "environment": "prod",
            "displayCode": displayCode,
            "prrCluster": cluster,
            "status": "active"
          }
    headers = {'content-type': 'application/json'}
    apiKeyRes = requests.post(url, data=json.dumps(postObj), headers=headers)
    apiKey = apiKeyRes.text.split(',')[0].split(':')[-1].replace(" ","").replace('"','')
    print ("API KEY USE: "+ apiKey)
    if apiKey != "":
        textSearchUrl = "https://bazaar-icebreaker-external.nexus.bazaarvoice.com/api/v1/client/"+clientName+"?passkey="+ passkey
        putObj = {"enable-full-text-search": True}
        textSearch = requests.put(textSearchUrl, data=json.dumps(putObj), headers=headers)
        if textSearch.status_code == requests.codes.ok:
            return True
        else:
            return False

# Function to check the given data from Jira
def checkData(issue):
    if apiKey != "":
        if not checkAPIKey():
            return False
        else:
            return True
    else:
        if generateApiKey():
            return True
        else:
            return False

def parseData(issue):
    global clientName
    global apiKey
    global encKey
    global vendor
    global portal
    global locale
    global displayCode
    global cluster

    summary = issue.fields.summary.split(': ')
    clientName = summary[0].replace(" ", "")

    if clientName != "":
        clientNameCheck = requests.get('https://rosetta.prod.us-east-1.nexus.bazaarvoice.com/search/1/display?client='+ clientName)
        fixClientName = clientNameCheck.content.split(",")
        for i in fixClientName:
            if '"client":' in i:
                clientName = i.replace('"client":', "").replace('"',"")
            if '"cluster":' in i:
                cluster = i.replace('"cluster":', "").replace('"',"")

        bhive = requests.get('http://rosetta.prod.us-east-1.nexus.bazaarvoice.com/search/1/display?client='+clientName)
        if (bhive.content.find('platform":"cv2"') == -1):
            return False # not CV2 client
    else:
        addComment('Bot could not find client name in ticket summary, please follow guidlines.')

    description = issue.fields.description
    descByLines = description.splitlines()
    locale = ""
    for i in descByLines:
        if "*API key:*" in i:
            apiKey = i.replace("*API key:*", "").replace(" ","")
            apiKey = "".join(apiKey.split())
        if "*Vendor email address:*" in i:
            vendor = i.replace("*Vendor email address:* ", "")
        if "*TryIt Portal:*" in i:
            portal = i.split(" ")
            portal = i.replace("*TryIt Portal:*","")
            portal = portal.replace(" ","")
            if bool([i for i in us_list if(i in portal)]):
                locale += "&en_US"
            if bool([i for i in uk_list if(i in portal)]):
                locale += "&en_GB"
            if bool([i for i in de_list if(i in portal)]):
                locale += "&de_DE"
            if bool([i for i in fr_list if(i in portal)]):
                locale += "&fr_FR"
    rosseta = requests.get('https://rosetta.prod.us-east-1.nexus.bazaarvoice.com/search/1/display?client='+clientName)
    displayCode = rosseta.content.split(",")[0].replace('[{"code":"', '').replace('"', '')
    rosseta = requests.get('https://rosetta.prod.us-east-1.nexus.bazaarvoice.com/package/1/site/'+displayCode+'/prr?decode=true')
    position = rosseta.content.find('"encodingKey"')
    encKey = rosseta.content[position:position+1000].split(",")[0].replace('"','').replace("encodingKey:","")
    return True

# Function to start the process of solving an issue
def processIssue(issue):
    resetGlobals()
    print "Got a job to process ticket: " + issue.key
    print "Parsing ticket data"
    if parseData(issue):
        print "Checking ticket data"
        if checkData(issue):
            print "Jira start"
            jiraStart(issue)
            print "Processing Data"
            if processData():
                print "Close Jira"
                jiraEnd(issue)
            else:
                print "Needs a hand"
        else:
            print "Data check failed."
    else:
        print "Client is PRR!"

# Function to monitor issues assigned to MetaUser: sampling
def monitorQueue():
    queue = jira.search_issues('project = CPRO AND assignee = metauser-sampling AND status not in ("Engineering Q", Done, Closed, Resolved, Completed) ORDER BY created DESC')
    for i in range(len(queue)):
        if queue[i].key != "CPRO-2374":
            processIssue(queue[i])
    print "Waiting for next round..."
    time.sleep(3600) # sleep for an hour
    monitorQueue() # and back to work

monitorQueue()