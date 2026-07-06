"""
Script: AutoDoc.py
Version: 0.1
Author: Dalamar Kanan
    Project: UO-Copilot - AutoDoc
    
Contact: 
    https://discord.gg/2NmXqQ5QAk (@RE Dev)
    Dalamar#2877
    cesare.montresor@gmail.com 
    
Abstract:
    This script produce UO-Copilot API documentation (only HTML atm) by reading the *Scripting API Data* contained in Config/AutoComplete.json
    The AutoComplete.json file it produced by the counterpart of this script inside UO-Copilot engine:
    https://github.com/UltimaTools/UO_Copilot/blob/GTK-64bit/uo_copilot/AutoDoc.cs 
    

Classes:
    HTML:
        - Containes *all the HTML* code and functions as a theme template. HTML is used by AutoDocHTML and can be used directly.
        - This class can be copied/replaced/customized to alter the structure of the page and make custom Themes.
        - However, before changing this class is adivced to first attempt customization via css (much easier).
        - The standard generated page includes by default also a main.css and a main.js.
        - HTML class don't use *complex object* in input, just *simple string*.

    AutoDoc:
        - Loads the Config/AutoComplete.json and provide convenience methods to query and filter the data.
        - AutoDoc is used by AutoDocHTML and can be used directly.
        - AutoDoc produce *complex object* as result of the json structure.

    AutoDocHTML: 
        - AutoDocHTML uses both AutoDoc and HTML classes.
        - Pull the data as *complex objects* from AutoDoc and combine them into *simple strings* give it to the HTML class to decorate.
        - Return elaborate HTML Chunks, with data.
        - AutoDocHTML shoudn't contain any *actual HTML*

Main:
    - Reperents the entry point of this script, the first function that Run when you Run the script. ( see the end of this file for details )
    - The code in the main() function should be minimal, ideally only 2 lines:
        adio=AutoDocHTML(doc_path)
        adio.MakeDocumentation()
        

"""

import os
import json
import re
import sys

    

def main():
    ## SETTINGS
    
    debug=True

    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Write to your Script/Docs/ folder
    output_path = os.path.join(script_dir, "api") + os.sep
    api_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(script_dir, "Config", "AutoComplete.json")
    
    ## RUN 
    
    # setup AutoDocHTML to a test path
    adhtml=AutoDocHTML(output_path, api_path)
    version = adhtml.DocVersionHTML()
    
    # generates the main menu from the list of classes
    menu = adhtml.MainMenuHTML()
    index_html = HTML.LeftRightPage(version+menu,"","UO-Copilot API Documentation")
    adhtml.WriteToFile("index.html".format(), index_html)
    
    # generates doc page for the Player class ( usefull for testing ) 
    # player_html = adhtml.ClassHTML("Player")
    # player_html = HTML.BasePage(player_html,"Player - UO-Copilot API")
    # adhtml.WriteToFile("Player.html", player_html)
    
    ## generates doc pages for All the classes.
    for cls in adhtml.ad.GetClasses():
        className = cls["itemClass"]
        filename = "{}.html".format(className)
        player_html = adhtml.ClassHTML(className)
        player_html = HTML.LeftRightPage(version+menu,player_html,"{} - UO-Copilot API".format(className))
        adhtml.WriteToFile(filename, player_html, debug=debug)

    ## generates wiki-style docs to ./doc/wiki/
    print("\nGenerating wiki-style docs...")
    wiki = WikiAutoDocHTML(output_path=None, api_path=api_path)
    wiki.MakeWikiDocumentation()
     
