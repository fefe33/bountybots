#crawls a webpage for forms and links **(within a specifies scope), creating a tree like structure for endpoints and their respective form parameters
import time, argparse, json
#selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By

class crawler:
    #construct the crawler object
    # url = the base url for the crawler to start crawling
    # scope = all sites and keywords that a given url must
    def __init__(self, browser:str, url:str, scope:list, noscope:list):
        if browser.lower() == 'chrome':
            self.driver = webdriver.Chrome()
        elif browser.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        self.scope = scope
        self.noscope = noscope
        self.results = [] 
        self.endpoints = [url]  # this holds all endpoints, that are to be and have been visitted. 
        self.visited = []       # holds all previously visited URLs
        self.iter = 0           # this is the index of the current endpoint (relative to self.endpoints)

    #change the browsers current location
    def change_url(self,url):
        #dont bother validating if its in scope. this is only ever called using urls from self.endpoints
        if url not in self.visited:
            #if it hasnt, add it to the 'visited' array, then navigate to the URL
            self.visited.append(url)
            self.driver.get(url)
        else:
            return False
        print('navigating to ', url)
        return True

    #takes a url, checks if it has already been indexed. if false, adds it to self.endpoints if its 
    def add_endpoint(self,url):
        #check that the url hasnt already been added
        if url in self.visited:
            return False

        #iterate through the domains listed as 'in scope', checking any of them show up in the url. if not, return false    
        in_scope = False
        #check in scope kws, domains, urls
        for i in self.scope:
            if i in url: 
                in_scope = True
                break
        #check out of scope kws, domains, urls
        for i in self.noscope:
            if i in url:
                in_scope = False

        
        #if the url is in scope, append it to endpoints
        if in_scope:
            print('adding url ', url)
            self.endpoints.append(url)
        
        
    #run the bot using the given scope
    def run(self):
        #if the current iteration is greater than the number of urls in the self.endpoints array
        if self.iter >= len(self.endpoints):
            #print the results and quit
            self.driver.quit()
                
        print('endpoint: ',self.iter)
        #go to the provided url using change_url method
        try:
            if self.change_url(self.endpoints[self.iter]):
                #pull all the anchor tags from the page
                a_tags = self.driver.find_elements(By.TAG_NAME, 'a')

                #add all the hrefs to self.endpoints using the add_endpoint method
                for i in a_tags:
                    if i.get_attribute('href')!=None:
                        self.add_endpoint(i.get_attribute('href'))
                
                #get all the forms on the page
                forms = self.driver.find_elements(By.TAG_NAME, 'form')
            else:
                #if the url fails to open. increment self.iter and do the recursive thing
                print('could not open URL')
                self.iter += 1
                self.run()
        except:
            #on error return gracefully quit
            self.driver.quit()
            return            
        #get the forms
        forms = self.driver.find_elements(By.TAG_NAME, 'form')
        #if there are any, analyze them
        if len(forms) > 0:
            #exit with error for now
            print('more than one form detected on page.\n')
            #counter for the forms
            f_count = 0
            #create the results object for this endpoints
            results_EP = {'title':self.driver.title, 'url':self.endpoints[self.iter], 'forms':[]}
            #iterate through all the forms
            for form in forms:
                results = {}
                #save the form method and action to the results
                results['method'] = form.get_attribute('method')
                results['endpoint'] = form.get_attribute('action')
                results['parameters'] = dict()
                #get all buttons, inputs, and select/options
                inputs = form.find_elements(By.TAG_NAME,'input')
                text_areas = form.find_elements(By.TAG_NAME,'textarea')
                selects = form.find_elements(By.TAG_NAME, 'select')
                fieldsets = form.find_elements(By.TAG_NAME, 'fieldset')

                #separate out all of the inputs, grouping them by name into the results
                for i in inputs:
                    if i.get_attribute('type') != 'hidden':
                        results['parameters'][i.get_attribute('name')] = {'type':i.get_attribute('type')} #name and datatype of given param 
                    else: 
                        results['parameters'][i.get_attribute('name')] = {'type':i.get_attribute('type'), 'value':i.get_attribute('value')} #name and datatype of given param 
                   
                try:
                    for i in textareas:
                        #save stats about these
                        results['parameters'][i.get_attribute('name')] = {'type':'text(box)'}
                except:pass
                
                for i in selects:
                    try:
                        select_options = i.find_elements(By.TAG_NAME, 'option')
                        #take all of the names and write them to the results dictionary (sorting by name )
                        results[i.get_attribute('name')] = {'type':'select/option','values': [x.get_attribute('value') for x in select_options]}
                    except:
                        continue
                
                for i in fieldsets:
                    try:
                        select_options = i.find_elements(By.TAG_NAME, 'input')
                        results['parameters'][i.get_attribute('name')] = {'type': 'fieldset', 'values':[x.get_attribute('value') for x in select_options]}
                    except:continue
                # append the form object to the forms array in the results dictionary
                results_EP['forms'].append(results)
                self.results.append(results_EP)
                # 
                
        #once the forms have been parsed (if any are present), iterate and recurse
        self.iter+=1
        self.run()
        #that should be it for now

        #return the results as json
        def get_results_json():
            if self.results:
                output = json.dumps({'origin':self.endpoints[0], 'totalVisited':self.visited, 'results':self.results})
                return output




#now handle arguments
parser = argparse.ArgumentParser(
            description='a selenium bot that crawls websites for forms',
            epilog='designed and written by someone somewhere in a galaxy far far away'
        )

parser.add_argument('-b','--browser', type=str, nargs=1, choices=['chrome', 'firefox'], required=True, help='the browser to use (chrome or firefox)')
parser.add_argument('-u', '--url', type=str, nargs=1, required=True, help='the initial url for the bot to scan')
parser.add_argument('-is','--inscope', nargs = '*', required=True, help='domains, keywords, and urls that the bot should consider in scope')
parser.add_argument('-ns', '--noscope', nargs='*', type=str, required=True, help='domains,keywords, and urls that the bot should consider out of scope.')
parser.add_argument('-o', '--out', nargs=1, type=str,help='the name of the output file or fifo to write the output to (as json)')
args = parser.parse_args()
browser = args.browser[0]
url = args.url[0] 
inscope = args.inscope
noscope = args.noscope
print('in scope: ', inscope,'\nout of scope: ', noscope)
#init with a random site
crawlbot = crawler(browser,url, inscope,noscope)
crawlbot.run()
print(crawlbot.results)
#try to get the out file
try:
    if args.out:
        file = args.out
        if not file.endswith('.json'):
            file = file+'.json'
        with open(file, 'w') as f:
            file.write(crawlbot.get_results_json())
    else:
        pass
    
except:pass
