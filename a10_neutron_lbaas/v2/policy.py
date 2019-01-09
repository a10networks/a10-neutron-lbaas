# Copyright 2019, Omkar Telee (omkartelee01), A10 Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import re
TYPE_DICT = {
          "HOST_NAME" : "HTTP::host",
          "PATH" : "HTTP::uri",
          "FILE_TYPE" : "HTTP::uri endswith",
          "HEADER" : "HTTP::header",
          "COOKIE" : "HTTP::cookie"
        }


COMPARE_TYPE_DICT = {
       "REGEX" : "matches_regex",
       "STARTS_WITH" : "starts_with",
       "ENDS_WITH" : "ends_with",
       "CONTAINS" : "contains",
       "EQUAL_TO" : "equals"
    }

class PolicyUtil():
    def __init__(self):
        self.base = """ when HTTP_REQUEST {{ \n
        if {{ {0} }} {{ \n
        {1}  \n
        }} \n
        }} """
    
    def createPolicy(self,l7policy):
        actionString = ""
        if l7policy.action == "REDIRECT_TO_POOL" :
            actionString = "pool " + l7policy.redirect_pool.id 

        elif l7policy.action == "REDIRECT_TO_URL":
            actionString = "HTTP::redirect "+ l7policy.redirect_url

        else:
            actionString = "HTTP::close"
        # placeholder till rules
        ruleString = ""
        if len(l7policy.rules) <= 0 :
            ruleString = "( true )"
        else:
            ruleArray = []
            for rule in l7policy.rules:
                temp = self.ruleParser(rule)
                ruleArray.append(temp)
            ruleString = " and ".join(ruleArray)
        return self.base.format(ruleString,actionString)
        
    def ruleParser(self,l7rule):
        ruleString = "("
        # type
        typeString = TYPE_DICT[l7rule.type]
        if l7rule.key:
            typeString = typeString + " name " + l7rule.key
        typeString = "[" + typeString + "]"  
        ruleString += typeString
        
        #compare type
        compare_type_string =  COMPARE_TYPE_DICT[l7rule.compare_type]
        ruleString += " " + compare_type_string

        #value 
        value_string = l7rule.value
        ruleString += " \"" + value_string + "\""
       
        ruleString += ")"
        return ruleString

    def convertRules(self,l7Rule, policyTCL):
        m = re.search('({.*})', policyTCL)
        ruleString = m.group(0)
        ruleString = ruleString.replace('{' , "").replace('}' , "")
        rules = [x.strip() for x in ruleString.split('and')]

    def ruleObjectCreator(self, ruleSring):
        # ([HTTP::header name namer] equals value)
        ruleString = ruleString.replace('(' , "").replace(')' , "").strip()
        if 'name' in ruleString:
            rules = [x.strip() for x in ruleString.split(" ")]
            r = Rule(rules[0]+"]", rules[3], rules[2], None, rules[2])
        else:
            rules = [x.strip() for x in ruleString.split(" ")]
            r = Rule(rules[0], rules[1], None, rules[2])

        return r  