class HTML():
    
    
# content
    @staticmethod
    def ClassContainer(name, description, properties, contructors, methods, cssId=None, cssClass=None ):
        name_html = HTML.Div(name,cssClass="class-name")
        description_html = HTML.Div(description,cssClass="class-description")
        contructors_html = "" if len(contructors) == 0 else HTML.Div(contructors,cssClass="class-contructors")
        properties_html = "" if len(properties) == 0 else HTML.Div(properties,cssClass="class-properties")
        methods_html = "" if len(methods) == 0 else HTML.Div(methods,cssClass="class-methods")
        
        class_content = "\n".join([
            name_html,
            description_html,
            contructors_html,
            properties_html,
            methods_html
        ])
        
        class_html = HTML.Div(class_content, cssId=cssId, cssClass=cssClass)
        return class_html
        
    def ConstructorContainer():
        # TODO
        return ""

    @staticmethod
    def MethodContainer(permalink, className, methodName, description, signature, parameters, returns, cssId=None, cssClass=None ):
        permalink_html = HTML.DocPermalink(permalink)
        className_html = HTML.Span(className,cssClass="method-class-name")
        methodName_html = HTML.Span(methodName,cssClass="method-name")
        
        signature_content = "{}.{}({})".format(className_html,methodName_html, signature)
        signature_html = HTML.Div(signature_content,cssClass="redoc-method-signature")
        
        description_html = "" if len(description) == 0 else HTML.Div(description,cssClass="method-description")
        parameters_html = "" if len(parameters) == 0 else HTML.Div(parameters,cssClass="method-parameters")
        returns_html = "" if len(returns) == 0 else HTML.Div(returns,cssClass="method-returns")
        
        icon_open_html = HTML.IconExpand()
        icon_close_html = HTML.IconCollapse()
        
        signature_content = "{}.{}({})".format(className_html,methodName_html, signature)
        signature_closed_html = HTML.Div(icon_open_html+signature_content,cssClass="redoc-method-signature")
        signature_open_html = HTML.Div(icon_close_html+signature_content, cssClass="redoc-property-title")
        
        method_content_open = "\n".join([
            signature_open_html,
            description_html,
            parameters_html,
            returns_html
        ])
     
        
        box_closed = signature_closed_html
        box_open   = method_content_open
        
        method_content = HTML.CollapsableContainer(box_open, box_closed)
        
        method_html = HTML.Div(method_content, cssId=cssId, cssClass=cssClass)
        return permalink_html+method_html
        
    
    def PropertiesContainer(className, propName, type, description, cssId=None,  cssClass=None ):
        if cssClass is None: cssClass = 'redoc-property-container'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        
        className_html = HTML.Span(className,cssClass="redoc-class-name")
        propName_html = HTML.PropertyName(propName)
        
        name_html = "{}.{}".format(className_html,propName_html)
        type_html =  HTML.VariableType(type)
        
        icon_open_html = HTML.IconExpand()
        prop_title_closed_content = icon_open_html+name_html+type_html
        prop_title_closed_html = HTML.Div(prop_title_closed_content, cssClass="redoc-property-title")
        
        icon_close_html = HTML.IconCollapse()
        prop_title_open_content = icon_close_html+name_html+type_html
        prop_title_open_html = HTML.Div(prop_title_open_content, cssClass="redoc-property-title")
        
        
        desc_html =  '' if description is None or description == "" else HTML.Div(description, cssClass='redoc-class-property-desc')
        
        box_closed = prop_title_closed_html
        box_open   = prop_title_open_html+desc_html
        
        property_content = HTML.CollapsableContainer(box_open, box_closed)
        
        return HTML.Div(property_content, cssId=cssId, cssClass=cssClass)
        
    
# UI elements  
    def CollapsableContainer(open_html, closed_html, cssId=None,  cssClass=None ):
        if cssClass is None: cssClass = ''
        cssClass += ' redoc-collapsable-container closed-container'
        #cssClass = ' class="{}"'.format(cssClass)
        
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        
        
        box_closed = HTML.Div(closed_html, cssClass="redoc-collapsable-container-closed")
        box_open = HTML.Div(open_html, cssClass="redoc-collapsable-container-open")
        box_html = HTML.Div(box_closed+box_open, cssClass=cssClass)
        return box_html
        
    
# pages
    
    
    @staticmethod
    def BasePage(body, title=""):
        css_html_fa = HTML.CSS("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css")
        css_html = HTML.CSS("./main.css")
        js_html = HTML.JS("./main.js")
        header_html = css_html_fa +"\n"+ css_html +"\n"+ js_html
        body_html = HTML.Div(body,cssClass="redoc-page-container")
        
        return HTML.EmptyPage(body_html, title, header_html)
        
        
    @staticmethod
    def EmptyPage(body,title="",header=""):
        title_html = "" if len(title)==0 else "\n<title>{}</title>\n".format(title)
        header_html = "" if (len(header)==0 and len(title_html)==0) else "\n<head>{}\n{}\n</head>\n".format(title_html,header)
        body_html = "" if len(body)==0 else "\n<body>\n{}\n</body>\n".format(body)
        return '<!Doctype html>{}{}</html>'.format(header_html, body_html)
    
    @staticmethod
    def LeftRightPage(left_content, right_content, title=""):
        left_html = HTML.Div(left_content,cssClass="redoc-page-left")
        right_html = HTML.Div(right_content,cssClass="redoc-page-right")
        body = left_html + right_html
        
        return HTML.BasePage(body, title)

        
# sub-elements
    
 
    @staticmethod
    def ParamForSignature(name, paramType=None, cssId=None,  cssClass=None ):
        if cssClass is None: cssClass = 'redoc-method-params-sign'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = ' class="{}"'.format(cssClass)
        name_html =  HTML.VariableName(name)
        type_html = '' if paramType is None or paramType == "" else HTML.VariableType(paramType)
        return '<span{}{}>{}{}</span>'.format(cssId, cssClass, name_html, type_html )
    
        
    @staticmethod
    def ParamDescription(name, type_html, description, cssId=None,  cssClass=None ):
        if cssClass is None: cssClass = 'redoc-method-params'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = ' class="{}"'.format(cssClass)
        name_html =  HTML.VariableName(name)
        desc_html =  '' if description is None or description == "" else HTML.Div(description, cssClass='redoc-method-params-desc')
        return '<span{}{}>{}{}{}</span>'.format(cssId, cssClass, name_html, type_html, desc_html)
        
    @staticmethod
    def ParamForDescription(name, type, description, cssId=None,  cssClass=None ):
        if cssClass is None: cssClass = 'redoc-method-params'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = ' class="{}"'.format(cssClass)
        name_html =  HTML.VariableName(name)
        type_html =  HTML.VariableType(type)
        desc_html =  '' if description is None or description == "" else HTML.Div(description, cssClass='redoc-method-params-desc')
        return '<span{}{}>{}{}{}</span>'.format(cssId, cssClass, name_html, type_html, desc_html)
       
     
    
    @staticmethod
    def VariableType(content, cssId=None,  cssClass=None):
        if cssClass is None: cssClass = 'redoc-variable-type'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = ' class="{}"'.format(cssClass)
        return '<span{}{}>{}</span>'.format(cssId, cssClass, content)
        
    @staticmethod
    def VariableName(content, cssId=None,  cssClass=None):
        if cssClass is None: cssClass = 'redoc-variable-name'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = ' class="{}"'.format(cssClass)
        return '<span{}{}>{}</span>'.format(cssId, cssClass, content)
        
    @staticmethod
    def PropertyName(content, cssId=None,  cssClass=None):
        if cssClass is None: cssClass = 'redoc-property-name'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = ' class="{}"'.format(cssClass)
        return '<span{}{}>{}</span>'.format(cssId, cssClass, content)
        
    @staticmethod
    def MethodReturn(type_html, description, cssId=None,  cssClass=None):
        if cssClass is None: cssClass = 'redoc-method-return'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)

        desc_html =  '<br/>' if description is None or description == "" else HTML.Div(description, cssClass='redoc-method-return-desc')
        
        return_label = HTML.Div("Return",cssClass="redoc-method-return-box-title") 
        return_html =  return_label+HTML.Div(type_html + desc_html, cssClass="redoc-method-return-box")
        
        return HTML.Div(return_html, cssId, cssClass)
    
    @staticmethod
    def DocVersion(version, cssId=None,  cssClass=None):
        if cssClass is None: cssClass = 'redoc-doc-version'
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = ' class="{}"'.format(cssClass)
        return '<div{}{}><a href="./index.html">UO-Copilot API v{}</a></div>'.format(cssId, cssClass, version)
        
    @staticmethod
    def DocPermalink(url, content=None, cssClass=None):
        content = HTML.IconLink() if content is None else content
        link = ' href="#{}"'.format(url)
        cssId = ' id="{}"'.format(url)
        if cssClass is None: cssClass = 'redoc-permalink' 
        cssClass =  '' if cssClass == '' else ' class="{}"'.format(cssClass)
        return '<a{}{}{}>{}</a>'.format(cssId, cssClass, link, content)
        
    @staticmethod
    def IconLink():
        return '<i class="redoc-icon-link fas fa-link "></i>'
        
    @staticmethod    
    def IconExpand():
        return '<i class="redoc-icon-expand fas fa-angle-down "></i>'
        
    @staticmethod
    def IconCollapse():
        return '<i class="redoc-icon-collapse fas fa-angle-up"></i>'     
        
# base html elements
    @staticmethod
    def CSS(url,inline=False):
        css_html = '<style>{}</style>' if inline else '<link rel="stylesheet" type="text/css" href="{}">'
        css_html = css_html.format(url)
        return css_html
        
        
    @staticmethod
    def JS(url,inline=False):
        js_html = '<script>\n{}\n</script>' if inline else '<script src="{}"></script>'
        js_html = js_html.format(url)
        return js_html
    
    @staticmethod
    def Link(content, url=None, cssId=None,  cssClass=None ):
        url = '' if url is None else ' href="{}"'.format(url)
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = '' if cssClass is None else ' class="{}"'.format(cssClass)
        return '<a{}{}{}>{}</a>'.format(cssId, cssClass, url, content)
    
    @staticmethod
    def Div(content, cssId=None,  cssClass=None ):
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = '' if cssClass is None else ' class="{}"'.format(cssClass)
        return '<div{}{}>{}</div>'.format(cssId, cssClass, content)
    
    @staticmethod
    def Span(content, cssId=None,  cssClass=None ):
        cssId = '' if cssId is None else ' id="{}"'.format(cssId)
        cssClass = '' if cssClass is None else ' class="{}"'.format(cssClass)
        return '<span{}{}>{}</span>'.format(cssId, cssClass, content)
        
    
class AutoDocHTML:
    def __init__(self, output_path=None, api_path=None):
        self.doc_path = "./doc/api/" if output_path is None else output_path
        self.ad = AutoDoc(api_path)
        
    def KeyToSlug(self, xmlkey, overload=True, shortname=True):
        if overload: xmlkey = re.sub("\(.*\)","",xmlkey)
        if shortname: xmlkey = xmlkey.replace(":Assistant.",":") #TODO: remove all settings/basename
        return re.sub("[^a-zA-Z]","-",xmlkey)
        
    def PermalinkHTML(self,xmlkey):
        anchor_slug = self.KeyToSlug(xmlkey)
        return HTML.DocPermalink(anchor_slug, cssClass='redoc-permalink' )
        
    def DocVersionHTML(self):
        version = self.ad.GetVersion()
        return HTML.DocVersion(version)
    
    def MainMenuHTML(self, menuId='redoc-main-menu', itemClass='redoc-main-menu-entry'):
        classList = self.ad.GetClasses()
        links = []
        for cls in classList:
            name = cls["itemClass"]
            url = "./{}.html".format(name)
            html = HTML.Link(name, url, cssClass=itemClass )
            links.append( html )
        #
        links_html = "\n".join(links)
        main_menu = HTML.Div(links_html, cssId=menuId)
        return main_menu
        
    def ClassHTML(self, className, classId='redoc-class-', itemClass='redoc-class'):
        classList = self.ad.GetClasses(className)
        if len(classList)==0: return "Class not found: {}".format(className);
        doc_class = classList[0]
        
        description = doc_class["itemDescription"]
        properties_html = self.ProperiesHTML(className)
        constructors_html = self.ConstructorsHTML(className)
        methods_html = self.MethodsHTML(className)
        
        class_html = HTML.ClassContainer(className, description, properties_html, constructors_html, methods_html, cssId=classId, cssClass=itemClass)
        return class_html
        
    def ProperiesHTML(self, className):
        propertyList = self.ad.GetProperties(className)
        if (len(propertyList) == 0): return ''
        prop_html_list = []
        for property in propertyList:
            link = self.PermalinkHTML(property["xmlKey"])
            prop_html = HTML.PropertiesContainer(className,property['itemName'], property['propertyType'], property['itemDescription'])
            prop_html = HTML.Div(link+prop_html, cssClass="redoc-class-property-entry")
            prop_html_list.append(prop_html)
        
        props_html = "\n".join(prop_html_list)
        props_html = HTML.Div(props_html, cssClass="redoc-property-box")
        props_html = HTML.Div("Properties",cssClass="redoc-property-box-title") + props_html
        return props_html
        
    def ConstructorsHTML(self, className):
        constructorList = self.ad.GetConstructors(className)
        if (len(constructorList) == 0): return "TODO: "+className+" Constructors"
        # TODO
        return "TODO: "+className+" Constructors" 
        
    def MethodsHTML(self, className):
        methodList = self.ad.GetMethods(className)
        methodNames = set( [method['itemName'] for method in methodList] )
        methodNames = list(sorted(methodNames));
        methods_html_list = []
        for methodName in methodNames:
            methods_html_list.append( self.MethodOverloadHTML(className, methodName) )
        #    
        methods_html = "\n".join(methods_html_list)
        methods_html = HTML.Div(methods_html, cssClass="redoc-method-box")
        methods_html = HTML.Div("Methods",cssClass="redoc-method-box-title") + methods_html
        return methods_html
        
        
    def MethodOverloadHTML(self, className, methodName):
        methodList = self.ad.GetMethods(className, methodName)
        
        # setup for aggregation: descriptions
        lastMethod = methodList[-1]
        firstMethod = methodList.pop(0)
        firstMethod["itemDescription"] = [ firstMethod["itemDescription"] ]
        firstMethod["returnDesc"] = [ firstMethod["returnDesc"] ]
        firstMethod["returnType"] = [ firstMethod["returnType"] ]
        
        # setup for aggregation: default params instead of overloading ( python way )
        min_p = len(lastMethod)
        max_p = len(firstMethod)
        for num_p in range(min_p,max_p): #TODO: check indexes
            param = firstMethod["paramList"][num_p]
            if not param['itemHasDefault']:
                param['itemHasDefault'] = True
                param['itemDefaultValue'] = "null"
        firstMethod["paramList"] = [[param] for param in firstMethod["paramList"] ]
        
        # accumulate: descriptions and params
        for method in methodList:
            firstMethod["itemDescription"].append(method["itemDescription"])
            firstMethod["returnDesc"].append(method["returnDesc"])
            firstMethod["returnType"].append(method["returnType"])
            
            for p_num, param in enumerate(method["paramList"]):
                firstMethod["paramList"][p_num].append(param)
          
          
        # aggregate descriptions and returns      
        description = "\n".join([desc.strip() for desc in firstMethod["itemDescription"]]).strip()
        
        # deduplicate returns ( likely the same ) 
        firstMethod["returnType"] = list(set(firstMethod["returnType"]))
        return_desc = "\n".join([desc.strip() for desc in firstMethod["returnDesc"]]).strip()
        return_type_list = [ HTML.VariableType(ret_type) for ret_type in firstMethod["returnType"]]
        return_type = "\n".join(return_type_list)
        return_html = HTML.MethodReturn(return_type, return_desc )
        
        
        # aggregate params
        param_name_list = [] 
        param_desc_html_list = []
        for param_list in firstMethod["paramList"]:
            param_name = param_list[0]["itemName"] #names from first method 
            param_type_list = [param["itemType"] for param in param_list]
            param_desc_list = [param["itemDescription"] for param in param_list]
        
            param_type_list = list(filter(lambda t: t is not None and t != "", set(param_type_list)))
            param_desc_list = list(filter(lambda t: t is not None and t != "", set(param_desc_list)))
            
            param_type_html = "\n".join([HTML.VariableType(param_type) for param_type in param_type_list])
            param_desc_html = "\n".join(param_desc_list)
            
            param_desc_html_list.append(HTML.ParamDescription(param_name, param_type_html, param_desc_html) )
            param_name_list.append(param_name)
        #
        signature_list = [HTML.ParamForSignature(param_name) for param_name in param_name_list]
        signature_html = "{}".format( ", ".join(signature_list) )
        
        param_html = "\n".join(param_desc_html_list).strip()
        if param_html != "":
            param_desc_label = HTML.Div("Parameters",cssClass="redoc-method-params-box-title") 
            param_html = param_desc_label+HTML.Div(param_html,cssClass="redoc-method-params-box") 
            
            
        cssClass = 'redoc-method-container' 
        link = self.KeyToSlug(firstMethod["xmlKey"]) 
           
            
        className=firstMethod["itemClass"]
        methodName=firstMethod["itemName"]
        method_html = HTML.MethodContainer(link,className, methodName, description, signature_html, param_html, return_html, cssClass=cssClass )
        method_html = HTML.Div(method_html, cssClass="redoc-class-method-entry")
        
        return method_html
        
        
        
    # old
    def MethodDetailHTML(self, className, methodName):
        methodList = self.ad.GetMethods(className, methodName)
        methods_html_list = []
        for method in methodList:
            cssClass = 'redoc-method-container' 
            link = self.KeyToSlug(method["xmlKey"])
            description = method["itemDescription"]
            paramList = method["paramList"]
            
            
            methodReturn = HTML.MethodReturn(method["returnType"], method["returnDesc"] )
            return_label = HTML.Div("Return",cssClass="redoc-method-return-box-title") 
            return_html = return_label+methodReturn
            return_html = HTML.Div(return_html,cssClass="redoc-method-return-box") 
            
            
            paramSignature = [HTML.ParamForSignature(p['itemName'], p['itemType']) for p in paramList]
            paramDescription = [HTML.ParamForDescription(p['itemName'], p['itemType'], p['itemDescription']) for p in paramList]
            
            
            signature_html = "{}".format( ", ".join(paramSignature) )
            paramsDesc = "\n".join(paramDescription).strip()
            if paramsDesc != "":
                paramsDesc = HTML.Div("Parameters",cssClass="redoc-method-params-box-title") + paramsDesc
            #
            
            
            #
            
            
            
            method_html = HTML.MethodContainer(link,className, methodName, description, signature_html, paramsDesc, return_html, cssClass=cssClass )
            method_html = HTML.Div(method_html, cssClass="redoc-class-method-entry")
            methods_html_list.append(method_html)
            
        #    
        methods_html = "\n".join(methods_html_list)
        
        return methods_html
        
    def WriteToFile(self, path, content, debug=False):
        fullpath = self.doc_path + path
        print(fullpath)
        dirpath  = os.path.dirname(fullpath)
        if not os.path.exists(dirpath):
            print("Make Dir: "+dirpath)
            os.makedirs(dirpath)
        #
        file = open(fullpath,'w+')
        file.write(content)
        file.close()
        
     
        
    
    

class WikiHTML:
    """Wiki-style HTML theme (DokuWiki-inspired, dark theme)"""

    @staticmethod
    def Page(sidebar, content, title="", right_index=None):
        title_html = "<title>{}</title>".format(title) if title else ""
        css = '<link rel="stylesheet" type="text/css" href="./wiki.css">'
        js = '<script src="./wiki.js"></script>'
        header = "<head>{}{}{}</head>".format(title_html, css, js)

        sidebar_html = '<nav class="wiki-sidebar">{}</nav>'.format(sidebar)
        content_html = '<main class="wiki-content">{}</main>'.format(content)
        right_html = ''
        if right_index:
            right_html = '<aside class="wiki-index">{}</aside>'.format(right_index)
        body = '<body><div class="wiki-layout">{}{}{}</div></body>'.format(
            sidebar_html, content_html, right_html
        )

        return "<!DOCTYPE html><html>{}{}</html>".format(header, body)

    @staticmethod
    def Sidebar(version, class_links):
        version_html = '<div class="wiki-version"><a href="./index.html">UO-Copilot API v{}</a></div>'.format(
            version
        )
        links_html = "\n".join(class_links)
        nav = '<div class="wiki-nav">{}</div>'.format(links_html)
        return version_html + nav

    @staticmethod
    def SidebarLink(name, url, active=False):
        css_class = ' class="wiki-nav-link active"' if active else ' class="wiki-nav-link"'
        return '<a{} href="{}">{}</a>'.format(css_class, url, name)

    @staticmethod
    def TOC(entries):
        if not entries:
            return ""
        items = []
        for anchor, label in entries:
            items.append('<li><a href="#{}">{}</a></li>'.format(anchor, label))
        return '<div class="wiki-toc"><h3>Table of Contents</h3><ul>{}</ul></div>'.format(
            "\n".join(items)
        )

    @staticmethod
    def RightIndex(entries):
        if not entries:
            return ""
        items = []
        for anchor, label in entries:
            items.append('<li><a href="#{}">{}</a></li>'.format(anchor, label))
        return '<div class="wiki-index-header">Index</div><ul class="wiki-index-list">{}</ul>'.format(
            "\n".join(items)
        )

    @staticmethod
    def ClassHeader(class_name, description=""):
        desc_html = (
            '<p class="wiki-class-desc">{}</p>'.format(description)
            if description
            else ""
        )
        return '<h1 class="wiki-class-name">{}</h1>{}'.format(class_name, desc_html)

    @staticmethod
    def SectionHeader(title, anchor):
        return '<h2 id="{}" class="wiki-section-header">{}</h2>'.format(anchor, title)

    @staticmethod
    def PropertyEntry(class_name, prop_name, prop_type, description, anchor):
        syntax = "{}.{}".format(class_name, prop_name)
        desc_html = (
            '<p class="wiki-desc">{}</p>'.format(description)
            if description
            else ""
        )
        return '<div class="wiki-entry" id="{}">\n<h3 class="wiki-entry-name">{}</h3>\n<div class="wiki-syntax"><span class="wiki-label">Syntax:</span> <code>{}</code></div>\n<div class="wiki-returns"><span class="wiki-label">Returns:</span> <code>{}</code></div>\n{}\n</div>'.format(
            anchor, prop_name, syntax, prop_type, desc_html
        )

    @staticmethod
    def MethodEntry(class_name, method_name, signature, description, params_html, returns_html, anchor):
        syntax = "{}.{}({})".format(class_name, method_name, signature)
        desc_html = (
            '<p class="wiki-desc">{}</p>'.format(description)
            if description
            else ""
        )
        params_section = (
            '<div class="wiki-params">{}</div>'.format(params_html)
            if params_html
            else ""
        )
        returns_section = (
            '<div class="wiki-returns-section"><span class="wiki-label">Returns:</span> {}</div>'.format(
                returns_html
            )
            if returns_html
            else ""
        )
        return '<div class="wiki-entry" id="{}">\n<h3 class="wiki-entry-name">{}</h3>\n<div class="wiki-syntax"><span class="wiki-label">Syntax:</span> <code>{}</code></div>\n{}\n{}\n{}\n</div>'.format(
            anchor, method_name, syntax, desc_html, params_section, returns_section
        )

    @staticmethod
    def ParamItem(name, param_type, description):
        type_html = (
            ' <span class="wiki-param-type">({})</span>'.format(param_type)
            if param_type
            else ""
        )
        desc_html = ": {}".format(description) if description else ""
        return '<li><code class="wiki-param-name">{}</code>{}{}</li>'.format(
            name, type_html, desc_html
        )

    @staticmethod
    def ParamList(params_html):
        return '<div class="wiki-param-list"><span class="wiki-label">Parameters:</span><ul>{}</ul></div>'.format(
            params_html
        )

    @staticmethod
    def ReturnType(type_html):
        return '<div class="wiki-returns-section"><span class="wiki-label">Returns:</span> {}</div>'.format(
            type_html
        )


class WikiAutoDocHTML:
    """Generates wiki-style documentation using WikiHTML and AutoDoc"""

    def __init__(self, output_path=None, api_path=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_wiki = os.path.join(script_dir, "wiki") + os.sep
        self.doc_path = default_wiki if output_path is None else output_path
        self.ad = AutoDoc(api_path)

    def KeyToSlug(self, xmlkey):
        xmlkey = re.sub(r"\(.*\)", "", xmlkey)
        xmlkey = xmlkey.replace(":Assistant.", ":")
        return re.sub(r"[^a-zA-Z]", "-", xmlkey)

    def SidebarHTML(self, active_class=None):
        version = self.ad.GetVersion()
        class_list = self.ad.GetClasses()
        links = []
        for cls in class_list:
            name = cls["itemClass"]
            url = "./{}.html".format(name)
            active = name == active_class
            links.append(WikiHTML.SidebarLink(name, url, active))
        return WikiHTML.Sidebar(version, links)

    def ClassPageHTML(self, class_name):
        class_list = self.ad.GetClasses(class_name)
        if not class_list:
            return "Class not found: {}".format(class_name)

        doc_class = class_list[0]
        description = doc_class.get("itemDescription", "")

        parts = []
        parts.append(WikiHTML.ClassHeader(class_name, description))

        toc_entries = []
        properties = self.ad.GetProperties(class_name)
        methods = self.ad.GetMethods(class_name)

        if properties:
            toc_entries.append(("properties", "Properties"))
        if methods:
            toc_entries.append(("methods", "Methods"))

        parts.append(WikiHTML.TOC(toc_entries))

        if properties:
            parts.append(WikiHTML.SectionHeader("Properties", "properties"))
            for prop in properties:
                anchor = self.KeyToSlug(prop["xmlKey"])
                parts.append(
                    WikiHTML.PropertyEntry(
                        class_name,
                        prop["itemName"],
                        prop["propertyType"],
                        prop.get("itemDescription", ""),
                        anchor,
                    )
                )

        if methods:
            parts.append(WikiHTML.SectionHeader("Methods", "methods"))
            method_names = sorted(set(m["itemName"] for m in methods))
            for method_name in method_names:
                method_list = self.ad.GetMethods(class_name, method_name)
                parts.append(self.MethodWikiHTML(class_name, method_name, method_list))

        return "\n".join(parts)

    def RightIndexHTML(self, class_name):
        properties = self.ad.GetProperties(class_name)
        methods = self.ad.GetMethods(class_name)

        entries = []
        seen = set()
        for prop in properties:
            name = prop["itemName"]
            if name not in seen:
                seen.add(name)
                anchor = self.KeyToSlug(prop["xmlKey"])
                entries.append((anchor, name))
        for method in methods:
            name = method["itemName"]
            if name not in seen:
                seen.add(name)
                anchor = self.KeyToSlug(method["xmlKey"])
                entries.append((anchor, name))

        entries.sort(key=lambda e: e[1].lower())
        return WikiHTML.RightIndex(entries)

    def MethodWikiHTML(self, class_name, method_name, method_list):
        first = method_list[0]
        anchor = self.KeyToSlug(first["xmlKey"])

        descriptions = [m.get("itemDescription", "") for m in method_list]
        description = "\n".join(d for d in descriptions if d).strip()

        return_types = list(set(m["returnType"] for m in method_list))
        returns_html = ", ".join(
            '<code>{}</code>'.format(rt) for rt in return_types
        )

        param_names = []
        param_items_html = []
        if first.get("paramList"):
            for param in first["paramList"]:
                pname = param["itemName"]
                ptype = param.get("itemType", "")
                pdesc = param.get("itemDescription", "")
                param_names.append(pname)
                param_items_html.append(WikiHTML.ParamItem(pname, ptype, pdesc))

        signature = ", ".join(param_names)
        params_html = (
            WikiHTML.ParamList("\n".join(param_items_html))
            if param_items_html
            else ""
        )

        return WikiHTML.MethodEntry(
            class_name, method_name, signature, description, params_html, returns_html, anchor
        )

    def IndexPageHTML(self):
        version = self.ad.GetVersion()
        class_list = self.ad.GetClasses()

        parts = []
        parts.append('<h1>UO-Copilot API Documentation</h1>')
        parts.append('<p class="wiki-version-text">Version: {}</p>'.format(version))
        parts.append('<h2>Classes</h2>')
        parts.append('<ul class="wiki-class-list">')
        for cls in class_list:
            name = cls["itemClass"]
            parts.append('<li><a href="./{}.html">{}</a></li>'.format(name, name))
        parts.append('</ul>')

        return "\n".join(parts)

    def WriteToFile(self, path, content):
        fullpath = self.doc_path + path
        print("Wiki: " + fullpath)
        dirpath = os.path.dirname(fullpath)
        if not os.path.exists(dirpath):
            print("Make Dir: " + dirpath)
            os.makedirs(dirpath)
        with open(fullpath, "w+") as f:
            f.write(content)

    def MakeWikiDocumentation(self):
        sidebar = self.SidebarHTML()

        index_content = self.IndexPageHTML()
        index_html = WikiHTML.Page(sidebar, index_content, "UO-Copilot API Documentation")
        self.WriteToFile("index.html", index_html)

        for cls in self.ad.GetClasses():
            class_name = cls["itemClass"]
            sidebar = self.SidebarHTML(active_class=class_name)
            content = self.ClassPageHTML(class_name)
            index = self.RightIndexHTML(class_name)
            page_html = WikiHTML.Page(sidebar, content, "{} - UO-Copilot API".format(class_name), right_index=index)
            self.WriteToFile("{}.html".format(class_name), page_html)


class AutoDoc:
    # Load data from AutoComplete.json and provides several convenience methods to query the content.
    
    def __init__(self, api_path=None):
        self.api_data = None
        self.api_path = "./Config/AutoComplete.json" if api_path is None else api_path
        
    def GetSettings(self):
        api = self.GetPythonAPI()
        docs = api["settings"]
        return docs
        
    def GetVersion(self):
        settings = self.GetSettings()
        return settings["version"]
        
    def GetClasses(self, filterClass=None):
        api = self.GetPythonAPI()
        docs = api["classes"]
        docs = list( sorted(docs, key=lambda doc: doc["itemClass"]) )
        if filterClass is not None:
            docs = list(filter(lambda doc: doc["itemClass"] == filterClass,docs))
        return docs
    
    def GetProperties(self, filterClass=None):
        api = self.GetPythonAPI()
        docs = api["properties"]
        if filterClass is not None:
            docs = list(filter(lambda doc: doc["itemClass"] == filterClass,docs))
        #
        docs = list( sorted(docs, key=lambda doc: (doc["itemClass"], doc["itemName"]) ) )
        return docs
        
    def GetConstructors(self, filterClass=None):
        api = self.GetPythonAPI()
        docs = api["constructors"]
        if filterClass is not None:
            docs = list(filter(lambda doc: doc["itemClass"] == filterClass, docs))
        #
        docs = list( sorted(docs, key=lambda doc: (doc["itemClass"], doc["itemName"]) ) )
        return docs
        
    def GetMethods(self, filterClass=None, filterName=None):
        api = self.GetPythonAPI()
        docs = api["methods"]
        
        if filterClass is not None:
            docs = list(filter(lambda doc: doc["itemClass"] == filterClass,docs))
        #
        if filterName is not None:
            docs =  list(filter(lambda doc: doc["itemName"] == filterName,docs))
        #
        docs = list( sorted(docs, key=lambda doc: (doc["itemClass"], doc["itemName"], -len(doc["paramList"]) ) ) )
        return docs
    
    
    def GetPythonAPI(self):
        if self.api_data is not None: return self.api_data
        
        print("Loading from Path:\n{}".format(self.api_path))
        
        api_file = open(self.api_path,'r+')
        api_json = api_file.read()
        api_file.close()
        print("File Size: {}".format(len(api_json)) )
        self.api_data = json.loads(api_json)
        
        return self.api_data
        


"""
By placing the call to the main function at the bottom of the file, there is the freedom to rearrage the code freely in the file.

NOTE: *if __name__ == '__main__':* make sure that the main() is called only when the script is run directly.
      In this way is possible to safely use this file also via "include autodoc" without worrying that the main() would be executed.
"""
if __name__ == '__main__':
    main() 
